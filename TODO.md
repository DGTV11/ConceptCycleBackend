# Intended UX

User gives the platform their notes (markdown/txt, pdf, audio(?), image, pptx, pdfs(?)), platform processes notes.

```
Step 1: input notes in the form of text/md files, audio (transcription), images (to be converted into text using VLMs), pdfs and pptx files

Step 2: LLM takes all the notes and condenses them into topics, subtopics and then distinct byte-sized concept documents (objects with title and content fields + SRS parameters)
```

## Adaptive quiz mode:

User uses quiz mode -> AI tests user on concepts from notes then uses SRS to calculate review timings for each concept (basically how long until concept can be tested again)

For users willing to sit down and study for a bit

```
Step 3: Upon first user request, LLM generates quiz based on these concept documents (one question per concept) (limit total no of concepts in a quiz) and tests user with questions based on these concepts to promote active recall

Step 4: LLM grades quiz and update tested concepts’ SRS parameters based on Leitner system or https://github.com/open-spaced-repetition/py-fsrs?tab=readme-ov-file#usage

Step 5: Upon subsequent user requests, LLM generates quiz based on due (based on SRS algorithm) and unseen concept documents (one question per concept) (limit number of new concepts and total no of concepts in a quiz) and tests user with questions based on these concepts to promote active recall
```

## Quick revision notes generator (DO NOT DO DURING THIS TvP SP, DO AFTER PRESENTATION):

User uses quick revision notes generator -> user chooses either cheat sheet or mindmap -> AI generates chosen type of notes

```
Step 3: Upon user request, LLM generates an easily digestible cheat sheet (made using markdown) OR mindmap (https://graphviz.org/, may not be built in initial prototype) based on the generated concept documents

Step 4: User may download the cheat sheet as a markdown file or pdf and the mindmap as a pdf 
```

# Roadmap

1. Set up division of labour within the team
**(DONE)**

2. Prepare LLM backend (try to use smth like OpenRouter or Groq and not Ollama)
**(TODO)**

3. Make API using FastAPI and pocketflow (using stuff like ChromaDB and OpenAI)

- design API interface **(DONE)**
- design prompts and Flows **(TODO)**
    - concept extractor **(DONE)**
    - quiz generator **(TODO)**
    - quiz grader + SRS update system **(TODO)**
- (OPTIONAL because LAZY) implement authentication (https://medium.com/@wangarraakoth/user-authentication-in-fastapi-using-python-3b51af11b38d)

4. Make suitable frontend (app for prototype development TBD) **(TODO)**

5. (NOT URGENT) DOCKERISE (so I can self-host on my rpi) **(TODO)**
