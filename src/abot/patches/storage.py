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

	@property
	def raw_conn(self):
		return getattr(self.conn, "_conn", self.conn)

	async def update(self):
		if not self.conn:
			await self.open()
			return
		res = super().update()
		if inspect.isawaitable(res):
			await res
		if self.raw_conn:
			with self.raw_conn:
				self.raw_conn.executescript(DOCUMENT_SCHEMA)

	async def create(self):
		if not self.conn:
			await self.open()
			return
		res = super().create()
		if inspect.isawaitable(res):
			await res
		if self.raw_conn:
			with self.raw_conn:
				self.raw_conn.executescript(DOCUMENT_SCHEMA)

	def _get_last_message(self) -> Optional[Tuple[int, int]]:
		if not self.raw_conn:
			return None
		res = self.raw_conn.execute("SELECT * FROM last_message").fetchone()
		if res:
			with self.raw_conn:
				self.raw_conn.execute("DELETE FROM last_message")
			return res
		return None

	def _set_last_message(self, chat_id:int, message_id:int):
		if not self.raw_conn:
			return
		with self.raw_conn:
			self.raw_conn.execute("DELETE FROM last_message")
			self.raw_conn.execute("INSERT INTO last_message VALUES (?, ?)", (chat_id, message_id,))

	def get_doc(self, key: str) -> Optional[Dict[str, Any]]:
		if not self.raw_conn:
			return None
		with self.raw_conn:
			row = self.raw_conn.execute(
				"SELECT doc FROM documents WHERE key = ?", (key,)
			).fetchone()
			if row is None or row[0] is None:
				return None
			return json.loads(row[0])

	def put_doc(self, key:str, doc:Dict[str, Any]) -> None:
		if not self.raw_conn:
			return
		with self.raw_conn:
			self.raw_conn.execute("DELETE FROM documents WHERE key = ?", (key, ))
			self.raw_conn.execute("INSERT INTO documents VALUES (?, ?)", (key, json.dumps(doc), ))
