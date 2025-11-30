# bot/command_registry.py
# A simple registry used by help and docs generator.
# Handlers should import and register metadata here.

COMMANDS = {
    "ban": {"usage": "ban <user> <reason?>", "short": "Ban a user permanently", "category": "Moderation"},
    "sban": {"usage": "sban <user> <reason?>", "short": "Silent ban", "category": "Moderation"},
    "tban": {"usage": "tban <user> <time> <reason?>", "short": "Temporary ban", "category": "Moderation"},
    "mute": {"usage": "mute <user> <reason?>", "short": "Mute a user", "category": "Moderation"},
    "tmute": {"usage": "tmute <user> <time> <reason?>", "short": "Temporary mute", "category": "Moderation"},
    "kick": {"usage": "kick <user> <reason?>", "short": "Kick user from chat", "category": "Moderation"},
    "purge": {"usage": "purge [count]", "short": "Delete recent messages", "category": "Moderation"},
    "flood": {"usage": "flood", "short": "Show flood protection status", "category": "Anti-Spam"},
    "setflood": {"usage": "setflood <count|on|off>", "short": "Configure flood threshold", "category": "Anti-Spam"},
}
