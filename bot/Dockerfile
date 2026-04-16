FROM python:3.14.2-slim-bookworm

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
COPY *.py ./
COPY handlers/ ./handlers/
COPY services/ ./services/

RUN uv sync

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "bot.py"]
