# 📚 Study Platform API Docs

Base URL: `http://localhost:5046`
Version: `v1`

Do note that example response data, if any are merely illustrative and may not reflect the API's true output

---

## **Notes**

### `POST /notes`

Upload a new note.

* **Body**: `multipart/form-data` (file upload, optional metadata)
* **Response**: `{ "note_id": "uuid" }`

---

### `POST /notes/text`

Upload a new note in text form.

* **Response**: `{ "note_id": "uuid" }`

---


### `GET /notes`

List all uploaded notes.

* **Response**: `[ { "id": "uuid", "name": "string", "status": "processed|processing|pending" } ]`

---

### `GET /notes/{note_id}`

Get a specific note by ID.

* **Response**: `{ "name": "string", "content": "string", "status": "processed|processing|pending" }`

---

### `DELETE /notes/{note_id}`

Delete a note by ID.

* **Response**: `{ "deleted": true }`

---

### `POST /notes/{note_id}/process`

Process a note into concept documents.

* **Response**: `{ "note_id": "uuid", "concepts_generated": int }` | `{ "error": "Note is already being processed or has been processed" }`

---

## **Concepts**

### `GET /concepts`

List all concepts.

* **Response**: `[ { "id": "c1", "name": "string" } ]`

---

### `GET /concepts/{concept_id}`

Get details of a concept.

* **Response**: `{ "name": "string", "content": "string", "srs_info": {...} }`

---

## **Quizzes**

### `GET /quizzes`

List all quizzes (past + active).

* **Response**: `[ { "quiz_id": "q1", "created": "timestamp", "status": "active|completed" } ]`

---

### `POST /quizzes`

Start a new quiz.

* **Query params**:

  * `concept_limit`: int → number of concepts
  * `question_limit`: int → number of questions (must be above or equal to number of concepts)
  * `mode`: string → `"due_only" | "new_only" | "mixed"`
* **Response**: `{ "quiz_id": "q1", "questions": [ { "concept_id": "c1", "question": "string" } ] }`

---

### `GET /quizzes/{quiz_id}`

Get quiz by ID.

* **Response**: `{ "quiz_id": "q1", "questions": [...], "status": "active|completed" }`

---

### `POST /quizzes/{quiz_id}/submit`

Submit answers for a quiz.

* **Body**:

```json
{
  "responses": [
    { "concept_id": "c1", "answer": "string", "grade": 0-5 }
  ]
}
```

* **Response**:

```json
{
  "quiz_id": "q1",
  "updated_concepts": [
    { "id": "c1", "next_due": "timestamp", "interval": 3 }
  ]
}
```
