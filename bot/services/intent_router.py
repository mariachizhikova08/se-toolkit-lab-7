"""Intent router: user message → LLM with tools → REAL backend API → response."""
import asyncio
import sys
from services.llm_client import LLMClient

async def route_intent(user_message: str) -> str:
    """Main entry point: route user message to LLM with tools."""
    print(f"[router] Input: {user_message}", file=sys.stderr)
    
    async with LLMClient() as llm:
        system_prompt = """You are a helpful assistant for a university Learning Management System.
You have access to backend tools to fetch REAL data about labs, students, and scores.
When the user asks a question, you MUST call the appropriate tool(s) to get real data.
After receiving tool results, summarize the data clearly.
Always mention specific lab names (Products, Architecture, Backend, Testing, Pipeline, Agent) and percentages when available.
If you cannot answer, say so politely."""
        
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}]
        
        try:
            print(f"[router] Calling LLM with tools...", file=sys.stderr)
            response = await llm.chat_with_tools(messages, max_turns=3)
            print(f"[router] LLM response: {response[:200]}...", file=sys.stderr)
            return response
        except Exception as e:
            print(f"[router] LLM error: {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)
            # Фолбэк — но с реальными данными от бэкенда
            try:
                from services.lms_client import LMSClient
                async with LMSClient() as backend:
                    labs = await backend.get_labs()
                    if labs:
                        lab_names = []
                        for lab in labs[:5]:
                            title = lab.get("title", "Unknown")
                            lab_names.append(f"- {title}")
                        return f"📋 Available labs:\n" + "\n".join(lab_names) + "\n\nAsk me about scores, pass rates, or top students for any lab!"
            except:
                pass
            return "⚠️ I had trouble connecting to the AI service. Please try again in a moment."

def handle_text_message(text: str) -> str:
    """Sync wrapper for route_intent."""
    return asyncio.run(route_intent(text))
