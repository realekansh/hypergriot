# bot/commands.py
from typing import Callable, Dict, List

# Each command registers metadata used for help generation and routing.
# This is the single source of truth for command docs.
registry: List[Dict] = []

def command(name: str, *, category: str = "Misc", usage: str = "", short: str = "", admin_only: bool = False):
    """
    Decorator to register a command handler.
    Usage:
        @command("ban", category="Moderation", usage="ban <user|reply> [reason]", short="Ban user", admin_only=True)
        async def ban_handler(client, message): ...
    """
    def decorator(fn: Callable):
        entry = {
            "name": name,
            "handler": fn,
            "category": category,
            "usage": usage,
            "short": short,
            "admin_only": admin_only,
        }
        registry.append(entry)
        return fn
    return decorator

def find_by_name(name: str):
    for cmd in registry:
        if cmd["name"] == name:
            return cmd
    return None

def commands_in_category(category: str):
    return [c for c in registry if c["category"].lower() == category.lower()]
