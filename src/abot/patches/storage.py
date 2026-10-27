import json
import inspect

from pathlib import Path
from typing import Dict, Any, Tuple, Optional

from pyrogram.storage import FileStorage

DOCUMENT_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents
(
	key TEXT PRIMARY KEY,
	doc TEXT
);

CREATE TABLE IF NOT EXISTS last_message
(
	chat_id INTEGER,
	message_id INTEGER
);
"""

class DocumentFileStorage(FileStorage):
	"""
	A wrapper around pyrogram FileStorage to add simple document-like capabilities in json format.
	It's not efficient and more complex use-cases should directly run query on the connection object, but 
	simple values can be made persistant easily. It also by default creates and searches the session object inside 
	the data folder, to not litter top level with runtime data.
	"""
	def __init__(self, name: str, workdir: Path):
		data_dir = Path(workdir) / 'data'
		data_dir.mkdir(parents=True, exist_ok=True)
		super().__init__(name, data_dir)

	async def update(self):
		if not self.conn:
			await self.open()
			return
		res = super().update()
		if inspect.isawaitable(res):
			await res
		if self.conn:
			await self.conn.executescript(DOCUMENT_SCHEMA)
			await self.conn.commit()

	async def create(self):
		if not self.conn:
			await self.open()
			return
		res = super().create()
		if inspect.isawaitable(res):
			await res
		if self.conn:
			await self.conn.executescript(DOCUMENT_SCHEMA)
			await self.conn.commit()

	async def _get_last_message(self) -> Optional[Tuple[int, int]]:
		if not self.conn:
			return None
		async with self.conn.execute("SELECT * FROM last_message") as cursor:
			res = await cursor.fetchone()
		if res:
			await self.conn.execute("DELETE FROM last_message")
			await self.conn.commit()
			return res
		return None

	async def _set_last_message(self, chat_id: int, message_id: int):
		if not self.conn:
			return
		await self.conn.execute("DELETE FROM last_message")
		await self.conn.execute("INSERT INTO last_message VALUES (?, ?)", (chat_id, message_id))
		await self.conn.commit()

	async def get_doc(self, key: str) -> Optional[Dict[str, Any]]:
		if not self.conn:
			return None
		async with self.conn.execute("SELECT doc FROM documents WHERE key = ?", (key,)) as cursor:
			row = await cursor.fetchone()
		if row is None or row[0] is None:
			return None
		return json.loads(row[0])

	async def put_doc(self, key: str, doc: Dict[str, Any]) -> None:
		if not self.conn:
			return
		await self.conn.execute("DELETE FROM documents WHERE key = ?", (key,))
		await self.conn.execute("INSERT INTO documents VALUES (?, ?)", (key, json.dumps(doc)))
		await self.conn.commit()
