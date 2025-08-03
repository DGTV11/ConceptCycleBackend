FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ADD . /app

WORKDIR /app

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     gcc \
#     pkg-config \
#     libssl-dev \
#     rustc \
#     cargo \
#  && rm -rf /var/lib/apt/lists/*

RUN uv sync --locked --compile-bytecode

ENTRYPOINT ["uv", "run", "fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "5046"]
# ENTRYPOINT ["uv", "run", "fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "5046"]
