# Adapted from https://github.com/astral-sh/uv-docker-example

# ---
# Stage 1: build the application
# ---

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# 🔧 Копируем файлы зависимостей
COPY uv.lock pyproject.toml ./
COPY backend/pyproject.toml ./backend/

# 🔧 Устанавливаем зависимости
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# 🔧 Копируем ВЕСЬ код backend (включая app/run.py)
COPY backend/ ./backend/

# ---
# Stage 2: final image
# ---

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Создаём пользователя
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# 🔧 Копируем ВСЁ приложение из builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Добавляем venv в PATH
ENV PATH="/app/.venv/bin:$PATH"

# Переключаемся на non-root пользователя
USER nonroot

# Рабочая директория
WORKDIR /app

# 🔧 Запускаем приложение (путь относительно WORKDIR /app)
CMD ["python", "backend/app/run.py"]
