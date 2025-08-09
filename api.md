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

### `GET /notes/{note_id}/concepts`

Get details of all concepts under a note.

* **Response**: `[ { "id": "uuid", "name": "string", "content": "string", "srs_info": {...} } ]`

---

## **Concepts**

### `GET /concepts`

List all concepts.

* **Response**: `[ { "id": "uuid", "note_id": "uuid", "name": "string", "srs_info": {...} } ]`

---

### `GET /concepts/{concept_id}`

Get details of a concept.

* **Response**: `{ "note_id": "uuid", "name": "string", "content": "string", "srs_info": {...} }`

---

## **Quizzes**

### `GET /quizzes`

List all quizzes (past + active).

* **Response**: `[ { "id": "q1", "name": "string", "status": "active|completed", "total_no_questions": int, "total_score": int | null } ]`

---

### `POST /quizzes`

Start a new quiz.

* **Query params**:

  * `note_ids` : list[str] → list of note ids
  * `concept_limit`: int → number of concepts
  * `question_limit`: int → number of questions (must be above or equal to number of concepts)
  * `mode`: string → `"due_only" | "learning_only" | "new_only" | "mixed"`
* **Response**: `{ "id": "q1", "name": "string", "questions": [ { "concept_id": "c1", "question": "string" } ], "total_no_questions": int }`

---

### `GET /quizzes/{quiz_id}`

Get quiz by ID.

* **Response**: `{ "name": "string", "status": "active|completed", "questions": [ { "concept_id": "c1", "question": "string", "response": "str" | null, "grade": int | null , "feedback": "str" | null } ], "total_no_questions": int, "total_score": int | null }`

---

### `POST /quizzes/{quiz_id}/submit`

Submit answers for a quiz.

* **Body**:

```json
{
  "answers": [...]
}
```

* **Response**:

```json
{
  "grades": [ int ],
  "feedback": [ "feedback" ],
  "total_score": int
}
```
