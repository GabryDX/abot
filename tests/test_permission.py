import tempfile
import os
from abot.util.permission import Authenticator, JsonDriver


def test_authenticator_permissions():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a custom JsonDriver pointing to tmpdir
        class TmpJsonDriver(JsonDriver):
            def __init__(self, name: str):
                self.fname = os.path.join(tmpdir, f"perms-{name}.json")
                super(JsonDriver, self).__init__(name)

        auth = Authenticator("testbot", driver=TmpJsonDriver)

        # Default state
        assert not auth.check(11111)
        assert not auth.any(11111)
        assert len(auth.all()) == 0

        # Add user
        assert auth.put(11111) is True
        assert auth.check(11111) is True
        assert auth.any(11111) is True
        assert 11111 in auth.all()

        # Duplicate put
        assert auth.put(11111) is False

        # Add to custom group
        assert auth.put(22222, group="moderators") is True
        assert auth.check(22222, group="moderators") is True
        assert not auth.check(22222, group="_")

        # Pop user
        assert auth.pop(11111) is True
        assert not auth.check(11111)
        assert auth.pop(11111) is False


@pytest.mark.asyncio
async def test_perms_filter_headless_update():
	from types import SimpleNamespace
	from abot.util.permission import PermsFilter

	flt = PermsFilter()
	client = SimpleNamespace(sudoers=[], public=False)
	update = SimpleNamespace(from_user=None, sender_chat=None)
	res = await flt(client, update)
	assert res is False
