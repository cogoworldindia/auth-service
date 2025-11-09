import httpx
from typing import Optional


async def async_post(url: str, json: dict = None, headers: dict = None, timeout: int = 30) -> Optional[httpx.Response]:
    """
    Makes an async POST request using httpx, with error handling.
    Returns the httpx.Response object or None if failed.
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=json, headers=headers)
            return response
    except httpx.RequestError as e:
        print(f"[HTTP ERROR] {e}")
        return None
