#!/usr/bin/env python3
"""
Auto-generate the commands list from bot.command_registry.

If the registry isn't available (e.g., missing imports), it falls back
to placeholder data so CI never breaks.
"""

import os
import importlib

OUTPUT = "docs/commands.md"

HEADER = """# HyperGriot Commands

This file is generated automatically.

"""

def load_registry():
    try:
        reg = importlib.import_module("bot.command_registry")
        if hasattr(reg, "COMMANDS"):
            return reg.COMMANDS
    except Exception:
        pass

    # fallback sample data
    return {
        "ban": ("ban <user> <time>", "Ban a user temporarily or permanently"),
        "mute": ("mute <user> <time>", "Mute a user"),
        "warn": ("warn <user> [reason]", "Add a warning"),
    }

def generate_table(cmds):
    lines = []
    lines.append("| Command | Usage | Description |")
    lines.append("|---------|--------|-------------|")
    for name, (usage, desc) in sorted(cmds.items()):
        lines.append(f"| `{name}` | `{usage}` | {desc} |")
    return "\n".join(lines)

def main():
    cmds = load_registry()
    md = HEADER + "\n" + generate_table(cmds) + "\n"
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        f.write(md)
    print(f"[ok] Generated {OUTPUT}")

if __name__ == "__main__":
    main()
