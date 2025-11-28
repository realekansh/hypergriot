# bot/utils.py
import re
from datetime import timedelta
from typing import Optional
from pyrogram import Client
from pyrogram.types import ChatMember

UNITS = {
    's': 1,
    'sec': 1, 'secs': 1, 'second': 1, 'seconds': 1,
    'm': 60,
    'min': 60, 'mins': 60, 'minute': 60, 'minutes': 60,
    'h': 3600,
    'hr': 3600, 'hour': 3600, 'hours': 3600,
    'd': 86400,
    'day': 86400, 'days': 86400,
    'w': 604800,
    'week': 604800, 'weeks': 604800,
}

TIME_RE = re.compile(r'(\\d+)\\s*([a-zA-Z]+)')

def parse_time_to_seconds(s: str) -> int:
    s = s.strip()
    if not s:
        raise ValueError("Empty time string")
    total = 0
    for match in TIME_RE.finditer(s):
        num_str, unit = match.groups()
        num = 0
        for ch in num_str:
            if not ('0' <= ch <= '9'):
                raise ValueError("Invalid number in time")
            num = num * 10 + (ord(ch) - ord('0'))
        unit = unit.lower()
        if unit not in UNITS:
            raise ValueError(f"Unknown time unit: {unit}")
        total += num * UNITS[unit]
    if total <= 0:
        raise ValueError("Time must be > 0 seconds")
    return total

def human_readable(seconds: int) -> str:
    td = timedelta(seconds=seconds)
    days = td.days
    hours, rem = divmod(td.seconds, 3600)
    minutes, secs = divmod(rem, 60)
    parts = []
    if days: parts.append(f"{days}d")
    if hours: parts.append(f"{hours}h")
    if minutes: parts.append(f"{minutes}m")
    if secs: parts.append(f"{secs}s")
    return ''.join(parts) if parts else "0s"

# resolve_user: try by @username or numeric id; if not found, returns None
async def resolve_user(client: Client, chat_id: int, identifier: str):
    identifier = identifier.strip()
    if identifier.isdigit():
        try:
            user = await client.get_users(int(identifier))
            return user
        except Exception:
            return None
    if identifier.startswith("@"):
        identifier = identifier[1:]
    try:
        user = await client.get_users(identifier)
        return user
    except Exception:
        return None

# is_admin: checks if a user is an admin or owner in the chat
async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status in ("creator", "administrator"):
            return True
        return False
    except Exception:
        return False
