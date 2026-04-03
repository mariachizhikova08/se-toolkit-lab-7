# Development Plan: LMS Telegram Bot

## Overview
This bot integrates with the university Learning Management System to provide students with quick access to lab statuses, scores, and deadlines via Telegram.

## Architecture
- **Handlers layer** (`handlers/`): Pure functions that process commands and return text. No Telegram dependency — enables easy testing via `--test` mode.
- **Services layer** (`services/`): API clients for LMS backend and LLM provider. Abstracted for easy mocking in tests.
- **Config management** (`config.py`): Loads environment variables from `.env.bot.secret` with sensible defaults.
- **Entry point** (`bot.py`): Supports both `--test` mode for CI/CD and real Telegram mode via aiogram.

## Task Breakdown
1. **Task 1 (Scaffold)**: Project structure, `--test` mode, placeholder handlers.
2. **Task 2 (Backend Integration)**: Connect handlers to real LMS API via `services/lms_client.py`.
3. **Task 3 (Intent Routing)**: Add LLM-based routing for free-text queries using `services/llm_client.py`.
4. **Task 4 (Containerize)**: Dockerize the bot for consistent deployment.

## Testing Strategy
- Unit tests for handlers (pure functions = easy to test).
- Integration tests via `--test` mode (no Telegram token needed).
- Manual testing in Telegram after each task.

## Deployment
- Run on VM with `nohup uv run bot.py &`.
- Environment variables via `.env.bot.secret`.
- Future: Docker Compose service alongside backend.
