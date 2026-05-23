import redis.asyncio as aioredis
from app.core.config import settings

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


async def close_redis():
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


async def check_rate_limit(user_id: int, redis: aioredis.Redis) -> tuple[bool, int]:
    """
    Возвращает (разрешено, осталось_запросов).
    Бесплатный лимит: 5 запросов в день на user_id.
    """
    key = f"rate:{user_id}:{_today()}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 86400)  # сбрасывается в полночь

    limit = settings.free_requests_per_day
    remaining = max(0, limit - count)
    allowed = count <= limit
    return allowed, remaining


def _today() -> str:
    from datetime import date
    return date.today().isoformat()