import json
from asyncio import Semaphore
from datetime import timedelta
from time import time
from uuid import uuid4

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# sem = Semaphore(1)

# *NOTES


@app.post("/notes")
async def upload_notes():
    pass


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
    uvicorn.run(app, port=5046, host="0.0.0.0")
