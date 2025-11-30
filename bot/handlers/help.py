# bot/handlers/help.py
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.commands import registry, commands_in_category
from bot.commands import command

TOP_HELP_TEXT = "\\n".join([
    "HyperGriot - Help",
    "",
    "About the bot",
    "HyperGriot is a moderation and community management assistant for Telegram. It provides moderation commands, filters, welcome and verification flows, anti-raid protection, and reporting. The bot is configurable per chat and logs actions to the configured modlog.",
    "",
    "How to use the bot",
    "1. Admins configure the bot using /settings and /setmodlog.",
    "2. Use moderation commands (ban, mute, kick, purge) as replies or with usernames/IDs.",
    "3. Create filters and notes with /filter and /save.",
    "4. Enable automated features (flood, anti-raid, smart moderation) if desired.",
    "",
    "Select a topic using the buttons below for a concise command list, or use /help <topic> for details.",
])

def help_keyboard():
    keyboard = [
        [InlineKeyboardButton("About", callback_data="help:about"),
         InlineKeyboardButton("How to use", callback_data="help:usage")],
        [InlineKeyboardButton("Moderation", callback_data="help:moderation"),
         InlineKeyboardButton("Community", callback_data="help:community")],
        [InlineKeyboardButton("Anti-spam", callback_data="help:antispam"),
         InlineKeyboardButton("Settings", callback_data="help:settings")],
        [InlineKeyboardButton("Full docs", callback_data="help:fulldocs"),
         InlineKeyboardButton("Close", callback_data="help:close")],
    ]
    return InlineKeyboardMarkup(keyboard)

def render_category(category_name: str):
    lines = [f"{category_name} commands", ""]
    for cmd in commands_in_category(category_name):
        lines.append(f"{cmd['usage']:30} {cmd['short']}")
    lines.append("")
    lines.append("Use /help <topic> for details or press Full docs to receive full documentation by DM.")
    return "\\n".join(lines)

@command("help", category="Misc", usage="help [topic]", short="Show help pages", admin_only=False)
async def help_cmd(client: Client, message):
    text = message.text or ""
    parts = text.split(maxsplit=1)
    if len(parts) > 1:
        topic = parts[1].strip().lower()
        # try categories
        cats = {"moderation":"Moderation","community":"Community","antispam":"Anti-spam","settings":"Settings"}
        for k,v in cats.items():
            if topic == k or topic.replace("-", "") == k.replace("-", ""):
                await message.reply_text(render_category(v))
                return
        # try command name
        from bot.commands import find_by_name
        cmd = find_by_name(topic)
        if cmd:
            out = "\\n".join(["Command help: " + cmd["name"], "", "Usage: " + cmd["usage"], "", cmd["short"]])
            await message.reply_text(out)
            return
        await message.reply_text("No help found for that topic.")
        return

    await message.reply_text(TOP_HELP_TEXT, reply_markup=help_keyboard())

@Client.on_callback_query(filters.regex(r"^help:"))
async def help_cb(client, cq):
    data = cq.data  # e.g., "help:moderation"
    parts = data.split(":")
    if parts[1] == "close":
        try:
            await cq.message.delete()
        except:
            pass
        await cq.answer()
        return

    if parts[1] == "fulldocs":
        try:
            # render full doc from registry
            sections = {}
            for cmd in registry:
                sections.setdefault(cmd["category"], []).append(cmd)
            doc_lines = ["HyperGriot - Full documentation", ""]
            for cat, cmds in sections.items():
                doc_lines.append(cat)
                for c in cmds:
                    doc_lines.append(f"{c['usage']:30} {c['short']}")
                doc_lines.append("")
            full = "\\n".join(doc_lines)
            await client.send_message(cq.from_user.id, full)
            await cq.answer("Full docs sent by DM")
        except Exception:
            await cq.answer("Could not send DM. You may have DMs disabled.")
        return

    mapping = {"moderation":"Moderation","community":"Community","antispam":"Anti-spam","settings":"Settings"}
    key = parts[1]
    if key in mapping:
        text = render_category(mapping[key])
        await cq.message.edit_text(text, reply_markup=help_keyboard())
        await cq.answer()
        return

    await cq.answer()
