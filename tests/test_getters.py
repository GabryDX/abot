from types import SimpleNamespace
from pyrogram.enums import ParseMode
from abot.util.getters import get_text, get_username


def test_get_text_plain_strings():
	msg = SimpleNamespace(text="Hello world", caption=None)
	assert get_text(msg) == "Hello world"

	msg_caption = SimpleNamespace(text=None, caption="Image caption")
	assert get_text(msg_caption) == "Image caption"


def test_get_text_formatted():
	class FormattedStr(str):
		@property
		def html(self):
			return "<b>Bold</b>"

		@property
		def markdown(self):
			return "**Bold**"

	msg = SimpleNamespace(text=FormattedStr("Bold"), caption=None)
	assert get_text(msg, parse_mode=ParseMode.HTML) == "<b>Bold</b>"
	assert get_text(msg, parse_mode=ParseMode.MARKDOWN) == "**Bold**"


def test_get_username():
	assert get_username(None) == "[Anonymous]"

	user_with_username = SimpleNamespace(id=123, username="testuser", first_name="Test")
	assert get_username(user_with_username, mention=False) == "testuser"
	assert get_username(user_with_username, mention=True) == "@testuser"

	user_without_username = SimpleNamespace(id=456, username=None, first_name="John", last_name="Doe", mention=None)
	assert get_username(user_without_username, mention=False) == "John Doe"
