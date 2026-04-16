FROM python:3.14-slim

WORKDIR /app

RUN pip install uv

COPY bot/pyproject.toml bot/uv.lock ./
RUN uv sync --frozen

COPY bot/ ./

CMD ["python", "bot.py"]