"""Intent router: user message → LLM with tools → API calls → response."""
import asyncio
import re
import sys
from services.llm_client import LLMClient

def _classify_simple_intent(text: str) -> str:
    """Quick classification for VERY simple cases only."""
    text_lower = text.lower().strip()
    # Только точные совпадения для приветствий
    if text_lower in ["hello", "hi", "hey", "привет"]:
        return "greeting"
    if text_lower in ["thanks", "thank you", "спасибо"]:
        return "thanks"
    # Не классифицируем "help" — пусть LLM решает
    return None

def get_fallback_response(intent: str, text: str) -> str:
    """Return helpful response for simple intents."""
    if intent == "greeting":
        return "👋 Hello! I am your LMS assistant. I can help you with labs, scores, students, and groups. Just ask in plain English!"
    elif intent == "thanks":
        return "😊 You are welcome! Let me know if you need anything else about your labs."
    return "🤔 I am not sure I understood. Try asking about labs, scores, students, or groups!"

async def route_intent(user_message: str) -> str:
    """Main entry point: route user message to LLM or fallback."""
    print(f"[router] Input: {user_message}", file=sys.stderr)
    
    # Проверяем очень простые случаи
    simple_intent = _classify_simple_intent(user_message)
    if simple_intent:
        print(f"[router] Simple intent: {simple_intent}", file=sys.stderr)
        return get_fallback_response(simple_intent, user_message)
    
    # Для всего остального — LLM с инструментами
    print(f"[router] Calling LLM with tools...", file=sys.stderr)
    async with LLMClient() as llm:
        system_prompt = """You are a helpful assistant for a university Learning Management System.
You have access to backend tools to fetch real data about labs, students, and scores.
When the user asks a question, decide which tool(s) to call to get the answer.
After receiving tool results, summarize the data in a clear, friendly way.
Always mention specific lab numbers (like Lab 01, Lab 02) and percentages when available.
If you cannot answer, say so politely and suggest what the user could ask instead."""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}]
        try:
            print(f"[router] Sending to LLM: {user_message[:50]}...", file=sys.stderr)
            response = await llm.chat_with_tools(messages, max_turns=3)
            print(f"[router] LLM response: {response[:100]}...", file=sys.stderr)
            return response
        except Exception as e:
            print(f"[router] LLM error: {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)
            # Фолбэк при ошибке LLM — но с полезной информацией
            return f"📋 Available labs: Lab 01 (Products), Lab 02 (Backend), Lab 03 (Agent), Lab 04 (Frontend). Ask me about scores, pass rates, or top students for any lab!"
