import json
import os

# from asyncio import Semaphore
from contextlib import asynccontextmanager
from typing import List, Optional
from uuid import uuid4

from fastapi import FastAPI, File, Form, Path, Query, UploadFile
from pydantic import BaseModel

import concept_extraction
import concepts
import db
import notes

# * Context manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    global connection

    connection = db.create_connection(
        os.path.join(os.path.dirname(__file__), "db.sqlite")
    )

    connection.execute("PRAGMA foreign_keys = ON")

    # *Create notes tables
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

    # *Create concepts tables
    db.execute_write_query(
        connection,
        """
        CREATE TABLE IF NOT EXISTS concepts (
            id TEXT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            content TEXT NOT NULL
        );
        """,
    )
    db.execute_write_query(
        connection,
        """
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY NOT NULL,
            concept_id TEXT NOT NULL,
            state TEXT,
            step TEXT,
            stability REAL,
            difficulty REAL,
            due TEXT,
            last_review TEXT,
            FOREIGN KEY(concept_id) REFERENCES concepts(id) ON DELETE CASCADE
        );
        """,
    )
    db.execute_write_query(
        connection,
        """
        CREATE TABLE IF NOT EXISTS review_logs (
            id         INTEGER PRIMARY KEY,
            card_id    INTEGER NOT NULL,
            rating     INTEGER,
            review_datetime TEXT,
            review_duration TEXT,
            FOREIGN KEY(card_id) REFERENCES cards(id) ON DELETE CASCADE
        );
        """,
    )

    yield  # *run app

    connection.close()


# * App

app = FastAPI(lifespan=lifespan)

# sem = Semaphore(1)

# *Models


class TextNoteIn(BaseModel):
    name: str
    content: str


class StartQuizIn(BaseModel):
    concept_limit: int
    question_limit: int
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
        "DELETE FROM notes WHERE id = ?",
        (note_id,),
    )
    return {"deleted": True}


@app.post("/notes/{note_id}/process")
async def process_note_into_concept(note_id: str = Path(...)):
    status = db.execute_read_query(
        connection,
        "SELECT status FROM notes WHERE id = ?",
        (note_id,),
    )[0][0]

    if status in ["processing", "processed"]:
        return {"error": "Note is already being processed or has been processed"}

    db.execute_write_query(
        connection,
        """
        UPDATE notes
        SET status = 'processing'
        WHERE id = ?
        """,
        (note_id,),
    )

    content = db.execute_read_query(
        connection,
        "SELECT content FROM notes WHERE id = ?",
        (note_id,),
    )[0][0]

    extracted_concepts = concept_extraction.extract_concepts(content)

    for name, content in extracted_concepts.items():
        concepts.create_concept_card(connection, name, content)

    db.execute_write_query(
        connection,
        """
        UPDATE notes
        SET status = 'processed'
        WHERE id = ?
        """,
        (note_id,),
    )

    return {"note_id": note_id, "concepts_generated": len(extracted_concepts)}


# *CONCEPTS


@app.get("/concepts")
async def list_concepts():
    raw_concepts = db.execute_read_query(connection, "SELECT id, name FROM concepts")

    concepts = []

    for id, name in raw_concepts:
        srs_info = db.execute_read_query(
            connection,
            """
            SELECT id, state, step, stability, difficulty, due, last_review
            FROM cards
            WHERE concept_id = ?
            """,
            (id,),
        )[0]
        concepts.append({"id": id, "name": name, "srs_info": srs_info})

    return concepts


@app.get("/concepts/{concept_id}")
async def get_concept_by_id(concept_id: str = Path(...)):
    name, content = db.execute_read_query(
        connection, "SELECT name, content FROM concepts WHERE id = ?", (concept_id,)
    )[0]

    srs_info = db.execute_read_query(
        connection,
        """
        SELECT id, state, step, stability, difficulty, due, last_review
        FROM cards
        WHERE concept_id = ?
        """,
        (concept_id,),
    )[0]

    return {"name": name, "content": content, "srs_info": srs_info}


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
