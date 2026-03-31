import unittest
from datetime import datetime

from src.application.salon_manager import SalonManager
from src.domain.appointment import AppointmentStatus
from src.domain.salon import Salon
from src.exceptions import BookingError


class TestBooking(unittest.TestCase):

    def setUp(self) -> None:
        self.salon = Salon()
        self.manager = SalonManager(self.salon)

        self.client = self.manager.create_client("Anna", "123")
        self.service = self.manager.create_service("Haircut", 30, 20)
        self.tool = self.manager.create_tool("Scissors")
        self.mirror = self.manager.create_mirror("Mirror 1")
        self.chair = self.manager.create_chair("Chair 1")
        self.hairdresser = self.manager.create_hairdresser(
            "Olga",
            [self.service.id],
            [self.tool.id],
        )

    def test_book_haircut(self) -> None:
        appointment = self.manager.book_haircut(
            self.client.id,
            self.hairdresser.id,
            self.service.id,
            self.chair.id,
            self.mirror.id,
            datetime(2026, 4, 5, 14, 0),
        )

        self.assertEqual(appointment.client.name, "Anna")
        self.assertEqual(appointment.hairdresser.name, "Olga")
        self.assertEqual(appointment.status, AppointmentStatus.BOOKED)

    def test_hairdresser_chair_and_mirror_conflict(self) -> None:
        booking_time = datetime(2026, 4, 5, 14, 0)

        self.manager.book_haircut(
            self.client.id,
            self.hairdresser.id,
            self.service.id,
            self.chair.id,
            self.mirror.id,
            booking_time,
        )

        second_client = self.manager.create_client("Eva", "456")

        with self.assertRaises(BookingError):
            self.manager.book_haircut(
                second_client.id,
                self.hairdresser.id,
                self.service.id,
                self.chair.id,
                self.mirror.id,
                booking_time,
            )

    def test_perform_consult_and_pay(self) -> None:
        appointment = self.manager.book_haircut(
            self.client.id,
            self.hairdresser.id,
            self.service.id,
            self.chair.id,
            self.mirror.id,
            datetime(2026, 4, 5, 14, 0),
        )

        self.manager.provide_hair_care_consultation(
            appointment.id,
            "Use moisturizing shampoo twice a week.",
        )
        self.manager.perform_haircut_and_styling(appointment.id, [self.tool.id])
        amount = self.manager.pay_for_service(appointment.id)

        self.assertEqual(
            appointment.consultation_notes,
            "Use moisturizing shampoo twice a week.",
        )
        self.assertEqual(appointment.status, AppointmentStatus.SERVICED)
        self.assertTrue(appointment.paid)
        self.assertEqual(amount, 20)


if __name__ == "__main__":
    unittest.main()
