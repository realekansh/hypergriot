import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

from db.session import SessionLocal
from db import models

from services.modlog_service import create_modlog_record, send_modlog

def gen_action_id() -> str:
    return str(uuid.uuid4())

def parse_duration_str(duration: Optional[str]) -> Optional[int]:
    if not duration:
        return None
    try:
        from bot.utils import parse_time_to_seconds
        return parse_time_to_seconds(duration)
    except Exception:
        return None

async def perform_action(
    client,
    chat_id: int,
    issuer_id: Optional[int],
    target_user_id: int,
    action: str,
    duration: Optional[str] = None,
    reason: Optional[str] = None,
    silent: bool = False,
) -> Dict[str, Any]:
    """
    Centralized performer for actions. Async version that awaits pyrogram client calls.
    Returns dict {action_id, ok, error}
    """
    action_id = gen_action_id()
    now = datetime.now(timezone.utc)

    seconds = None
    if action.startswith("t") and duration:
        seconds = parse_duration_str(duration)
    until_date = None
    if seconds:
        until_date = now + timedelta(seconds=seconds)

    res = {"action_id": action_id, "ok": False, "error": None}
    try:
        if action in ("ban", "tban"):
            await client.ban_chat_member(chat_id, target_user_id, until_date=until_date)
            with SessionLocal() as db:
                b = models.Ban(
                    chat_id=chat_id,
                    user_id=target_user_id,
                    type="TEMP" if action == "tban" else "PERM",
                    reason=reason,
                    moderator_id=issuer_id,
                    start_ts=now,
                    end_ts=until_date,
                    active=True,
                )
                db.add(b)
                db.commit()
        elif action in ("unban",):
            await client.unban_chat_member(chat_id, target_user_id)
            with SessionLocal() as db:
                db.query(models.Ban).filter(
                    models.Ban.chat_id == chat_id,
                    models.Ban.user_id == target_user_id,
                    models.Ban.active == True,
                ).update({"active": False})
                db.commit()
        elif action in ("mute", "tmute"):
            from pyrogram.types import ChatPermissions
            perms = ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
            )
            await client.restrict_chat_member(chat_id, target_user_id, permissions=perms, until_date=until_date)
            with SessionLocal() as db:
                m = models.Mute(
                    chat_id=chat_id,
                    user_id=target_user_id,
                    type="TEMP" if action == "tmute" else "PERM",
                    mute_mode="FULL",
                    reason=reason,
                    moderator_id=issuer_id,
                    start_ts=now,
                    end_ts=until_date,
                    active=True,
                )
                db.add(m)
                db.commit()
        elif action in ("unmute",):
            # unrestrict: allow sending messages (careful: this restores general rights)
            from pyrogram.types import ChatPermissions
            perms = ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False,
            )
            await client.restrict_chat_member(chat_id, target_user_id, permissions=perms)
            with SessionLocal() as db:
                db.query(models.Mute).filter(
                    models.Mute.chat_id == chat_id,
                    models.Mute.user_id == target_user_id,
                    models.Mute.active == True,
                ).update({"active": False})
                db.commit()
        elif action in ("kick",):
            await client.ban_chat_member(chat_id, target_user_id)
            await client.unban_chat_member(chat_id, target_user_id, only_if_banned=True)
        else:
            res["error"] = f"Unknown action: {action}"
            return res

        meta = {"reason": reason, "duration": duration}
        log_id = create_modlog_record(chat_id=chat_id, moderator_id=issuer_id, action=action.upper(), target_user=target_user_id, reason=reason, metadata=meta)
        try:
            send_modlog(client, chat_id, log_id)
        except Exception:
            pass

        res["ok"] = True
        res["action_id"] = log_id
        return res

    except Exception as e:
        res["error"] = str(e)
        return res
