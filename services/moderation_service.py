# services/moderation_service.py
# Implements actions (ban, temp ban, mute) and writes modlog entries.

import asyncio
from db.session import SessionLocal
from db import models
from datetime import datetime, timezone, timedelta
from typing import Optional, Any, Dict

async def is_user_admin(client, chat_id: int, user_id: int) -> bool:
    try:
        mem = await client.get_chat_member(chat_id, user_id)
        return mem.status in ("administrator", "creator")
    except Exception:
        return False

async def resolve_user_to_id(client, target, chat_id: int) -> int:
    # accepts numeric id, @username or user id
    if isinstance(target, int):
        return target
    if isinstance(target, str) and target.startswith("@"):
        u = await client.get_users(target)
        return u.id
    # assume numeric-looking str
    if isinstance(target, str) and target.isdigit():
        return int(target)
    # fallback: raise
    raise ValueError("Could not resolve target")

async def _write_modlog(chat_id: int, moderator_id: int, action: str, target_user: Any, reason: Optional[str]=None, metadata: Optional[Dict]=None):
    with SessionLocal() as db:
        m = models.ModLog(
            chat_id=chat_id,
            moderator_id=moderator_id,
            action=action,
            target_user=target_user,
            reason=reason,
            metadata_json=metadata or {},
            created_at=datetime.now(timezone.utc)
        )
        db.add(m)
        db.commit()
        db.refresh(m)
        return m.id

async def ban(client, chat_id: int, target_user: int, moderator_id: int, reason: Optional[str]=None, silent: bool=False):
    # perform ban via pyrogram
    try:
        await client.ban_chat_member(chat_id, target_user)
    except Exception as e:
        return {"ok": False, "message": f"Failed to ban: {e}"}
    log_id = await _write_modlog(chat_id, moderator_id, "BAN", target_user, reason)
    return {"ok": True, "id": log_id, "message": "User banned."}

async def temp_ban(client, chat_id: int, target_user: int, seconds: int, moderator_id: int, reason: Optional[str]=None):
    # we ban now and schedule unban
    res = await ban(client, chat_id, target_user, moderator_id, reason)
    if not res.get("ok"):
        return res
    # schedule unban in background (simple asyncio Task)
    async def unban_later():
        await asyncio.sleep(seconds)
        try:
            await client.unban_chat_member(chat_id, target_user)
            await _write_modlog(chat_id, 0, "TUNBAN", target_user, f"Auto unban after {seconds}s")
        except Exception:
            pass
    asyncio.create_task(unban_later())
    return {"ok": True, "message": f"User temp-banned for {seconds} seconds."}

# same approach for mute/kick (not implemented here, mimic ban pattern)
