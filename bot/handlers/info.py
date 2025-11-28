# bot/handlers/info.py
from pyrogram import Client, filters
from bot.commands import command
from bot.utils import resolve_user
from pyrogram.types import User

@command("id", category="Community", usage="id [reply|@user|id]", short="Show chat/user ids", admin_only=False)
async def id_cmd(client: Client, message):
    # If reply, show replied message id and user id
    if message.reply_to_message:
        m = message.reply_to_message
        lines = [
            f"chat_id: {message.chat.id}",
            f"user_id: {m.from_user.id if m.from_user else 'unknown'}",
            f"message_id: {m.message_id}",
        ]
        return await message.reply_text("\\n".join(lines))
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) > 1:
        target_str = parts[1].strip()
        target = await resolve_user(client, message.chat.id, target_str)
        if not target:
            return await message.reply_text("User not found.")
        await message.reply_text(f"user_id: {target.id}")
    else:
        await message.reply_text(f"chat_id: {message.chat.id}\\nyour user_id: {message.from_user.id}")

@command("info", category="Community", usage="info [@user|id|reply]", short="Show info about user", admin_only=False)
async def info_cmd(client: Client, message):
    # provide simple info: join date not always available; show recent moderation state
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    else:
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) > 1:
            target = await resolve_user(client, message.chat.id, parts[1].strip())
            if not target:
                return await message.reply_text("User not found.")
        else:
            target = message.from_user
    lines = [
        f"user_id: {target.id}",
        f"name: {target.first_name or '-'}",
        f"username: @{target.username if getattr(target, 'username', None) else '-'}",
    ]
    await message.reply_text("\\n".join(lines))

@command("admins", category="Community", usage="admins", short="List chat admins", admin_only=False)
async def admins_cmd(client: Client, message):
    members = []
    try:
        async for m in client.iter_chat_members(message.chat.id, filter="administrators"):
            members.append(f"{m.user.first_name} ({m.user.id})")
    except Exception:
        return await message.reply_text("Failed to fetch admins.")
    if not members:
        return await message.reply_text("No admins found.")
    await message.reply_text("Admins:\\n" + "\\n".join(members))
