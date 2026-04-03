"""Command handlers — pure functions, no Telegram dependency."""

def handle_start() -> str:
    """Handle /start command."""
    return "👋 Привет! Я бот для работы с учебной системой.\nИспользуй /help для списка команд."

def handle_help() -> str:
    """Handle /help command."""
    return "📚 Доступные команды:\n/start — начать работу\n/help — эта справка\n/health — статус бэкенда\n/labs — список лабораторных"

def handle_health() -> str:
    """Handle /health command."""
    return "✅ Бот работает! (заглушка для Task 1)"

def handle_labs(query: str = "") -> str:
    """Handle /labs command with optional query."""
    if query:
        return f"🔍 Поиск по запросу '{query}'...\n(реализация в Task 2)"
    return "📋 Доступные лабораторные:\n• Lab 01 — Введение\n• Lab 02 — Docker\n• Lab 03 — API\n(заглушка для Task 1)"

def handle_unknown(text: str) -> str:
    """Handle unknown commands or free text."""
    return f"🤔 Я пока не умею обрабатывать: '{text}'\nИспользуй /help для списка команд."
