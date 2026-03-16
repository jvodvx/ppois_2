import unittest

from src.domain.service import Service
from src.exceptions import ValidationError


class TestService(unittest.TestCase):

    def test_create_service(self):

        service = Service(1, "Haircut", 30, 20)

        self.assertEqual(service.name, "Haircut")
        self.assertEqual(service.duration, 30)
        self.assertEqual(service.price, 20)

    def test_invalid_duration(self):

        with self.assertRaises(ValidationError):
            Service(1, "Haircut", -10, 20)

    def test_invalid_price(self):

        with self.assertRaises(ValidationError):
            Service(1, "Haircut", 30, -5)


if __name__ == "__main__":
    unittest.main()