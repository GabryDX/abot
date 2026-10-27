from abot.util.command import ConsumableBuffer, CommandMatch


def test_consumable_buffer():
    buf = ConsumableBuffer(".cmd -f --opt value arg1")
    buf.consume("-f")
    assert "-f" not in str(buf)

    buf.consume(["--opt", "value"])
    assert "--opt" not in str(buf)
    assert "value" not in str(buf)
    assert "arg1" in str(buf)


def test_command_match():
    cmd = CommandMatch("test")
    assert cmd.base == "test"
    assert len(cmd) == 0

    cmd.arg.append("first")
    cmd.arg.append("second")
    assert len(cmd) == 2
    assert cmd[0] == "first"
    assert cmd[1] == "second"

    cmd.flags.append("-force")
    assert "-force" in cmd
    assert cmd["-force"] is True

    cmd.options["target"] = "user123"
    assert "target" in cmd
    assert cmd["target"] == "user123"
    assert cmd.option("target") == "user123"
    assert cmd.option("nonexistent", default="def") == "def"
    assert cmd["missing"] is None
