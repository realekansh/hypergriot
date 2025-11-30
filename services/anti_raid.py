# services/anti_raid.py
# Lightweight flood/raid detector using Redis counters and moderation_service callbacks.

import time
import asyncio
from services.flood_service import get_redis
from services import moderation_service

# config defaults (can be made dynamic via DB)
FLOOD_WINDOW = 10  # seconds
DEFAULT_THRESHOLD = 6

async def _key(chat_id: int, user_id: int) -> str:
    return f"flood:{chat_id}:{user_id}"

async def incr_and_check(chat_id: int, user_id: int, threshold: int = DEFAULT_THRESHOLD, window: int = FLOOD_WINDOW):
    """
    Increment user's action counter in chat and check threshold.
    Returns (count, exceeded_bool).
    """
    r = await get_redis()
    k = await _key(chat_id, user_id)
    # Use INCR with EXPIRE
    val = await r.incr(k)
    if val == 1:
        await r.expire(k, window)
    exceeded = val >= threshold
    return val, exceeded

async def get_flood_status(chat_id: int):
    # return settings placeholder
    return f"Flood: threshold={DEFAULT_THRESHOLD}, window={FLOOD_WINDOW}s"

async def process_message_event(client, message):
    """
    Call this for each incoming message:
    - increment user count
    - if threshold exceeded -> perform configured action
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    cnt, exceeded = await incr_and_check(chat_id, user_id)
    if exceeded:
        # default action: mute for 60 seconds
        await moderation_service.temp_ban(client, chat_id, user_id, seconds=60, moderator_id=0, reason="Auto flood protection")
        # optionally reset counter
        r = await get_redis()
        k = f"flood:{chat_id}:{user_id}"
        await r.delete(k)
        return True
    return False
