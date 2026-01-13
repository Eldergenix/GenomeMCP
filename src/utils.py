import httpx
import asyncio
from typing import Dict, Any

async def fetch_with_retry(client: httpx.AsyncClient, url: str, params: Dict[str, Any], retries: int = 3) -> httpx.Response:
    """Execute GET request with rate-limit handling (shared utility)."""
    for i in range(retries):
        response = await client.get(url, params=params)
        if response.status_code == 429:
            # NCBI rate limit: 3 requests/sec without API key.
            # Wait exponentially: 0.5s, 1.5s, 4.5s
            wait_time = 0.5 * (3 ** i)
            await asyncio.sleep(wait_time)
            continue
        # Don't raise here, let caller handle non-429s or raise manually
        return response
    # Final attempt
    return await client.get(url, params=params)
