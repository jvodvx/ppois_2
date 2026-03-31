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
        self.service = self.manager.get_service_by_name("Haircut")
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

    def test_complete_haircut_and_pay(self) -> None:
        appointment = self.manager.book_haircut(
            self.client.id,
            self.hairdresser.id,
            self.service.id,
            self.chair.id,
            self.mirror.id,
            datetime(2026, 4, 5, 14, 0),
        )

        self.manager.complete_appointment(appointment.id, tool_ids=[self.tool.id])
        amount = self.manager.pay_for_service(appointment.id)

        self.assertEqual(appointment.status, AppointmentStatus.COMPLETED)
        self.assertTrue(appointment.paid)
        self.assertEqual(amount, self.service.price)

    def test_consultation_marks_booking_completed(self) -> None:
        consultation_service = self.manager.get_service_by_name("Consultation")
        self.hairdresser.add_service(consultation_service)

        appointment = self.manager.book_haircut(
            self.client.id,
            self.hairdresser.id,
            consultation_service.id,
            self.chair.id,
            self.mirror.id,
            datetime(2026, 4, 6, 12, 0),
        )

        self.manager.complete_appointment(
            appointment.id,
            notes="Use a nourishing mask once a week.",
        )

        self.assertEqual(appointment.status, AppointmentStatus.COMPLETED)

    def test_styling_marks_booking_completed(self) -> None:
        styling_service = self.manager.get_service_by_name("Styling")
        self.hairdresser.add_service(styling_service)

        appointment = self.manager.book_haircut(
            self.client.id,
            self.hairdresser.id,
            styling_service.id,
            self.chair.id,
            self.mirror.id,
            datetime(2026, 4, 7, 16, 0),
        )

        self.manager.complete_appointment(appointment.id, tool_ids=[self.tool.id])

        self.assertEqual(appointment.status, AppointmentStatus.COMPLETED)


if __name__ == "__main__":
    unittest.main()
