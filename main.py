import json
import os
from asyncio import Semaphore
from typing import List, Optional
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, File, Form, Path, Query, UploadFile
from pydantic import BaseModel

import concepts
import db
import notes

app = FastAPI()


# sem = Semaphore(1)

# *Models


class TextNoteIn(BaseModel):
    name: str
    content: str


class StartQuizIn(BaseModel):
    limit: int
    mode: str


class SubmitQuizIn(BaseModel):
    responses: List[str]


# *Endpoints


@app.post("/notes")
async def upload_notes(
    file: UploadFile = File(...),
    content_type: str = Form(...),
):
    filename = file.filename.rsplit(".", 1)[0]
    content_bytes = await file.read()
    content = notes.process_file(content_bytes, filename, content_type)

    note_id = str(uuid4())
    db.execute_write_query(
        connection,
        """
        INSERT INTO notes (id, name, content, status)
        VALUES (?, ?, ?, 'pending')
        """,
        (note_id, filename, content),
    )
    return {"note_id": note_id}


@app.post("/notes/text")
async def upload_textual_notes(note: TextNoteIn):
    note_id = str(uuid4())
    db.execute_write_query(
        connection,
        """
        INSERT INTO notes (id, name, content, status)
        VALUES (?, ?, ?, 'pending')
        """,
        (note_id, note.name, note.content),
    )
    return {"note_id": note_id}


@app.get("/notes")
async def list_notes():
    notes = db.execute_read_query(connection, "SELECT id, name, status FROM notes")

    return [{"id": id, "name": name, "status": status} for id, name, status in notes]


@app.get("/notes/{note_id}")
async def get_note_by_id(note_id: str = Path(...)):
    name, content, status = db.execute_read_query(
        connection,
        """
        SELECT name, content, status 
        FROM notes
        WHERE id = ?
        """,
        (note_id,),
    )[0]

    return {"name": name, "content": content, "status": status}


@app.delete("/notes/{note_id}")
async def delete_note_by_id(note_id: str = Path(...)):
    db.execute_write_query(
        connection,
        "DELETE FROM notes WHERE id=?",
        (note_id,),
    )
    return {"deleted": True}


@app.post("/notes/{note_id}/process")
async def process_note_into_concept(note_id: str = Path(...)):
    pass


# *CONCEPTS


@app.get("/concepts")
async def list_concepts():
    pass


@app.get("/concepts/{concept_id}")
async def get_concept_by_id(concept_id: str = Path(...)):
    pass


# *QUIZZES


@app.get("/quizzes")
async def list_quizzes():
    pass


@app.post("/quizzes")
async def start_quiz(quiz_data: StartQuizIn):
    pass


@app.get("/quizzes/{quiz_id}")
async def get_quiz(quiz_id: str = Path(...)):
    pass


@app.post("/quizzes/{quiz_id}/submit")
async def submit_quiz(quiz_id: str = Path(...), submit_data: SubmitQuizIn = None):
    pass


if __name__ == "__main__":
    connection = db.create_connection(
        os.path.join(os.path.dirname(__file__), "db.sqlite")
    )

    db.execute_write_query(
        connection,
        """
        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            status TEXT NOT NULL
        );
        """,
    )

    db.execute_write_query(
        connection,
        """
        CREATE TABLE IF NOT EXISTS conccepts (
            id TEXT PRIMARY KEY NOT NULL,
            content TEXT NOT NULL
        );
        """,
    )

    uvicorn.run(app, port=5046, host="0.0.0.0")

    connection.close()
