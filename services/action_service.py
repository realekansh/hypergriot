import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

from db.session import SessionLocal
from db import models

from services.modlog_service import create_modlog_record, send_modlog

def gen_action_id() -> str:
    return str(uuid.uuid4())

def parse_duration_str(duration: Optional[str]) -> Optional[int]:
    """
    Accepts strings like '10m', '1h30m' and returns seconds.
    Uses utils.parse_time_to_seconds if available.
    """
    if not duration:
        return None
    try:
        from bot.utils import parse_time_to_seconds
        return parse_time_to_seconds(duration)
    except Exception:
        return None

def perform_action(
    client,
    chat_id: int,
    issuer_id: int,
    target_user_id: int,
    action: str,
    duration: Optional[str] = None,
    reason: Optional[str] = None,
    silent: bool = False,
) -> Dict[str, Any]:
    """
    Centralized performer for actions. This function does:
     - basic validation (permissions/hierarchy checks are stubs here)
     - calls Telegram API via provided client
     - persists modlog and ban/mute records in DB
     - returns {'action_id': str, 'ok': bool, 'error': Optional[str]}
    Note: client should be an instance of pyrogram.Client.
    """

    action_id = gen_action_id()
    now = datetime.now(timezone.utc)

    # basic permission/hierarchy checks (TODO: implement fully)
    # e.g., check issuer is admin and issuer outranks target
    # For now we assume caller already validated this.

    # Parse duration if temporary
    seconds = None
    if action.startswith("t") and duration:
        seconds = parse_duration_str(duration)
    until_date = None
    if seconds:
        until_date = now + timedelta(seconds=seconds)

    res = {"action_id": action_id, "ok": False, "error": None}
    try:
        # map basic actions -> Telegram calls
        if action in ("ban", "tban"):
            # ban_chat_member supports until_date for temporary bans
            client.ban_chat_member(chat_id, target_user_id, until_date=until_date)
            # create DB ban record
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
            client.unban_chat_member(chat_id, target_user_id)
            with SessionLocal() as db:
                # mark active bans inactive for this user in chat
                db.query(models.Ban).filter(
                    models.Ban.chat_id == chat_id,
                    models.Ban.user_id == target_user_id,
                    models.Ban.active == True,
                ).update({"active": False})
                db.commit()
        elif action in ("mute", "tmute"):
            # use restrict_chat_member
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
            client.restrict_chat_member(chat_id, target_user_id, permissions=perms, until_date=until_date)
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
        elif action in ("kick",):
            # implement as ban + unban to allow rejoin
            client.ban_chat_member(chat_id, target_user_id)
            client.unban_chat_member(chat_id, target_user_id, only_if_banned=True)
        else:
            res["error"] = f"Unknown action: {action}"
            return res

        # create modlog entry
        meta = {"reason": reason, "duration": duration}
        log_id = create_modlog_record(chat_id=chat_id, moderator_id=issuer_id, action=action.upper(), target_user=target_user_id, reason=reason, metadata=meta)
        # send modlog message (non-blocking; may raise)
        try:
            send_modlog(client, chat_id, log_id)
        except Exception:
            pass

        res["ok"] = True
        return res

    except Exception as e:
        res["error"] = str(e)
        return res
