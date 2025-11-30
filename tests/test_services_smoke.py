import pytest
import asyncio

from services import anti_raid

def test_get_status():
    st = asyncio.get_event_loop().run_until_complete(anti_raid.get_flood_status(123))
    assert "threshold" in st
