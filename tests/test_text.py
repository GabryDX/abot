from datetime import timedelta
from abot.util.text import batchify, cleanhtml, order_suffix
from abot.util.time import parse_timedelta


def test_batchify():
	text = "abcdefghij"
	assert batchify(text, 4) == ["abcd", "efgh", "ij"]
	assert batchify(text, 20) == ["abcdefghij"]
	assert batchify("1234", 2) == ["12", "34"]
	assert batchify("", 5) == [""]


def test_cleanhtml():
    raw = "<b>Hello</b> <i>World</i>! <a href='https://example.com'>Link</a>"
    assert cleanhtml(raw) == "Hello World! Link"


def test_order_suffix():
    assert "1.0 KiB" in order_suffix(1024)
    assert "1.0 MiB" in order_suffix(1024 * 1024)
    assert "500.0 B" in order_suffix(500)


def test_parse_timedelta():
    assert parse_timedelta("60") == timedelta(seconds=60)
    assert parse_timedelta("1h") == timedelta(hours=1)
    assert parse_timedelta("1d12h") == timedelta(days=1, hours=12)
    assert parse_timedelta("30m") == timedelta(minutes=30)
