#!/usr/bin/env python3
"""Bot entry point with --test mode and real Telegram support."""
import sys
import asyncio
import argparse
from handlers.commands import (
    handle_start, handle_help, handle_health, handle_labs, handle_unknown
)
from config import settings

# Маппинг команд → функции-хендлеры
COMMANDS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
}

def process_command(command: str, text: str = "") -> str:
    """Route command to appropriate handler."""
    handler = COMMANDS.get(command)
    if handler:
        if command == "/labs":
            return handler(text)
        return handler()
    return handle_unknown(f"{command} {text}".strip())

def run_test_mode(command: str) -> int:
    """Test mode: call handler directly, print result, exit."""
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else ""
    result = process_command(cmd, arg)
    print(result)
    return 0

async def run_telegram_bot():
    """Real Telegram bot using aiogram."""
    if not settings.BOT_TOKEN:
        print("⚠️ BOT_TOKEN not set. Bot cannot start.", file=sys.stderr)
        return 1
    
    # Импортируем aiogram только если токен есть
    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import Command
    
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрация хендлеров
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer(handle_start())
    
    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        await message.answer(handle_help())
    
    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        await message.answer(handle_health())
    
    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        # Получаем аргумент после /labs (если есть)
        args = message.text.split(maxsplit=1)
        query = args[1] if len(args) > 1 else ""
        await message.answer(handle_labs(query))
    
    # Обработчик для неизвестных команд и текста
    @dp.message()
    async def handle_other(message: types.Message):
        text = message.text or ""
        # Пытаемся распознать команду без слэша
        if text.startswith("/"):
            cmd = text.split()[0]
            response = handle_unknown(cmd)
        else:
            response = handle_unknown(text)
        await message.answer(response)
    
    print(f"🤖 Bot started! Token: {'*' * 10}{settings.BOT_TOKEN[-5:]}")
    await dp.start_polling(bot)
    return 0

def main():
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument("--test", type=str, help="Test mode: run command and print result")
    args = parser.parse_args()
    
    if args.test:
        return run_test_mode(args.test)
    else:
        # Запускаем асинхронный бот
        return asyncio.run(run_telegram_bot())

if __name__ == "__main__":
    sys.exit(main())
