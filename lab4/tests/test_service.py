import unittest

from src.domain.service import Service
from src.exceptions import ValidationError


class TestService(unittest.TestCase):
    def test_create_service(self) -> None:
        service = Service(1, "Haircut", 30, 20)

        self.assertEqual(service.name, "Haircut")
        self.assertEqual(service.duration, 30)
        self.assertEqual(service.price, 20)
        self.assertTrue(service.requires_tools)

    def test_invalid_duration(self) -> None:
        with self.assertRaises(ValidationError):
            Service(1, "Haircut", -10, 20)

    def test_invalid_price(self) -> None:
        with self.assertRaises(ValidationError):
            Service(1, "Haircut", 30, -5)

    def test_create_consultation_service(self) -> None:
        service = Service(1, "Consultation", 20, 15, Service.CONSULTATION)

        self.assertTrue(service.requires_notes)
        self.assertFalse(service.requires_tools)

    def test_invalid_execution_mode(self) -> None:
        with self.assertRaises(ValidationError):
            Service(1, "Coloring", 60, 45, "invalid")


if __name__ == "__main__":
    unittest.main()
