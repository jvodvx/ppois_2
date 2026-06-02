import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from src.bootstrap import build_manager
from src.domain.appointment import AppointmentStatus
from src.presentation.web_app import create_app


class TestWebApp(unittest.TestCase):

    @staticmethod
    def _future_time(days: int, hour: int, minute: int = 0) -> datetime:
        base = datetime.now().replace(second=0, microsecond=0) + timedelta(days=days)
        return base.replace(hour=hour, minute=minute)

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "test_salon_data.json"
        self.manager = build_manager(str(self.data_file))
        self.app = create_app(self.manager)
        self.app.testing = True
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_index_shows_default_services(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Haircut", response.get_data(as_text=True))
        self.assertIn("Consultation", response.get_data(as_text=True))

    def test_create_service_through_web(self) -> None:
        response = self.client.post(
            "/services",
            data={
                "name": "Coloring",
                "duration": "60",
                "price": "45.50",
                "execution_mode": "tool_based",
                "next_anchor": "registry-section",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("#registry-section", response.headers["Location"])
        self.assertEqual(self.manager.list_services()[-1].name, "Coloring")

    def test_create_entities_and_book_complete_pay_flow(self) -> None:
        self.client.post(
            "/clients",
            data={"name": "Анна", "phone": "+375291112233"},
            follow_redirects=True,
        )
        self.client.post(
            "/tools",
            data={"name": "Scissors"},
            follow_redirects=True,
        )
        self.client.post(
            "/mirrors",
            data={"label": "Mirror A"},
            follow_redirects=True,
        )
        self.client.post(
            "/chairs",
            data={"label": "Chair A"},
            follow_redirects=True,
        )

        haircut = self.manager.get_service_by_name("Haircut")
        response = self.client.post(
            "/hairdressers",
            data={
                "name": "Ольга",
                "service_ids": [str(haircut.id)],
                "tool_ids": [str(self.manager.list_tools()[0].id)],
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.manager.list_hairdressers()), 1)

        booking_response = self.client.post(
            "/appointments",
            data={
                "client_id": str(self.manager.list_clients()[0].id),
                "hairdresser_id": str(self.manager.list_hairdressers()[0].id),
                "service_id": str(haircut.id),
                "chair_id": str(self.manager.list_chairs()[0].id),
                "mirror_id": str(self.manager.list_mirrors()[0].id),
                "time": self._future_time(2, 10, 30).strftime("%Y-%m-%dT%H:%M"),
            },
            follow_redirects=True,
        )

        appointment = self.manager.list_appointments()[0]
        self.assertEqual(booking_response.status_code, 200)
        self.assertEqual(appointment.status, AppointmentStatus.BOOKED)

        complete_response = self.client.post(
            f"/appointments/{appointment.id}/complete",
            data={"tool_ids": [str(self.manager.list_tools()[0].id)]},
            follow_redirects=True,
        )

        self.assertEqual(complete_response.status_code, 200)
        self.assertEqual(appointment.status, AppointmentStatus.COMPLETED)

        pay_response = self.client.post(
            f"/appointments/{appointment.id}/pay",
            follow_redirects=True,
        )

        self.assertEqual(pay_response.status_code, 200)
        self.assertTrue(appointment.paid)
        self.assertIn("Payment accepted", pay_response.get_data(as_text=True))

    def test_cancel_appointment_through_web(self) -> None:
        client = self.manager.create_client("Maria", "123")
        tool = self.manager.create_tool("Brush")
        mirror = self.manager.create_mirror("Mirror B")
        chair = self.manager.create_chair("Chair B")
        service = self.manager.get_service_by_name("Styling")
        hairdresser = self.manager.create_hairdresser(
            "Irina",
            [service.id],
            [tool.id],
        )
        appointment = self.manager.book_haircut(
            client.id,
            hairdresser.id,
            service.id,
            chair.id,
            mirror.id,
            self._future_time(3, 11),
        )

        response = self.client.post(
            f"/appointments/{appointment.id}/cancel",
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(appointment.status, AppointmentStatus.CANCELLED)

    def test_complete_consultation_through_web(self) -> None:
        client = self.manager.create_client("Elena", "555")
        mirror = self.manager.create_mirror("Mirror C")
        chair = self.manager.create_chair("Chair C")
        consultation = self.manager.get_service_by_name("Consultation")
        hairdresser = self.manager.create_hairdresser(
            "Svetlana",
            [consultation.id],
            [],
        )
        appointment = self.manager.book_haircut(
            client.id,
            hairdresser.id,
            consultation.id,
            chair.id,
            mirror.id,
            self._future_time(4, 15),
        )

        response = self.client.post(
            f"/appointments/{appointment.id}/complete",
            data={"notes": "Использовать питательную маску один раз в неделю."},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(appointment.status, AppointmentStatus.COMPLETED)
        self.assertIn("питательную маску", appointment.consultation_notes)

    def test_hairdresser_with_haircut_requires_tool_in_web(self) -> None:
        haircut = self.manager.get_service_by_name("Haircut")

        response = self.client.post(
            "/hairdressers",
            data={
                "name": "Ольга",
                "service_ids": [str(haircut.id)],
                "tool_ids": [],
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.manager.list_hairdressers()), 0)
        self.assertIn("at least one tool", response.get_data(as_text=True))

    def test_web_rejects_booking_outside_working_hours(self) -> None:
        client = self.manager.create_client("Anna", "123")
        tool = self.manager.create_tool("Scissors")
        mirror = self.manager.create_mirror("Mirror A")
        chair = self.manager.create_chair("Chair A")
        service = self.manager.get_service_by_name("Haircut")
        hairdresser = self.manager.create_hairdresser("Olga", [service.id], [tool.id])

        response = self.client.post(
            "/appointments",
            data={
                "client_id": str(client.id),
                "hairdresser_id": str(hairdresser.id),
                "service_id": str(service.id),
                "chair_id": str(chair.id),
                "mirror_id": str(mirror.id),
                "time": self._future_time(2, 7, 30).strftime("%Y-%m-%dT%H:%M"),
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.manager.list_appointments()), 0)
        self.assertIn("between 08:00 and 20:00", response.get_data(as_text=True))
