import unittest
from datetime import datetime

from src.domain.salon import Salon
from src.domain.service import Service
from src.application.salon_manager import SalonManager


class TestBooking(unittest.TestCase):

    def setUp(self):

        self.salon = Salon()
        self.manager = SalonManager(self.salon)

        self.client = self.manager.create_client("Anna", "123")

        self.service = self.manager.create_service(
            "Haircut",
            30,
            20
        )

        self.master = self.manager.create_master(
            "Olga",
            [self.service.id]
        )

    def test_create_appointment(self):

        appointment = self.manager.book_appointment(
            self.client.id,
            self.master.id,
            self.service.id,
            datetime(2026, 4, 5, 14, 0)
        )

        self.assertEqual(appointment.client.name, "Anna")
        self.assertEqual(appointment.master.name, "Olga")

    def test_master_busy(self):

        time = datetime(2026, 4, 5, 14, 0)

        self.manager.book_appointment(
            self.client.id,
            self.master.id,
            self.service.id,
            time
        )

        with self.assertRaises(Exception):

            self.manager.book_appointment(
                self.client.id,
                self.master.id,
                self.service.id,
                time
            )

    def test_master_cannot_do_service(self):
        other_service = self.manager.create_service(
            "Coloring",
            60,
            50
        )

        with self.assertRaises(Exception):
            self.manager.book_appointment(
                self.client.id,
                self.master.id,
                other_service.id,
                datetime(2026, 4, 5, 14, 0)
            )

if __name__ == "__main__":
    unittest.main()