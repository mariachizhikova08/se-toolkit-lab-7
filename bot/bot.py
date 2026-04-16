#!/usr/bin/env python3
"""Bot entry point with --test mode and LLM intent routing."""
import sys
import asyncio
import argparse
from handlers.commands import (
    handle_start, handle_help, handle_health, handle_labs, handle_scores, handle_text_message
)
from config import settings

COMMANDS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
}

def process_command(command: str, text: str = "") -> str:
    """Route command to appropriate handler."""
    if command == "/start":
        return handle_start()
    elif command == "/help":
        return handle_help()
    elif command == "/health":
        return handle_health()
    elif command == "/labs":
        return handle_labs()
    elif command == "/scores":
        return handle_scores(text)
    else:
        full_text = f"{command} {text}".strip() if text else command
        return handle_text_message(full_text)

def run_test_mode(command: str) -> int:
    """Test mode: call handler directly, print result, exit."""
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else ""
    result = process_command(cmd, arg)
    print(result)
    return 0

async def run_telegram_bot():
    """Real Telegram bot using aiogram with inline buttons."""
    if not settings.BOT_TOKEN:
        print("⚠️ BOT_TOKEN not set.", file=sys.stderr)
        return 1
    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import Command
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    
    def get_start_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 List labs", callback_data="cmd_labs")],
            [InlineKeyboardButton(text="📊 Lab scores", callback_data="cmd_scores")],
            [InlineKeyboardButton(text="🏆 Top students", callback_data="cmd_top")],
        ])
    
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer(handle_start(), reply_markup=get_start_keyboard())
    
    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        await message.answer(handle_help())
    
    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        await message.answer(handle_health())
    
    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        await message.answer(handle_labs())
    
    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message):
        args = message.text.split(maxsplit=1)
        query = args[1] if len(args) > 1 else ""
        await message.answer(handle_scores(query))
    
    @dp.callback_query(lambda c: c.data.startswith("cmd_"))
    async def handle_callback(callback: types.CallbackQuery):
        cmd = callback.data.replace("cmd_", "")
        if cmd == "labs":
            await callback.message.edit_text(handle_labs(), reply_markup=get_start_keyboard())
        elif cmd == "scores":
            await callback.message.answer("🔍 Which lab? Example: lab-04")
        elif cmd == "top":
            await callback.message.answer("🏆 Top students for which lab? Example: lab-04")
        await callback.answer()
    
    @dp.message()
    async def handle_free_text(message: types.Message):
        text = message.text or ""
        if text.startswith("/"):
            response = handle_text_message(text)
        else:
            response = handle_text_message(text)
        await message.answer(response)
    
    print(f"🤖 Bot started with LLM intent routing!")
    await dp.start_polling(bot)
    return 0

def main():
    parser = argparse.ArgumentParser(description="LMS Telegram Bot with LLM routing")
    parser.add_argument("--test", type=str, help="Test mode: run command and print result")
    args = parser.parse_args()
    
    if args.test:
        return run_test_mode(args.test)
    else:
        return asyncio.run(run_telegram_bot())

if __name__ == "__main__":
    sys.exit(main())
