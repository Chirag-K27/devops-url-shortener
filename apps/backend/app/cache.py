import redis.asyncio as redis
from app.config import get_settings

settings = get_settings()

redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def get_cached_url(short_code: str) -> str | None:
    """Get original URL from Redis cache."""
    return await redis_client.get(f"url:{short_code}")


async def set_cached_url(short_code: str, original_url: str) -> None:
    """Cache a URL mapping in Redis with TTL."""
    await redis_client.set(
        f"url:{short_code}",
        original_url,
        ex=settings.CACHE_TTL,
    )


async def increment_click_count(short_code: str) -> None:
    """Increment click count in Redis for real-time stats."""
    await redis_client.incr(f"clicks:{short_code}")


async def get_click_count(short_code: str) -> int:
    """Get click count from Redis."""
    count = await redis_client.get(f"clicks:{short_code}")
    return int(count) if count else 0


async def check_redis_health() -> bool:
    """Check if Redis is reachable."""
    try:
        await redis_client.ping()
        return True
    except Exception:
        return False
