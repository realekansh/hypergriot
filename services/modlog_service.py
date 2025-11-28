import os
from db import models
from db.session import SessionLocal
from datetime import datetime, timezone
from typing import Optional

def create_modlog_record(chat_id: int, moderator_id: Optional[int], action: str, target_user: Optional[int], reason: Optional[str], metadata: Optional[dict] = None) -> str:
    """
    Insert modlog row and return the log_id (uuid string).
    """
    with SessionLocal() as db:
        ml = models.ModLog(
            chat_id=chat_id,
            moderator_id=moderator_id,
            action=action,
            target_user=target_user,
            reason=reason,
            metadata=metadata or {},
        )
        db.add(ml)
        db.commit()
        db.refresh(ml)
        return str(ml.id)

def send_modlog(client, chat_id: int, log_id: str):
    """
    Send a compact modlog message to the configured modlog channel for the chat.
    Reads chat_settings.settings.modlog_chat if set, otherwise looks at MODLOG_CHAT_ID env.
    """
    # fetch the modlog row
    with SessionLocal() as db:
        ml = db.query(models.ModLog).filter(models.ModLog.id == log_id).first()
        if not ml:
            return
        # find destination
        cs = db.query(models.ChatSettings).filter(models.ChatSettings.chat_id == chat_id).first()
        modlog_chat = None
        if cs and cs.settings and isinstance(cs.settings, dict):
            modlog_chat = cs.settings.get("modlog_chat")
        if not modlog_chat:
            modlog_chat = os.getenv("MODLOG_CHAT_ID")

    # build message text
    txt_lines = [
        f"modlog id: {log_id}",
        f"chat: {chat_id}",
        f"action: {ml.action}",
        f"target: {ml.target_user or '-'}",
        f"moderator: {ml.moderator_id or 'bot/auto'}",
        f"reason: {ml.reason or '-'}",
        f"timestamp: {ml.created_at.isoformat()}",
    ]
    txt = "\\n".join(txt_lines)

    if not modlog_chat:
        # no modlog destination configured
        return

    try:
        client.send_message(modlog_chat, txt)
    except Exception:
        # fail silently; admins can check DB if needed
        pass
