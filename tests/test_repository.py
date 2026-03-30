import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from src.application.salon_manager import SalonManager
from src.domain.appointment import AppointmentStatus
from src.domain.salon import Salon
from src.infrastructure.salon_repository import SalonRepository


class TestRepository(unittest.TestCase):

    def test_repository_restores_appointment_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "salon_data.json"
            repo = SalonRepository(str(data_file))
            manager = SalonManager(Salon(), repo)

            client = manager.create_client("Anna", "123")
            service = manager.create_service("Haircut", 30, 20)
            master = manager.create_master("Olga", [service.id])
            appointment = manager.book_appointment(
                client.id,
                master.id,
                service.id,
                datetime(2026, 4, 5, 14, 0),
            )

            manager.complete_appointment(appointment.id)
            loaded_salon = repo.load()

            self.assertEqual(len(loaded_salon.appointments), 1)
            self.assertEqual(
                loaded_salon.appointments[0].status,
                AppointmentStatus.COMPLETED,
            )

    def test_repository_restores_active_schedule_from_appointments(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "salon_data.json"
            repo = SalonRepository(str(data_file))
            manager = SalonManager(Salon(), repo)

            client = manager.create_client("Anna", "123")
            service = manager.create_service("Haircut", 30, 20)
            master = manager.create_master("Olga", [service.id])
            booking_time = datetime(2026, 4, 5, 14, 0)

            manager.book_appointment(
                client.id,
                master.id,
                service.id,
                booking_time,
            )

            loaded_salon = repo.load()
            loaded_master = loaded_salon.masters[0]

            self.assertFalse(loaded_master.is_available(booking_time))


if __name__ == "__main__":
    unittest.main()
