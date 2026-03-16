import unittest
from datetime import datetime

from src.domain.client import Client
from src.domain.master import Master
from src.domain.service import Service
from src.domain.appointment import Appointment


class TestAppointment(unittest.TestCase):

    def test_create_appointment(self):

        client = Client(1, "Anna", "123")
        master = Master(1, "Olga")
        service = Service(1, "Haircut", 30, 20)

        master.add_service(service)

        appointment = Appointment(
            1,
            client,
            master,
            service,
            datetime(2026, 4, 5, 14, 0)
        )

        self.assertEqual(appointment.client.name, "Anna")
        self.assertEqual(appointment.master.name, "Olga")

    def test_status_default(self):

        client = Client(1, "Anna", "123")
        master = Master(1, "Olga")
        service = Service(1, "Haircut", 30, 20)

        appointment = Appointment(
            1,
            client,
            master,
            service,
            datetime(2026, 4, 5, 14, 0)
        )

        self.assertEqual(appointment.status.value, "created")


if __name__ == "__main__":
    unittest.main()