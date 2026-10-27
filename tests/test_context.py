import pytest
from abot.util.context import Context


def test_context_basic_operations():
    ctx = Context()
    assert not ctx

    ctx.user = "test_user"
    assert ctx.user == "test_user"
    assert ctx["user"] == "test_user"
    assert bool(ctx) is True

    ctx["count"] = 42
    assert ctx.count == 42
    assert ctx["count"] == 42

    assert ctx.non_existent is None
    assert ctx["non_existent"] is None


def test_context_serialization():
    ctx = Context()
    ctx.key = "value"
    ctx.num = 123

    s = str(ctx)
    assert '"key": "value"' in s
    assert '"num": 123' in s


def test_context_unhashable():
    ctx = Context()
    with pytest.raises(TypeError):
        hash(ctx)
