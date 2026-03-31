import unittest
from datetime import datetime

from src.domain.chair import Chair
from src.domain.mirror import Mirror
from src.domain.tool import Tool


class TestResources(unittest.TestCase):

    def test_create_tool(self) -> None:
        tool = Tool(1, "Scissors")
        self.assertEqual(tool.name, "Scissors")

    def test_chair_and_mirror_availability(self) -> None:
        booking_time = datetime(2026, 4, 5, 14, 0)
        chair = Chair(1, "Chair 1")
        mirror = Mirror(1, "Mirror 1")

        self.assertTrue(chair.is_available(booking_time))
        self.assertTrue(mirror.is_available(booking_time))

        chair.book_time(booking_time)
        mirror.book_time(booking_time)

        self.assertFalse(chair.is_available(booking_time))
        self.assertFalse(mirror.is_available(booking_time))


if __name__ == "__main__":
    unittest.main()
