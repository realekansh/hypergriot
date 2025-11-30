# bot/handlers/captcha.py
from pyrogram import Client, filters
from bot.commands import command
from services.flood_service import get_redis
from db import models
from db.session import SessionLocal
import uuid
import json
import asyncio

# ChatSettings.settings['captcha'] = {
#   "enabled": bool,
#   "mode": "button"|"math",
#   "ttl": seconds (int)
# }

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

@command("setverify", category="Community", usage="setverify none|button|math", short="Set verification method", admin_only=True)
async def set_verify(client: Client, message):
    parts = (message.text or "").split()
    if len(parts) < 2 or parts[1] not in ("none","button","math"):
        return await message.reply_text("Usage: /setverify none|button|math")
    mode = parts[1]
    s = _get_settings(message.chat.id)
    captcha = s.get("captcha", {})
    captcha["enabled"] = mode != "none"
    captcha["mode"] = mode
    captcha["ttl"] = int(captcha.get("ttl", 120))
    s["captcha"] = captcha
    _set_settings(message.chat.id, s)
    await message.reply_text(f"Verification mode set to {mode}.")

# Helper to generate a callback token and store it in Redis
async def _issue_token(chat_id: int, user_id: int, ttl: int) -> str:
    redis = await get_redis()
    token = str(uuid.uuid4())
    key = f"verify:{chat_id}:{user_id}:{token}"
    payload = {"user_id": user_id}
    await redis.set(key, json.dumps(payload), ex=ttl)
    return token

# On new members, issue verification according to settings
@Client.on_message(filters.new_chat_members)
async def on_join_verification(client: Client, message):
    chat_id = message.chat.id
    s = _get_settings(chat_id)
    captcha = s.get("captcha", {})
    if not captcha.get("enabled"):
        return
    ttl = int(captcha.get("ttl", 120))
    mode = captcha.get("mode", "button")
    for m in message.new_chat_members:
        # If user is a bot or already approved, skip
        if getattr(m, "is_bot", False):
            continue
        token = await _issue_token(chat_id, m.id, ttl)
        if mode == "button":
            cb = f"verify:{chat_id}:{m.id}:{token}"
            try:
                await client.send_message(
                    chat_id,
                    f"New member {m.first_name} — please verify within {ttl} seconds.",
                    reply_markup={
                        "inline_keyboard": [
                            [{"text": "Verify", "callback_data": cb}]
                        ]
                    }
                )
            except Exception:
                try:
                    await client.send_message(m.id, "Please open the group and press Verify to join.")
                except Exception:
                    pass
        elif mode == "math":
            a = 2 + (m.id % 5)
            b = 1 + (m.id % 3)
            answer = str(a + b)
            token_payload = {"user_id": m.id, "answer": answer}
            redis = await get_redis()
            key = f"verify:math:{chat_id}:{m.id}:{token}"
            await redis.set(key, json.dumps(token_payload), ex=ttl)
            try:
                await client.send_message(m.id, f"To verify, reply here with the answer to: {a} + {b}")
            except Exception:
                try:
                    await client.send_message(chat_id, f"{m.first_name}, please check your DM to complete verification.")
                except:
                    pass

# Callback handler for button verification
@Client.on_callback_query(filters.regex(r"^verify:"))
async def verify_cb(client: Client, cq):
    # payload: verify:<chat_id>:<user_id>:<token>
    parts = cq.data.split(":", 3)
    if len(parts) != 4:
        await cq.answer("Invalid verification token.")
        return
    _, chat_id_s, user_id_s, token = parts
    try:
        chat_id = int(chat_id_s); user_id = int(user_id_s)
    except ValueError:
        await cq.answer("Invalid token.")
        return
    redis = await get_redis()
    key = f"verify:{chat_id}:{user_id}:{token}"
    raw = await redis.get(key)
    if not raw:
        await cq.answer("Verification expired or invalid.")
        return
    await redis.delete(key)
    try:
        await client.unban_chat_member(chat_id, user_id)
    except Exception:
        pass
    await cq.answer("Verified")
    try:
        await client.send_message(chat_id, f"User {user_id} verified.")
    except Exception:
        pass
