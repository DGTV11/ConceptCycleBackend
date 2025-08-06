from datetime import datetime

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


# *QUIZ GRADER


def create_quiz_from_note(
    connection, note_ids, concept_limit, question_limit, mode
):  # *TODO: add mode selector (mode -> "due_only" | "learning_only" | "new_only" | "mixed")
    concepts = {}

    for note_id in note_ids:
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

    quiz_concept_counts = {}

    no_questions = 0
    while no_questions < question_limit:
        question_cids[concepts[no_questions][0]] += 1
        no_questions += 1

    # *TODO: make actual question generator
