"""
bot.utils - small utilities used by HyperGriot tests.

This file intentionally avoids importing heavy network libraries (pyrogram)
at module import time so unit tests can import it safely.
"""

import re
from typing import Dict

# Unit aliases -> seconds multiplier
UNIT_ALIASES = {
    ("s","sec","secs","second","seconds"): 1,
    ("m","min","mins","minute","minutes"): 60,
    ("h","hr","hrs","hour","hours"): 3600,
    ("d","day","days"): 86400,
    ("w","week","weeks"): 604800,
}

# Build a flat lookup mapping (alias -> seconds)
UNITS: Dict[str,int] = {}
for aliases, sec in UNIT_ALIASES.items():
    for a in aliases:
        UNITS[a] = sec

# Regex finds 'number + optional spaces + unit' patterns.
# It is case-insensitive and supports both compact and spaced forms.
TIME_RE = re.compile(r"(\d+)\s*([a-zA-Z]+)", re.IGNORECASE)


def parse_time_to_seconds(s: str) -> int:
    """
    Parse time expressions into seconds.

    Examples:
      "1s" -> 1
      "1h30m" -> 5400
      "2 hours 30 min" -> 9000

    Raises ValueError for invalid input (empty string, unknown unit, invalid numbers).
    """
    if not isinstance(s, str):
        raise ValueError("Time must be a string")
    s = s.strip()
    if not s:
        raise ValueError("Empty time string")

    total = 0
    matched = False
    for match in TIME_RE.finditer(s):
        matched = True
        num_str, unit = match.groups()
        # validate numeric string (no floats allowed here)
        if not num_str.isdigit():
            raise ValueError("Invalid number in time")
        num = int(num_str)
        unit = unit.lower()
        if unit not in UNITS:
            raise ValueError(f"Unknown time unit: {unit}")
        total += num * UNITS[unit]

    if not matched or total <= 0:
        raise ValueError("Time must be > 0 seconds")

    return total


def human_readable(seconds: int) -> str:
    """
    Convert seconds to a compact human-readable string, e.g. 3665 -> "1h1m5s".
    Zero returns "0s".
    """
    if not isinstance(seconds, int):
        raise ValueError("seconds must be int")
    if seconds == 0:
        return "0s"
    parts = []
    rem = seconds
    units = [
        ("w", 604800),
        ("d", 86400),
        ("h", 3600),
        ("m", 60),
        ("s", 1),
    ]
    for suffix, value in units:
        if rem >= value:
            qty, rem = divmod(rem, value)
            parts.append(f"{qty}{suffix}")
    return "".join(parts)
