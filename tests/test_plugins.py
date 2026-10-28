import pytest
from abot.util.plugins import (
	normalize_plugin_name,
	normalize_plugin_url,
	normalize_plugin_name_author,
	GitException,
	install_plugin,
	remove_plugin,
)


def test_normalize_plugin_name():
	assert normalize_plugin_name("https://github.com/adev/tricks.git") == "tricks"
	assert normalize_plugin_name("git@github.com:adev/tricks.git") == "tricks"
	assert normalize_plugin_name("adev/tricks") == "tricks"
	assert normalize_plugin_name("tricks") == "tricks"


def test_normalize_plugin_url():
	assert normalize_plugin_url("https://github.com/adev/tricks.git") == "https://github.com/adev/tricks.git"
	assert normalize_plugin_url("git@github.com:adev/tricks.git") == "git@github.com:adev/tricks.git"
	assert normalize_plugin_url("adev/tricks") == "https://github.com/adev/tricks.git"
	assert normalize_plugin_url("https://user:pass@github.com/adev/tricks.git") == "https://github.com/adev/tricks.git"


def test_normalize_plugin_name_author():
	plugin, author = normalize_plugin_name_author("https://github.com/adev/tricks.git")
	assert plugin == "tricks"
	assert author == "adev"

	plugin, author = normalize_plugin_name_author("git@github.com:adev/tricks.git")
	assert plugin == "tricks"
	assert author == "adev"

	plugin, author = normalize_plugin_name_author("adev/tricks")
	assert plugin == "tricks"
	assert author == "adev"

	plugin, author = normalize_plugin_name_author("solo_plugin")
	assert plugin == "solo_plugin"
	assert author == "unknown"


@pytest.mark.asyncio
async def test_install_plugin_traversal():
	with pytest.raises(GitException, match="outside of plugins directory"):
		await install_plugin("https://github.com/adev/tricks.git", path="../outside")


@pytest.mark.asyncio
async def test_remove_plugin_traversal():
	with pytest.raises(GitException, match="Invalid plugin name"):
		await remove_plugin("../outside")


@pytest.mark.asyncio
async def test_install_plugin_flag_injection():
	with pytest.raises(GitException, match="leading '-' not allowed"):
		await install_plugin("--upload-pack=evil")

	with pytest.raises(GitException, match="leading '-' not allowed"):
		await install_plugin("https://github.com/adev/tricks.git", branch="--evil-flag")
