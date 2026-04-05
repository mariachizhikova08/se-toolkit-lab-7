"""LLM client for tool calling and intent routing."""
import httpx
import json
from typing import Optional, List, Dict, Any
from config import settings

class LLMClient:
    """Client for LLM API with tool calling support."""
    
    def __init__(self, base_url: str = None, api_key: str = None, model: str = None):
        self.base_url = base_url or settings.LLM_API_BASE_URL
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or "qwen-coder"
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=120)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return all 9 backend endpoints as LLM tool schemas."""
        return [
            {"type": "function", "function": {"name": "get_items", "description": "List all available labs and tasks in the LMS", "parameters": {"type": "object", "properties": {}, "required": []}}},
            {"type": "function", "function": {"name": "get_learners", "description": "Get list of enrolled students and groups", "parameters": {"type": "object", "properties": {}, "required": []}}},
            {"type": "function", "function": {"name": "get_scores", "description": "Get score distribution for a specific lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
            {"type": "function", "function": {"name": "get_pass_rates", "description": "Get per-task average scores for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
            {"type": "function", "function": {"name": "get_timeline", "description": "Get submission timeline for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
            {"type": "function", "function": {"name": "get_groups", "description": "Get per-group scores for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
            {"type": "function", "function": {"name": "get_top_learners", "description": "Get top N learners by score for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}, "limit": {"type": "integer", "default": 5}}, "required": ["lab"]}}},
            {"type": "function", "function": {"name": "get_completion_rate", "description": "Get completion rate percentage for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
            {"type": "function", "function": {"name": "trigger_sync", "description": "Trigger data sync from autochecker", "parameters": {"type": "object", "properties": {}, "required": []}}},
        ]

    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool by calling the backend API."""
        from services.lms_client import LMSClient
        async with LMSClient() as backend:
            if tool_name == "get_items":
                return await backend.get_labs()
            elif tool_name == "get_learners":
                resp = await backend._client.get(f"{backend.base_url}/learners/", headers={"Authorization": f"Bearer {backend.api_key}"})
                return resp.json() if resp.status_code == 200 else []
            elif tool_name == "get_scores":
                resp = await backend._client.get(f"{backend.base_url}/analytics/scores/", params={"lab": args.get("lab")}, headers={"Authorization": f"Bearer {backend.api_key}"})
                return resp.json() if resp.status_code == 200 else {}
            elif tool_name == "get_pass_rates":
                result = await backend.get_pass_rates(args.get("lab", ""))
                return result.get("tasks", []) if "tasks" in result else []
            elif tool_name == "get_timeline":
                resp = await backend._client.get(f"{backend.base_url}/analytics/timeline/", params={"lab": args.get("lab")}, headers={"Authorization": f"Bearer {backend.api_key}"})
                return resp.json() if resp.status_code == 200 else []
            elif tool_name == "get_groups":
                resp = await backend._client.get(f"{backend.base_url}/analytics/groups/", params={"lab": args.get("lab")}, headers={"Authorization": f"Bearer {backend.api_key}"})
                return resp.json() if resp.status_code == 200 else []
            elif tool_name == "get_top_learners":
                resp = await backend._client.get(f"{backend.base_url}/analytics/top-learners/", params={"lab": args.get("lab"), "limit": args.get("limit", 5)}, headers={"Authorization": f"Bearer {backend.api_key}"})
                return resp.json() if resp.status_code == 200 else []
            elif tool_name == "get_completion_rate":
                resp = await backend._client.get(f"{backend.base_url}/analytics/completion-rate/", params={"lab": args.get("lab")}, headers={"Authorization": f"Bearer {backend.api_key}"})
                return resp.json() if resp.status_code == 200 else {}
            elif tool_name == "trigger_sync":
                resp = await backend._client.post(f"{backend.base_url}/pipeline/sync", headers={"Authorization": f"Bearer {backend.api_key}"})
                return {"status": "synced" if resp.status_code == 200 else "failed"}
            else:
                return {"error": f"Unknown tool: {tool_name}"}

    async def chat_with_tools(self, messages: List[Dict[str, Any]], max_turns: int = 3) -> str:
        """Main loop: send messages + tools to LLM, execute tool calls, feed results back."""
        import sys
        for turn in range(max_turns):
            payload = {"model": self.model, "messages": messages, "tools": self.get_tool_definitions(), "tool_choice": "auto"}
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            try:
                resp = await self._client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"[llm] Error: {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)
                return f"Sorry, I couldn't reach the AI service. Please try again later."

            choice = data.get("choices", [{}])[0].get("message", {})
            if "content" in choice and choice.get("content") and not choice.get("tool_calls"):
                return choice["content"]
            tool_calls = choice.get("tool_calls", [])
            if tool_calls:
                messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls})
                for tc in tool_calls:
                    func = tc.get("function", {})
                    tool_name = func.get("name")
                    args = json.loads(func.get("arguments", "{}")) if func.get("arguments") else {}
                    print(f"[tool] LLM called: {tool_name}({args})", file=sys.stderr)
                    result = await self.execute_tool(tool_name, args)
                    print(f"[tool] Result: {len(result) if isinstance(result, (list, dict)) else 'ok'} items", file=sys.stderr)
                    messages.append({"role": "tool", "tool_call_id": tc.get("id"), "name": tool_name, "content": json.dumps(result, ensure_ascii=False) if not isinstance(result, str) else result})
                print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)
                continue
            if choice.get("content"):
                return choice["content"]
            return "I'm not sure how to help with that. Try asking about labs, scores, or students!"
        return "I reached the maximum number of steps. Here's what I found so far."
