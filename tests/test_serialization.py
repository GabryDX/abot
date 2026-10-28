from abot.util.serialization import convert_to_dict


class DummyObject:
	def __init__(self, name: str, phone: str = None, count: int = 1):
		self.name = name
		if phone:
			self.phone_number = phone
		self.count = count


def test_convert_to_dict_primitives():
	assert convert_to_dict(42) == 42
	assert convert_to_dict("hello") == "hello"
	assert convert_to_dict(True) is True
	assert convert_to_dict(None) is None
	assert convert_to_dict([1, 2, 3]) == [1, 2, 3]


def test_convert_to_dict_objects_and_masking():
	obj = DummyObject("Alice", phone="+1234567890", count=5)
	d = convert_to_dict(obj)
	assert d["_"] == "DummyObject"
	assert d["name"] == "Alice"
	assert d["count"] == 5
	assert d["phone_number"] == "*" * len("+1234567890")  # masked
