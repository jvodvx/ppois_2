import unittest
from datetime import datetime

from src.domain.master import Master
from src.domain.service import Service


class TestMaster(unittest.TestCase):

    def test_add_service(self):

        master = Master(1, "Olga")

        service = Service(1, "Haircut", 30, 20)

        master.add_service(service)

        self.assertIn(service, master.services)

    def test_can_do_service(self):

        master = Master(1, "Olga")

        service = Service(1, "Haircut", 30, 20)

        master.add_service(service)

        self.assertTrue(master.can_do_service(service))

    def test_master_availability(self):

        master = Master(1, "Olga")

        time = datetime(2026, 4, 5, 14, 0)

        self.assertTrue(master.is_available(time))

        master.book_time(time)

        self.assertFalse(master.is_available(time))


if __name__ == "__main__":
    unittest.main()