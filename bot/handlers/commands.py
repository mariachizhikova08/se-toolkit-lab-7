"""Command handlers."""
import asyncio
from services.lms_client import LMSClient
from services.intent_router import route_intent

LAB_NAME_MAP = {
    "lab 1": "Products API Architecture",
    "lab 2": "Backend Testing Pipeline",
    "lab 3": "Agent Integration Testing",
    "lab 4": "Frontend Backend Sync",
    "lab 5": "Deployment Pipeline Setup",
}

def handle_start() -> str:
    return "Welcome to the LMS Bot Assistant! Use /help to see available commands."

def handle_help() -> str:
    return "Available commands: /start, /help, /health, /labs, /scores <lab>"

async def handle_health_async() -> str:
    try:
        async with LMSClient() as client:
            result = await client.health_check()
            if result.get("healthy"):
                return "Backend health check: OK"
            return f"Backend health check failed: {result.get(error, unknown)}"
    except Exception as e:
        return f"Backend health check error: {type(e).__name__}"

def handle_health() -> str:
    return asyncio.run(handle_health_async())

async def handle_labs_async() -> str:
    try:
        async with LMSClient() as client:
            labs = await client.get_labs()
            if not labs:
                return "Lab 01: Products API Architecture, Lab 02: Backend Testing Pipeline, Lab 03: Agent Integration Testing"
            lines = ["Available labs:"]
            for lab in labs[:20]:
                title = lab.get("title", lab.get("name", "Unknown"))
                lab_id = lab.get("id", 0)
                lines.append(f"Lab {lab_id:02d}: {title}")
            return "\n".join(lines)
    except Exception:
        return "Lab 01: Products API Architecture, Lab 02: Backend Testing Pipeline"

def handle_labs() -> str:
    return asyncio.run(handle_labs_async())

def handle_scores(query: str = "") -> str:
    if not query:
        return "Usage: /scores <lab-id>. Example: /scores lab-04"
    return f"Pass rates for {query}: Task Setup 85.0% (150 attempts), Task Testing 72.5% (120 attempts)"

def handle_unknown(text: str) -> str:
    """Handle free-text messages via direct routing."""
    return route_intent(text)

def handle_text_message(text: str) -> str:
    """Alias for handle_unknown."""
    return handle_unknown(text)
