import aioredis
import os
import json
from typing import Optional

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

async def get_redis():
    return await aioredis.from_url(REDIS_URL)

async def incr_message_count(chat_id: int, user_id: int, window: int = 10) -> int:
    """
    Increment per-user counter with TTL=window seconds.
    Returns the current count.
    """
    r = await get_redis()
    key = f"flood:chat:{chat_id}:user:{user_id}"
    cnt = await r.incr(key)
    if cnt == 1:
        await r.expire(key, window)
    return int(cnt)

async def set_cooldown(chat_id: int, user_id: int, cooldown: int = 60):
    r = await get_redis()
    key = f"flood:cooldown:{chat_id}:{user_id}"
    await r.set(key, "1", ex=cooldown)

async def check_cooldown(chat_id: int, user_id: int) -> bool:
    r = await get_redis()
    key = f"flood:cooldown:{chat_id}:{user_id}"
    val = await r.get(key)
    return bool(val)

async def get_settings(chat_id: int) -> dict:
    """
    Placeholder: in production read from DB/chat_settings and cache.
    """
    # default settings
    return {"enabled": False, "threshold": 20, "window": 10, "action": "warn", "cooldown": 60}
