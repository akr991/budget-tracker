import httpx

from app.core.config import get_settings


async def fetch_live_gold_price_inr_per_gram() -> float | None:
    settings = get_settings()
    if not settings.gold_price_api_url:
        return None

    headers = {}
    if settings.gold_price_api_key:
        headers["Authorization"] = f"Bearer {settings.gold_price_api_key}"

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(settings.gold_price_api_url, headers=headers)
        response.raise_for_status()
        payload = response.json()

    if isinstance(payload, dict):
        if "price_per_gram" in payload:
            return float(payload["price_per_gram"])
        if "price" in payload:
            return float(payload["price"])
    return None
