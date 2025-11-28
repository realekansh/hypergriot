# bot/handlers/welcome.py
from pyrogram import Client, filters
from bot.commands import command
from db import models
from db.session import SessionLocal
from typing import Optional

# Helpers to manage ChatSettings.settings['welcome']
def _get_settings(chat_id: int) -> dict:
    with SessionLocal() as db:
        cs = db.query(models.ChatSettings).filter(models.ChatSettings.chat_id == chat_id).first()
        if not cs:
            return {}
        s = cs.settings or {}
        return s

def _set_settings(chat_id: int, settings: dict):
    with SessionLocal() as db:
        cs = db.query(models.ChatSettings).filter(models.ChatSettings.chat_id == chat_id).first()
        if not cs:
            cs = models.ChatSettings(chat_id=chat_id, settings=settings)
            db.add(cs)
        else:
            cs.settings = settings
        db.commit()

@command("setwelcome", category="Community", usage="setwelcome <text>", short="Set welcome message (template)", admin_only=True)
async def setwelcome(client: Client, message):
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply_text("Usage: /setwelcome <text>")
    text = parts[1].strip()
    s = _get_settings(message.chat.id)
    s["welcome"] = text
    _set_settings(message.chat.id, s)
    await message.reply_text("Welcome message set.")

@command("welcome", category="Community", usage="welcome", short="Show current welcome", admin_only=False)
async def show_welcome(client: Client, message):
    s = _get_settings(message.chat.id)
    txt = s.get("welcome")
    if not txt:
        return await message.reply_text("No welcome message configured.")
    await message.reply_text(txt)

@command("welcomeon", category="Community", usage="welcomeon", short="Enable welcome messages", admin_only=True)
async def welcome_on(client: Client, message):
    s = _get_settings(message.chat.id)
    s["welcome_enabled"] = True
    _set_settings(message.chat.id, s)
    await message.reply_text("Welcome messages enabled.")

@command("welcomeoff", category="Community", usage="welcomeoff", short="Disable welcome messages", admin_only=True)
async def welcome_off(client: Client, message):
    s = _get_settings(message.chat.id)
    s["welcome_enabled"] = False
    _set_settings(message.chat.id, s)
    await message.reply_text("Welcome messages disabled.")

# send welcome on join
@Client.on_message(filters.new_chat_members)
async def on_member_join(client: Client, message):
    chat_id = message.chat.id
    s = _get_settings(chat_id)
    if not s.get("welcome_enabled"):
        return
    tmpl = s.get("welcome")
    if not tmpl:
        return
    for m in message.new_chat_members:
        # simple templating
        text = tmpl.replace("{user}", f"{m.mention if hasattr(m, 'mention') else m.first_name}")
        text = text.replace("{user_name}", m.first_name or "")
        text = text.replace("{chat}", message.chat.title or "")
        await message.reply_text(text)
