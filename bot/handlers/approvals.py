# bot/handlers/approvals.py
from pyrogram import Client, filters
from bot.commands import command
from db.session import SessionLocal
from db import models
from typing import List

# We'll store approvals in ChatSettings.settings['approvals'] dict: {'enabled': bool, 'pending': [user_id,...], 'approved': [user_id,...]}

def _get_settings(chat_id: int) -> dict:
    with SessionLocal() as db:
        cs = db.query(models.ChatSettings).filter(models.ChatSettings.chat_id == chat_id).first()
        return cs.settings or {} if cs else {}

def _set_settings(chat_id: int, settings: dict):
    with SessionLocal() as db:
        cs = db.query(models.ChatSettings).filter(models.ChatSettings.chat_id == chat_id).first()
        if not cs:
            cs = models.ChatSettings(chat_id=chat_id, settings=settings)
            db.add(cs)
        else:
            cs.settings = settings
        db.commit()

@command("approvals", category="Community", usage="approvals on|off", short="Enable/disable join approvals", admin_only=True)
async def approvals_toggle(client: Client, message):
    parts = (message.text or "").split()
    if len(parts) < 2 or parts[1].lower() not in ("on","off"):
        return await message.reply_text("Usage: /approvals on|off")
    s = _get_settings(message.chat.id)
    approvals = s.get("approvals", {})
    approvals["enabled"] = parts[1].lower() == "on"
    approvals.setdefault("pending", [])
    approvals.setdefault("approved", [])
    s["approvals"] = approvals
    _set_settings(message.chat.id, s)
    await message.reply_text(f"Approvals {'enabled' if approvals['enabled'] else 'disabled'}.")

@command("pending", category="Community", usage="pending", short="List pending joiners", admin_only=True)
async def pending_list(client: Client, message):
    s = _get_settings(message.chat.id)
    approvals = s.get("approvals", {})
    pending = approvals.get("pending", [])
    if not pending:
        return await message.reply_text("No pending joiners.")
    text = "Pending joiners:\\n" + "\\n".join(str(x) for x in pending)
    await message.reply_text(text)

@command("approve", category="Community", usage="approve <user_id>", short="Approve a pending joiner", admin_only=True)
async def approve_cmd(client: Client, message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        return await message.reply_text("Usage: /approve <user_id>")
    uid = int(parts[1])
    s = _get_settings(message.chat.id)
    approvals = s.get("approvals", {})
    pending = approvals.get("pending", [])
    if uid not in pending:
        return await message.reply_text("User not in pending.")
    pending.remove(uid)
    approved = approvals.get("approved", [])
    if uid not in approved:
        approved.append(uid)
    approvals["pending"] = pending
    approvals["approved"] = approved
    s["approvals"] = approvals
    _set_settings(message.chat.id, s)
    try:
        await client.unban_chat_member(message.chat.id, uid)  # unrestrict / allow to send (best-effort)
    except:
        pass
    await message.reply_text(f"User {uid} approved.")

@command("reject", category="Community", usage="reject <user_id> [reason]", short="Reject a pending joiner", admin_only=True)
async def reject_cmd(client: Client, message):
    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 2:
        return await message.reply_text("Usage: /reject <user_id> [reason]")
    uid = int(parts[1])
    reason = parts[2] if len(parts) > 2 else None
    s = _get_settings(message.chat.id)
    approvals = s.get("approvals", {})
    pending = approvals.get("pending", [])
    if uid in pending:
        pending.remove(uid)
    approvals["pending"] = pending
    s["approvals"] = approvals
    _set_settings(message.chat.id, s)
    try:
        await client.kick_chat_member(message.chat.id, uid)
    except:
        pass
    await message.reply_text(f"User {uid} rejected. Reason: {reason or '-'}")
