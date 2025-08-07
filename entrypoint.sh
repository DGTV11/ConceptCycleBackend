#!/bin/sh
set -e

touch db.sqlite
# exec uv run fastapi run main.py --host 0.0.0.0 --port 5046
exec uv run fastapi dev main.py --host 0.0.0.0 --port 5046
