# AI Study Buddy Backend

## Install
1. Clone repo
```bash
git clone git@github.com:DGTV11/AIStudyBuddyBackend.git
```

OR 

```bash
git clone https://github.com/DGTV11/AIStudyBuddyBackend.git
```

2. Install dependencies
```bash
pip install uv
uv sync
```

3. Add `.env` file to directory and configure
```env
LLM_API_BASE_URL=<fill me>
LLM_API_KEY=<fill me>
LLM_NAME=<fill me>
VLM_API_BASE_URL=<fill me>
VLM_API_KEY=<fill me>
VLM_NAME=<fill me>
CHUNK_MAX_TOKENS=<fill me>
DEBUG_MODE=<fill me>
```

3. Run server
```bash
uv run main.py
```
