# bot/handlers/moderation.py
# Minimal handler layer: parse commands and call services.
from pyrogram import Client, filters
from pyrogram.types import Message
from bot.command_registry import COMMANDS
from services import moderation_service, anti_raid
from bot.utils import parse_time_to_seconds
from db.session import SessionLocal
from db import models
import typing

# Helpers
def resolve_target_from_msg(msg: Message):
    # Accept @username, user id, or reply
    if msg.reply_to_message:
        return msg.reply_to_message.from_user.id, msg.reply_to_message
    toks = msg.text.split()
    if len(toks) >= 2:
        tgt = toks[1]
        if tgt.isdigit() or (tgt.startswith("-") and tgt[1:].isdigit()):
            return int(tgt), None
        if tgt.startswith("@"):
            return tgt, None
    return None, None

def take_reason(tokens: list, start=2):
    if len(tokens) > start:
        return " ".join(tokens[start:])
    return None

# Example: /ban
@Client.on_message(filters.command("ban") & filters.group)
async def cmd_ban(client: Client, message: Message):
    # permission check (only admins)
    # you should add robust admin check using services/admins or chat permissions
    user = message.from_user
    # short permission check placeholder:
    if not await moderation_service.is_user_admin(client, message.chat.id, user.id):
        await message.reply_text("Permission denied")
        return

    target, replied = resolve_target_from_msg(message)
    reason = take_reason(message.text.split(), 2)
    if target is None:
        await message.reply_text("Usage: ban <user|reply> [reason]")
        return

    # If username string, resolve to id (service helper)
    target_id = await moderation_service.resolve_user_to_id(client, target, message.chat.id)
    res = await moderation_service.ban(client, message.chat.id, target_id, moderator_id=user.id, reason=reason, silent=False)
    await message.reply_text(res["message"])

# Silent ban
@Client.on_message(filters.command("sban") & filters.group)
async def cmd_sban(client: Client, message: Message):
    if not await moderation_service.is_user_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("Permission denied")
        return
    target, _ = resolve_target_from_msg(message)
    reason = take_reason(message.text.split(), 2)
    if target is None:
        await message.reply_text("Usage: sban <user|reply> [reason]")
        return
    target_id = await moderation_service.resolve_user_to_id(client, target, message.chat.id)
    res = await moderation_service.ban(client, message.chat.id, target_id, moderator_id=message.from_user.id, reason=reason, silent=True)
    # silent: delete the command message if possible
    try:
        await message.delete()
    except Exception:
        pass

# Temporary ban: tban <user> <time> <reason?>
@Client.on_message(filters.command("tban") & filters.group)
async def cmd_tban(client: Client, message: Message):
    if not await moderation_service.is_user_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("Permission denied")
        return
    toks = message.text.split()
    if len(toks) < 3:
        await message.reply_text("Usage: tban <user> <time> [reason]")
        return
    target_raw = toks[1]
    time_raw = toks[2]
    reason = " ".join(toks[3:]) if len(toks) > 3 else None
    target_id = await moderation_service.resolve_user_to_id(client, target_raw, message.chat.id)
    try:
        seconds = parse_time_to_seconds(time_raw)
    except Exception as e:
        await message.reply_text("Invalid time format: " + str(e))
        return
    res = await moderation_service.temp_ban(client, message.chat.id, target_id, seconds, moderator_id=message.from_user.id, reason=reason)
    await message.reply_text(res["message"])

# Flood command (show status)
@Client.on_message(filters.command("flood") & filters.group)
async def cmd_flood(client: Client, message: Message):
    if not await moderation_service.is_user_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("Permission denied")
        return
    status = await anti_raid.get_flood_status(message.chat.id)
    await message.reply_text(status)
