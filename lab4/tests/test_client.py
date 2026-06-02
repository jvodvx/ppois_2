import unittest
from src.domain.client import Client


class TestClient(unittest.TestCase):

    def test_create_client(self) -> None:
        client = Client(1, "Anna", "123")

        self.assertEqual(client.name, "Anna")
        self.assertEqual(client.phone, "123")

    def test_update_phone(self) -> None:
        client = Client(1, "Anna", "123")

        client.update_phone("456")

        self.assertEqual(client.phone, "456")


if __name__ == "__main__":
    unittest.main()
