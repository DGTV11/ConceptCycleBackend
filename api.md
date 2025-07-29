# 📚 Study Platform REST API

## **Base URL**

```
/api/v1
```

---

## **Step 1: Input Notes**

### `POST /notes/upload`

Upload notes in various formats.

**Request**

* `multipart/form-data`

  * `file` (required) — txt, md, pdf, pptx, image, audio
  * `metadata` (optional, JSON) — e.g., subject, tags

**Response**

```json
{
  "note_id": "uuid-123",
  "status": "processing",
  "message": "Notes uploaded successfully and queued for processing."
}
```

---

## **Step 2: Process Notes into Concepts**

### `POST /notes/:note_id/process`

Convert notes into concept objects.

**Response**

```json
{
  "concepts": [
    {
      "id": "c1",
      "title": "Efflux Pump-mediated Resistance",
      "content": "Mechanism where bacteria expel antibiotics...",
      "srs": {
        "interval": 0,
        "ease_factor": 2.5,
        "repetitions": 0,
        "due_date": "2025-07-30T00:00:00Z"
      }
    },
    {
      "id": "c2",
      "title": "Stages of Viral Infection: Attachment",
      "content": "Virus attaches to host cell surface receptors...",
      "srs": { ... }
    }
  ]
}
```

---

## **Adaptive Quiz Mode**

### `POST /quiz/start`

Generate quiz from due + new concepts.

**Request**

```json
{
  "limit": 10,
  "mode": "mixed"  // "due_only", "new_only", "mixed"
}
```

**Response**

```json
{
  "quiz_id": "q-001",
  "questions": [
    {
      "concept_id": "c1",
      "question": "What mechanism allows bacteria to resist antibiotics by pumping them out?",
      "type": "short_answer"
    },
    {
      "concept_id": "c2",
      "question": "What is the first stage of viral infection?",
      "type": "mcq",
      "options": ["Replication", "Attachment", "Maturation", "Release"]
    }
  ]
}
```

---

### `POST /quiz/:quiz_id/submit`

Submit answers and update SRS.

**Request**

```json
{
  "responses": [
    { "concept_id": "c1", "answer": "Efflux pump", "grade": 5 },
    { "concept_id": "c2", "answer": "Replication", "grade": 2 }
  ]
}
```

* `grade` can follow FSRS/Leitner scale (0–5).

**Response**

```json
{
  "updated_concepts": [
    {
      "id": "c1",
      "next_due": "2025-08-02T00:00:00Z",
      "interval": 3,
      "ease_factor": 2.6
    },
    {
      "id": "c2",
      "next_due": "2025-07-30T00:00:00Z",
      "interval": 0,
      "ease_factor": 2.3
    }
  ]
}
```

---

## **Quick Revision Notes Generator**

### `POST /revision/generate`

Generate cheat sheet or mindmap.

**Request**

```json
{
  "format": "cheatsheet",  // or "mindmap"
  "concept_ids": ["c1", "c2", "c3"]
}
```

**Response**

```json
{
  "revision_id": "r-001",
  "format": "cheatsheet",
  "content": "## Efflux Pump-mediated Resistance\n- Bacteria pump out antibiotics...\n\n## Stages of Viral Infection\n1. Attachment..."
}
```

### `GET /revision/:revision_id/download?type=pdf`

Download as PDF/Markdown.

---

## **Core Entities**

### **Concept Object**

```json
{
  "id": "string",
  "title": "string",
  "content": "string",
  "srs": {
    "interval": "int",
    "ease_factor": "float",
    "repetitions": "int",
    "due_date": "datetime"
  }
}
```

### **Quiz Object**

```json
{
  "quiz_id": "string",
  "questions": [ ... ]
}
```

---

## **Tech stack suggestion**

* Backend: **FastAPI** (Python, async-friendly, easy REST)
* Storage: **PostgreSQL** (concepts, SRS state)
* File handling: **Celery + Redis** (process uploads async)
* SRS: [py-fsrs](https://github.com/open-spaced-repetition/py-fsrs)
* Exports: **WeasyPrint** (for PDF), **Graphviz** (for mindmaps)
