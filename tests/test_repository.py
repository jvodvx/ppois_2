import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from src.application.salon_manager import SalonManager
from src.domain.appointment import AppointmentStatus
from src.domain.salon import Salon
from src.infrastructure.salon_repository import SalonRepository


class TestRepository(unittest.TestCase):

    def test_repository_restores_serviced_and_paid_appointment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "salon_data.json"
            repo = SalonRepository(str(data_file))
            manager = SalonManager(Salon(), repo)

            client = manager.create_client("Anna", "123")
            service = manager.create_service("Haircut", 30, 20)
            tool = manager.create_tool("Scissors")
            mirror = manager.create_mirror("Mirror 1")
            chair = manager.create_chair("Chair 1")
            hairdresser = manager.create_hairdresser(
                "Olga",
                [service.id],
                [tool.id],
            )
            appointment = manager.book_haircut(
                client.id,
                hairdresser.id,
                service.id,
                chair.id,
                mirror.id,
                datetime(2026, 4, 5, 14, 0),
            )

            manager.provide_hair_care_consultation(
                appointment.id,
                "Use a heat protectant before styling.",
            )
            manager.perform_haircut_and_styling(appointment.id, [tool.id])
            manager.pay_for_service(appointment.id)

            loaded_salon = repo.load()
            loaded_appointment = loaded_salon.appointments[0]

            self.assertEqual(loaded_appointment.status, AppointmentStatus.SERVICED)
            self.assertTrue(loaded_appointment.paid)
            self.assertEqual(
                loaded_appointment.consultation_notes,
                "Use a heat protectant before styling.",
            )

    def test_repository_restores_active_bookings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "salon_data.json"
            repo = SalonRepository(str(data_file))
            manager = SalonManager(Salon(), repo)

            client = manager.create_client("Anna", "123")
            service = manager.create_service("Haircut", 30, 20)
            tool = manager.create_tool("Scissors")
            mirror = manager.create_mirror("Mirror 1")
            chair = manager.create_chair("Chair 1")
            hairdresser = manager.create_hairdresser(
                "Olga",
                [service.id],
                [tool.id],
            )
            booking_time = datetime(2026, 4, 5, 14, 0)

            manager.book_haircut(
                client.id,
                hairdresser.id,
                service.id,
                chair.id,
                mirror.id,
                booking_time,
            )

            loaded_salon = repo.load()
            loaded_hairdresser = loaded_salon.hairdressers[0]
            loaded_chair = loaded_salon.chairs[0]
            loaded_mirror = loaded_salon.mirrors[0]

            self.assertFalse(loaded_hairdresser.is_available(booking_time))
            self.assertFalse(loaded_chair.is_available(booking_time))
            self.assertFalse(loaded_mirror.is_available(booking_time))


if __name__ == "__main__":
    unittest.main()
