"""
services/flood_service.py

Safe async Redis helper for flood counters.

This module prefers redis.asyncio (redis-py >=4.x) and falls back to aioredis if available.
Importing this module will not raise on machines without Redis clients installed;
instead get_redis() will raise an informative error when actually called.
"""
import os
import typing

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis_client_module = None
_redis_client_name = None

# Try to import redis.asyncio (preferred)
try:
    import redis.asyncio as _redis_asyncio  # type: ignore
    _redis_client_module = _redis_asyncio
    _redis_client_name = "redis.asyncio"
except Exception:
    # fallback to aioredis (older package) if available
    try:
        import aioredis as _aioredis  # type: ignore
        _redis_client_module = _aioredis
        _redis_client_name = "aioredis"
    except Exception:
        _redis_client_module = None
        _redis_client_name = None

async def get_redis():
    """
    Return an async Redis client instance.

    - If redis.asyncio is available, returns redis.asyncio.from_url(...)
    - If aioredis is available, returns aioredis.from_url(...)
    - If neither is available, raises ImportError with guidance.
    """
    if _redis_client_module is None:
        raise ImportError(
            "No async Redis client available. Install 'redis' (redis-py >= 4.x) "
            "for best compatibility: pip install redis[async]\n"
            "Or, if you prefer the older aioredis, install it: pip install aioredis\n\n"
            f"Detected client: {_redis_client_name}"
        )

    # For redis.asyncio (redis-py >=4), use from_url
    if _redis_client_name == "redis.asyncio":
        return _redis_client_module.from_url(REDIS_URL)
    # For aioredis (older), use from_url as well
    if _redis_client_name == "aioredis":
        return _redis_client_module.from_url(REDIS_URL)
    # Should not reach here
    raise ImportError("No supported async redis client available.")
