import asyncio
import hashlib
import json
from typing import List, Dict

from redis import asyncio as aioredis

from src.app.core.config import Settings


async def init_redis(settings):
    redis_url = f"redis://{settings.redis_host}:6379/{settings.redis_db_name}"
    redis = aioredis.from_url(
        redis_url,
        encoding="utf-8",
        decode_responses=True
    )
    return redis





async def get_redis(settings: Settings):
    redis = None

    if redis is None:
        redis = await init_redis(settings)
    return redis


def get_cache_key(url: str) -> str:
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return f"media:{url_hash}"


async def get_cached_media(url: str, settings: Settings) -> List[Dict] | None:
    redis_client = await get_redis(settings)
    cache_key = await asyncio.to_thread(get_cache_key, url)
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        try:
            return json.loads(cached_data)
        except json.JSONDecodeError:
            return None
    return None


async def cache_media(url: str, media_list: List[Dict], settings: Settings):
    redis_client = await get_redis(settings)
    cache_key = await asyncio.to_thread(get_cache_key, url)
    cache_data = json.dumps(media_list)
    await redis_client.setex(cache_key, 10800, cache_data)


