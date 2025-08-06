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


def create_quiz_from_note(connection, note_ids, concept_limit, question_limit):
    concepts = []

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

            concepts.append(
                {"id": id, "name": name, "content": content, "srs_info": srs_info}
            )

    concepts.sort(
        key=lambda concept: (
            0
            if not concept["srs_info"]["stability"]
            else concept["srs_info"]["stability"]
        )
    )  # *Prioritises low stability for review
