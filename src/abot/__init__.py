import sys

# Ensure wzgram acts as a seamless drop-in for pyrogram imports if wzgram is installed
try:
	import wzgram
	if "pyrogram" not in sys.modules:
		sys.modules["pyrogram"] = wzgram
except ImportError:
	pass

from .bot import aBot
