from bot.utils import parse_time_to_seconds, human_readable
import pytest

def test_empty_time_string():
    with pytest.raises(ValueError):
        parse_time_to_seconds("")

def test_human_readable_zero():
    assert human_readable(0) == "0s"
