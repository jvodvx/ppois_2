import unittest
from datetime import datetime

from src.domain.appointment import Appointment, AppointmentStatus
from src.domain.chair import Chair
from src.domain.client import Client
from src.domain.hairdresser import Hairdresser
from src.domain.mirror import Mirror
from src.domain.service import Service
from src.domain.tool import Tool


class TestAppointment(unittest.TestCase):

    def setUp(self) -> None:
        self.client = Client(1, "Anna", "123")
        self.hairdresser = Hairdresser(1, "Olga")
        self.service = Service(1, "Haircut", 30, 20)
        self.chair = Chair(1, "Chair 1")
        self.mirror = Mirror(1, "Mirror 1")
        self.tool = Tool(1, "Scissors")
        self.hairdresser.add_service(self.service)
        self.hairdresser.add_tool(self.tool)

    def test_create_appointment(self) -> None:
        appointment = Appointment(
            1,
            self.client,
            self.hairdresser,
            self.service,
            self.chair,
            self.mirror,
            datetime(2026, 4, 5, 14, 0),
        )

        self.assertEqual(appointment.client.name, "Anna")
        self.assertEqual(appointment.hairdresser.name, "Olga")
        self.assertEqual(appointment.status, AppointmentStatus.BOOKED)

    def test_perform_service_and_pay(self) -> None:
        appointment = Appointment(
            1,
            self.client,
            self.hairdresser,
            self.service,
            self.chair,
            self.mirror,
            datetime(2026, 4, 5, 14, 0),
        )

        appointment.perform_service([self.tool])
        amount = appointment.pay()

        self.assertEqual(appointment.status, AppointmentStatus.SERVICED)
        self.assertTrue(appointment.paid)
        self.assertEqual(amount, 20)


if __name__ == "__main__":
    unittest.main()
