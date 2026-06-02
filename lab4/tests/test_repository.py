import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from src.application.salon_manager import SalonManager
from src.domain.appointment import AppointmentStatus
from src.domain.salon import Salon
from src.infrastructure.salon_repository import SalonRepository


class TestRepository(unittest.TestCase):

    @staticmethod
    def _future_time(days: int, hour: int, minute: int = 0) -> datetime:
        base = datetime.now().replace(second=0, microsecond=0) + timedelta(days=days)
        return base.replace(hour=hour, minute=minute)

    @staticmethod
    def _create_manager(repo: SalonRepository) -> SalonManager:
        return SalonManager(Salon(), repo)

    def test_repository_restores_completed_and_paid_appointment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "salon_data.json"
            repo = SalonRepository(str(data_file))
            manager = self._create_manager(repo)

            client = manager.create_client("Anna", "123")
            service = manager.get_service_by_name("Haircut")
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
                self._future_time(1, 14),
            )

            manager.complete_appointment(appointment.id, tool_ids=[tool.id])
            manager.pay_for_service(appointment.id)

            loaded_salon = repo.load()
            loaded_appointment = loaded_salon.appointments[0]

            self.assertEqual(loaded_appointment.status, AppointmentStatus.COMPLETED)
            self.assertTrue(loaded_appointment.paid)

    def test_repository_restores_active_bookings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "salon_data.json"
            repo = SalonRepository(str(data_file))
            manager = self._create_manager(repo)

            client = manager.create_client("Anna", "123")
            service = manager.get_service_by_name("Haircut")
            tool = manager.create_tool("Scissors")
            mirror = manager.create_mirror("Mirror 1")
            chair = manager.create_chair("Chair 1")
            hairdresser = manager.create_hairdresser(
                "Olga",
                [service.id],
                [tool.id],
            )
            booking_time = self._future_time(1, 14)

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
