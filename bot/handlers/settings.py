# bot/handlers/settings.py
from pyrogram import Client, filters
from bot.commands import command
from db import models
from db.session import SessionLocal
import json
import os

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

@command("setmodlog", category="Settings", usage="setmodlog <chat_id_or_channel>", short="Set modlog destination", admin_only=True)
async def set_modlog(client: Client, message):
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply_text("Usage: /setmodlog <chat_id_or_channel>")
    dest = parts[1].strip()
    s = _get_settings(message.chat.id)
    s["modlog_chat"] = dest
    _set_settings(message.chat.id, s)
    await message.reply_text("Modlog destination saved.")

@command("settings", category="Settings", usage="settings", short="Show chat settings", admin_only=True)
async def show_settings(client: Client, message):
    s = _get_settings(message.chat.id)
    if not s:
        return await message.reply_text("No settings configured.")
    # show a compact JSON view
    out = json.dumps(s, indent=2)
    await message.reply_text("Chat settings:\\n" + out)
