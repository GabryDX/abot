import tempfile
from pathlib import Path
import pytest
from abot.patches.storage import DocumentFileStorage


@pytest.mark.asyncio
async def test_document_file_storage_crud():
	with tempfile.TemporaryDirectory() as tmpdir:
		storage = DocumentFileStorage("test_session", Path(tmpdir))
		await storage.open()

		# Test non-existent key returns None without crashing
		assert await storage.get_doc("missing_key") is None

		# Test putting and getting document
		payload = {"foo": "bar", "count": 10, "nested": {"a": [1, 2, 3]}}
		await storage.put_doc("my_key", payload)

		res = await storage.get_doc("my_key")
		assert res == payload
		assert res["count"] == 10
		assert res["nested"]["a"] == [1, 2, 3]

		# Test overwriting existing document
		updated_payload = {"foo": "updated"}
		await storage.put_doc("my_key", updated_payload)
		assert await storage.get_doc("my_key") == updated_payload

		await storage.close()


@pytest.mark.asyncio
async def test_storage_last_message():
	with tempfile.TemporaryDirectory() as tmpdir:
		storage = DocumentFileStorage("test_session", Path(tmpdir))
		await storage.open()

		assert await storage._get_last_message() is None

		await storage._set_last_message(chat_id=12345, message_id=67890)
		last = await storage._get_last_message()
		assert last == (12345, 67890)

		# Ensure reading it consumed/cleared it
		assert await storage._get_last_message() is None

		await storage.close()
