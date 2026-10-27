import tempfile
from pathlib import Path
from abot.patches.storage import DocumentFileStorage


def test_document_file_storage_crud():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = DocumentFileStorage("test_session", Path(tmpdir))
        storage.create()

        # Test non-existent key returns None without crashing
        assert storage.get_doc("missing_key") is None

        # Test putting and getting document
        payload = {"foo": "bar", "count": 10, "nested": {"a": [1, 2, 3]}}
        storage.put_doc("my_key", payload)

        res = storage.get_doc("my_key")
        assert res == payload
        assert res["count"] == 10
        assert res["nested"]["a"] == [1, 2, 3]

        # Test overwriting existing document
        updated_payload = {"foo": "updated"}
        storage.put_doc("my_key", updated_payload)
        assert storage.get_doc("my_key") == updated_payload


def test_storage_last_message():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = DocumentFileStorage("test_session", Path(tmpdir))
        storage.create()

        assert storage._get_last_message() is None

        storage._set_last_message(chat_id=12345, message_id=67890)
        last = storage._get_last_message()
        assert last == (12345, 67890)

        # Ensure reading it consumed/cleared it
        assert storage._get_last_message() is None
