# bot/handlers/rules.py
from pyrogram import Client, filters
from bot.commands import command
from db import models
from db.session import SessionLocal

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

@command("setrules", category="Community", usage="setrules <text>", short="Set rules text", admin_only=True)
async def setrules(client: Client, message):
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply_text("Usage: /setrules <text>")
    text = parts[1].strip()
    s = _get_settings(message.chat.id)
    s["rules"] = text
    _set_settings(message.chat.id, s)
    await message.reply_text("Rules saved.")

@command("rules", category="Community", usage="rules", short="Show group rules", admin_only=False)
async def show_rules(client: Client, message):
    s = _get_settings(message.chat.id)
    rules = s.get("rules")
    if not rules:
        return await message.reply_text("No rules set for this chat.")
    await message.reply_text(rules)
