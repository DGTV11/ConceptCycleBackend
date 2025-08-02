from datetime import timedelta
from uuid import uuid4

from fsrs import Card, Rating, ReviewLog, Scheduler

import db

"""
CREATE TABLE IF NOT EXISTS concepts (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    content TEXT NOT NULL
);
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
CREATE TABLE IF NOT EXISTS review_logs (
    id         INTEGER PRIMARY KEY,
    card_id    INTEGER NOT NULL,
    rating     INTEGER,
    review_datetime TEXT,
    review_duration TEXT,
    FOREIGN KEY(card_id) REFERENCES cards(id) ON DELETE CASCADE
);
"""

scheduler = Scheduler(
    learning_steps=(
        timedelta(minutes=1),
        timedelta(minutes=10),
        timedelta(minutes=30),
        timedelta(days=1),
    ),
    relearning_steps=(
        timedelta(minutes=1),
        timedelta(minutes=10),
        timedelta(minutes=30),
        timedelta(hours=1),
        timedelta(days=1),
    ),
    maximum_interval=1209600,  # 2 weeks
    enable_fuzzing=True,
)


def create_concept_card(connection, name: str, content: str):
    concept_id = str(uuid4())
    db.execute_write_query(
        connection,
        """
        INSERT INTO concepts (id, name, content)
        VALUES (?, ?, ?)
        """,
        (concept_id, name, content),
    )

    card_dict = Card().to_dict()

    db.execute_write_query(
        connection,
        """
        INSERT INTO cards (id, concept_id, state, step, stability, difficulty, due, last_review)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            card_dict["card_id"],
            concept_id,
            card_dict["state"],
            card_dict["step"],
            card_dict["stability"],
            card_dict["difficulty"],
            card_dict["due"],
            card_dict["last_review"],
        ),
    )
