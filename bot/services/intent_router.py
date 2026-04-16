"""Intent router using LLM with tool calling."""

import asyncio
from services.llm_client import LLMClient

SYSTEM_PROMPT = """You are a helpful LMS assistant. The user asks questions about labs, students, scores, and analytics.

You have tools to fetch real data from the backend API. Use them to answer questions accurately.
- Use get_items to list available labs
- Use get_learners to get enrolled students
- Use get_pass_rates for pass rates by lab
- Use get_scores for score distribution
- Use get_groups for group performance
- Use get_top_learners for leaderboard
- Use get_timeline for submission timeline
- Use get_completion_rate for completion stats
- Use trigger_sync to refresh data

When user asks something vague like just "lab 4" or "scores", ask clarifying question.
For greetings like "hello", respond friendly and mention what you can help with.
For gibberish, politely say you didn't understand and list what you can help with."""


async def route_intent_async(text: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text},
    ]
    try:
        async with LLMClient() as client:
            result = await client.chat_with_tools(messages)
            return result
    except Exception as e:
        return f"I apologize, but I encountered an error: {type(e).__name__}. Please try again later."


def route_intent(text: str) -> str:
    return asyncio.run(route_intent_async(text))
