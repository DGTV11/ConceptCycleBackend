import json
import os
from asyncio import Semaphore
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel

import concepts
import notes

app = FastAPI()

# sem = Semaphore(1)

# *NOTES


@app.post("/notes")
async def upload_notes(file: UploadFile):
    content_type = file.content_type

    content = notes.process_file(await file.read(), file.content_type)

    note_id = db.execute_query(
        connection,
        """
        INSERT INTO
            users (name, content)
        VALUES
            (?, ?)
        """,
        (os.path.basename(file.filename).split(".")[0], content),
    )

    return {"note_id": note_id}


@app.post("/notes/text")
async def upload_textual_notes(name: str, content: str):
    note_id = db.execute_query(
        connection,
        """
        INSERT INTO
            users (name, content)
        VALUES
            (?, ?)
        """,
        (name, content),
    )

    return {"note_id": note_id}


@app.get("/notes")
async def list_notes():
    pass


@app.get("/notes/{note_id}")
async def get_note_by_id(note_id: str):
    pass


@app.delete("/notes/{note_id}")
async def delete_note_by_id(note_id: str):
    pass


@app.post("/notes/{note_id}/process")
async def process_note_into_concept(note_id: str):
    pass


# *CONCEPTS


@app.get("/concepts")
async def list_concepts():
    pass


@app.get("/concepts/{concept_id}")
async def get_concept_by_id(concept_id: str):
    pass


# *QUIZZES


@app.get("/quizzes")
async def list_quizzes():
    pass


@app.post("/quizzes")
async def start_quiz(limit: int, mode: str):
    pass


@app.get("/quizzes/{quiz_id}")
async def get_quiz(quiz_id: str):
    pass


@app.post("/quizzes/{quiz_id}/submit")
async def submit_quiz(quiz_id: str, responses: list[str]):
    pass


if __name__ == "__main__":
    db_connection = db.create_connection(
        os.path.join(os.path.dirname(__file__), "db.sqlite")
    )
    db.execute_query(
        connection,
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT NOT NULL
        );
        """,
    )

    uvicorn.run(app, port=5046, host="0.0.0.0")

    connection.close()
