import unittest
from datetime import datetime

from src.domain.hairdresser import Hairdresser
from src.domain.service import Service
from src.domain.tool import Tool


class TestHairdresser(unittest.TestCase):

    def test_add_service_and_tool(self) -> None:
        hairdresser = Hairdresser(1, "Olga")
        service = Service(1, "Haircut", 30, 20)
        tool = Tool(1, "Scissors")

        hairdresser.add_service(service)
        hairdresser.add_tool(tool)

        self.assertIn(service, hairdresser.services)
        self.assertIn(tool, hairdresser.tools)

    def test_can_do_service(self) -> None:
        hairdresser = Hairdresser(1, "Olga")
        service = Service(1, "Haircut", 30, 20)

        hairdresser.add_service(service)

        self.assertTrue(hairdresser.can_do_service(service))

    def test_hairdresser_availability(self) -> None:
        hairdresser = Hairdresser(1, "Olga")
        booking_time = datetime(2026, 4, 5, 14, 0)

        self.assertTrue(hairdresser.is_available(booking_time))
        hairdresser.book_time(booking_time)
        self.assertFalse(hairdresser.is_available(booking_time))


if __name__ == "__main__":
    unittest.main()
