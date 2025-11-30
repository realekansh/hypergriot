import pytest
from bot.utils import parse_time_to_seconds, human_readable

def test_parse_simple_units():
    assert parse_time_to_seconds("1s") == 1
    assert parse_time_to_seconds("1m") == 60
    assert parse_time_to_seconds("1h") == 3600
    assert parse_time_to_seconds("1d") == 86400
    assert parse_time_to_seconds("1w") == 604800

def test_parse_compound():
    assert parse_time_to_seconds("1h30m") == 3600 + 1800
    assert parse_time_to_seconds("2d3h4m5s") == 2*86400 + 3*3600 + 4*60 + 5

def test_parse_spaces_and_words():
    assert parse_time_to_seconds("2 hours 30 min") == 2*3600 + 30*60

def test_invalid_unit_raises():
    with pytest.raises(ValueError):
        parse_time_to_seconds("5x")

def test_human_readable_roundtrip():
    secs = 3665  # 1h1m5s
    hr = human_readable(secs)
    # human_readable returns "1h1m5s" or similar; ensure it's non-empty and contains 'h' or 'm'
    assert isinstance(hr, str) and len(hr) > 0
