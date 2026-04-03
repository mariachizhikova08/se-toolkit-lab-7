"""LMS API client — pure HTTP logic, no Telegram dependency."""
import httpx
from typing import Optional
from config import settings

class LMSClientError(Exception):
    """Base exception for LMS client errors."""
    pass

class LMSClient:
    """Client for the LMS backend API."""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or settings.LMS_API_BASE_URL
        self.api_key = api_key or settings.LMS_API_KEY
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
    
    async def health_check(self) -> dict:
        """Check backend health via GET /items/."""
        try:
            resp = await self._client.get(
                f"{self.base_url}/items/",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            resp.raise_for_status()
            items = resp.json()
            count = len(items) if isinstance(items, list) else 0
            return {"healthy": True, "item_count": count}
        except httpx.ConnectError:
            return {"healthy": False, "error": f"connection refused ({self.base_url}). Check that the services are running."}
        except httpx.HTTPStatusError as e:
            return {"healthy": False, "error": f"HTTP {e.response.status_code}: {e.response.text[:100]}"}
        except Exception as e:
            return {"healthy": False, "error": f"{type(e).__name__}: {str(e)[:100]}"}
    
    async def get_labs(self) -> list[dict]:
        """Get list of labs from GET /items/."""
        try:
            resp = await self._client.get(
                f"{self.base_url}/items/",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            resp.raise_for_status()
            items = resp.json()
            if isinstance(items, list):
                return items
            return []
        except Exception:
            return []
    
    async def get_pass_rates(self, lab_id: str) -> dict:
        """Get pass rates for a lab via GET /analytics/pass-rates/."""
        try:
            resp = await self._client.get(
                f"{self.base_url}/analytics/pass-rates/",
                params={"lab": lab_id},
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            resp.raise_for_status()
            data = resp.json()
            # Адаптация под разный формат ответа
            if isinstance(data, list):
                return {"lab": lab_id, "tasks": data}
            elif isinstance(data, dict) and "tasks" in data:
                return data
            elif isinstance(data, dict):
                return {"lab": lab_id, "tasks": [data]}
            return {"lab": lab_id, "tasks": []}
        except httpx.ConnectError:
            return {"error": f"connection refused ({self.base_url}). Check that the services are running."}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": f"lab '{lab_id}' not found"}
            return {"error": f"HTTP {e.response.status_code}"}
        except Exception as e:
            return {"error": f"{type(e).__name__}: {str(e)[:100]}"}
