FROM ghcr.io/astral-sh/uv:python3.12-alpine

RUN apk add --no-cache gcc musl-dev libgcc rust cargo

ADD . /app

WORKDIR /app
RUN uv sync --locked # --compile-bytecode

# CMD ["uv", "run", "fastapi", "run", "main.py"]
CMD ["uv", "run", "fastapi", "dev", "main.py"]
