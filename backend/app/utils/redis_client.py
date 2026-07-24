import redis.asyncio as redis

from app.config import settings

redis_client = redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,  
)


async def get_redis() -> redis.Redis:
    
    return redis_client


async def close_redis_connection():
    await redis_client.close()