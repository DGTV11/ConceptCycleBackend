import json
from datetime import datetime
from uuid import uuid4

import yaml
from pocketflow import *

import db
from debug import printd
from llm import call_llm

# class StartQuizIn(BaseModel):
#     note_ids: list[str]
#     concept_limit: int
#     question_limit: int
#     mode: str
#
#     @model_validator(mode="after")
#     def check_values(self):
#         if self.question_limit < self.concept_limit:
#             raise ValueError(
#                 "question_limit must be greater than or equal to concept_limit"
#             )
#         return self


# *QUIZ GENERATOR
class GenerateQuizName(Node):
    def prep(self, shared):
        return self.params["concept_names"]

    def exec(self, concept_names):
        prompt = f"""
Given names of concepts tested in a quiz: {concept_names}
Analyse them and write a succinct name for the quiz that aptly describes the tested concepts. Ensure that the length of the quiz name does not exceed 7 words.
Output in yaml (including starting "```yaml" and closing "```" at start and end of your response respectively):
```yaml
analysis: detailed step-by-step analysis of the concept names (ONE string)
quiz_name: name of quiz (ONE string)
```
        """
        resp = call_llm(prompt)
        yaml_str = resp.split("```yaml")[1].split("```")[0].strip()
        result = yaml.safe_load(yaml_str)

        assert isinstance(result, dict)
        assert "quiz_name" in result
        assert isinstance(result["quiz_name"], str)

        result["quiz_name"] = result["quiz_name"].strip()

        return result

    def post(self, shared, prep_res, exec_res):
        shared["quiz_name"] = exec_res["quiz_name"]


class GenerateQuestionsFromConcept(Node):
    def prep(self, shared):
        name = self.params["name"]
        content = self.params["content"]
        count = self.params["count"]

        return name, content, count

    def exec(self, inputs):
        name, content, count = inputs
        prompt = f"""
Given concept "{name}" with content:
```
{content}
```
Analyse the content and make {count} question-and-answer pairs. The questions need to test the answerer on the concept's content so that we can accurately acertain whether he/she understands the concept. The corresponding answers need to accurately and fully answer the question based on the given concept's content with all relevant information (e.g. alternative viewpoints, grading instructions, etc.) without compromising the intended solutions' accuracy for future graders.
Output in yaml (including starting "```yaml" and closing "```" at start and end of your response respectively):
```yaml
analysis: detailed step-by-step analysis of chunk (ONE string)
questions_and_answers: (list of objects)
    - question: question (ONE string)
      answer: answer and relevant information (ONE string)
```
        """
        resp = call_llm(prompt)
        yaml_str = resp.split("```yaml")[1].split("```")[0].strip()
        result = yaml.safe_load(yaml_str)

        assert isinstance(result, dict)
        assert "analysis" in result
        assert "questions_and_answers" in result
        assert isinstance(result["questions_and_answers"], list)
        assert len(result["questions_and_answers"]) == count
        assert all(
            (
                isinstance(x, dict)
                and "question" in x
                and isinstance(x["question"], str)
                and "answer" in x
                and isinstance(x["answer"], str)
            )
            for x in result["questions_and_answers"]
        )

        result["questions_and_answers"] = [
            {y: z.strip() for y, z in x.items()}
            for x in result["questions_and_answers"]
        ]

        return result

    def post(self, shared, prep_res, exec_res):
        shared["questions_and_answers"] = exec_res["questions_and_answers"]


generate_quiz_name_node = GenerateQuizName(max_retries=60, wait=5)

generate_questions_from_concept_node = GenerateQuestionsFromConcept(
    max_retries=60, wait=5
)

# *QUIZ GRADER


def create_quiz_from_note(connection, note_ids, concept_limit, question_limit, mode):
    concepts = {}

    printd("Getting concepts from notes")
    for note_id in note_ids:
        printd(f"Getting concepts from note {note_id}")
        raw_concepts = db.execute_read_query(
            connection,
            "SELECT id, name, content FROM concepts WHERE note_id = ?",
            (note_id,),
        )

        for id, name, content in raw_concepts:
            card_id, state, step, stability, difficulty, due, last_review = (
                db.execute_read_query(
                    connection,
                    """
                SELECT id, state, step, stability, difficulty, due, last_review
                FROM cards
                WHERE concept_id = ?
                """,
                    (id,),
                )[0]
            )

            srs_info = {
                "id": card_id,
                "step": step,
                "stability": stability,
                "difficulty": difficulty,
                "due": due,
                "last_review": last_review,
            }

            match mode:
                case "due_only":
                    due_datetime = datetime.fromisoformat(due)
                    if last_review is not None and due_datetime <= datetime.now():
                        concepts[id] = {
                            "name": name,
                            "content": content,
                            "srs_info": srs_info,
                        }
                case "learning_only":
                    if last_review is not None:
                        concepts[id] = {
                            "name": name,
                            "content": content,
                            "srs_info": srs_info,
                        }
                case "new_only":
                    if last_review is None:
                        concepts[id] = {
                            "name": name,
                            "content": content,
                            "srs_info": srs_info,
                        }
                case "mixed":
                    concepts[id] = {
                        "name": name,
                        "content": content,
                        "srs_info": srs_info,
                    }
                case _:
                    raise ValueError("Invalid mode")

    printd("Sorting concepts")
    concepts = sorted(
        concepts.items(),
        key=lambda concept: (
            0
            if not concept[1]["srs_info"]["stability"]
            else concept[1]["srs_info"]["stability"]
        ),  # *Prioritises low stability for review
    )[
        :concept_limit
    ]  # * Trim sorted concept list (or queue) to concept_limit

    concepts_dict = dict(concepts)

    question_cids = {}

    printd("Processing sorted concepts")
    no_questions = 0
    while no_questions < question_limit:
        concept_idx = no_questions % concept_limit
        if question_cids.get(concepts[concept_idx][0], None):
            question_cids[concepts[concept_idx][0]] += 1
        else:
            question_cids[concepts[concept_idx][0]] = 1
        no_questions += 1

    printd("Generating quiz name")
    concept_names = [c["name"] for c in concepts_dict.values()]

    shared = {}
    generate_quiz_name_node.set_params({"concept_names": concept_names})
    generate_quiz_name_node.run(shared)
    quiz_name = shared["quiz_name"]

    printd("Generating questions")
    cids_questions_and_answers = []
    for question_cid, question_count in question_cids.items():
        concept = concepts_dict[question_cid]
        concept_name = concept["name"]
        concept_content = concept["content"]

        shared = {}
        generate_questions_from_concept_node.set_params(
            {"name": concept_name, "content": concept_content, "count": question_count}
        )
        generate_questions_from_concept_node.run(shared)

        # result["questions_and_answers"] = [
        #     {y: z.strip() for y, z in x.items()}
        #     for x in result["questions_and_answers"]
        # ]

        qa_tuple_list = []

        for qa_dict in shared["questions_and_answers"]:
            qa_tuple_list.append((qa_dict["question"], qa_dict["answer"]))

        cids_questions_and_answers.extend(
            zip(
                [question_cid] * len(shared["questions_and_answers"]),
                *zip(*qa_tuple_list),
            )
        )

    cids, questions, answers = zip(*cids_questions_and_answers)

    printd("Updating db")
    quiz_id = str(uuid4())

    db.execute_write_query(
        connection,
        """
        INSERT INTO quizzes (id, name, status, questions, answers, concept_ids)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            quiz_id,
            quiz_name,
            "active",
            json.dumps(questions),
            json.dumps(answers),
            json.dumps(cids),
        ),
    )

    return {
        "id": quiz_id,
        "name": quiz_name,
        "questions": [
            {"concept_id": cid, "question": question}
            for cid, question in zip(cids, questions)
        ],
        "total_no_questions": len(cids),
    }
