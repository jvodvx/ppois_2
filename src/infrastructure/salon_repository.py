import json
from datetime import datetime
from pathlib import Path

from ..domain.appointment import Appointment, AppointmentStatus
from ..domain.chair import Chair
from ..domain.client import Client
from ..domain.hairdresser import Hairdresser
from ..domain.mirror import Mirror
from ..domain.salon import Salon
from ..domain.service import Service
from ..domain.tool import Tool


class SalonRepository:

    def __init__(self, filename: str = "salon_data.json"):
        self.filename = Path(filename)

    def save(self, salon: Salon, filename: str | None = None) -> None:
        target = Path(filename) if filename is not None else self.filename

        data = {
            "clients": [
                {"id": client.id, "name": client.name, "phone": client.phone}
                for client in salon.clients
            ],
            "hairdressers": [
                {
                    "id": hairdresser.id,
                    "name": hairdresser.name,
                    "services": [service.id for service in hairdresser.services],
                    "tools": [tool.id for tool in hairdresser.tools],
                }
                for hairdresser in salon.hairdressers
            ],
            "tools": [
                {"id": tool.id, "name": tool.name}
                for tool in salon.tools
            ],
            "services": [
                {
                    "id": service.id,
                    "name": service.name,
                    "duration": service.duration,
                    "price": service.price,
                }
                for service in salon.services
            ],
            "mirrors": [
                {"id": mirror.id, "label": mirror.label}
                for mirror in salon.mirrors
            ],
            "chairs": [
                {"id": chair.id, "label": chair.label}
                for chair in salon.chairs
            ],
            "appointments": [
                {
                    "id": appointment.id,
                    "client": appointment.client.id,
                    "hairdresser": appointment.hairdresser.id,
                    "service": appointment.service.id,
                    "chair": appointment.chair.id,
                    "mirror": appointment.mirror.id,
                    "time": appointment.time.isoformat(),
                    "consultation_notes": appointment.consultation_notes,
                    "used_tools": [tool.id for tool in appointment.used_tools],
                    "status": appointment.status.value,
                    "paid": appointment.paid,
                    "payment_amount": appointment.payment_amount,
                }
                for appointment in salon.appointments
            ],
        }

        with target.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def load(self, filename: str | None = None) -> Salon:
        target = Path(filename) if filename is not None else self.filename
        salon = Salon()

        try:
            with target.open(encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            return salon

        clients: dict[int, Client] = {}
        hairdressers: dict[int, Hairdresser] = {}
        services: dict[int, Service] = {}
        tools: dict[int, Tool] = {}
        mirrors: dict[int, Mirror] = {}
        chairs: dict[int, Chair] = {}

        for client_data in data.get("clients", []):
            client = Client(
                client_data["id"],
                client_data["name"],
                client_data["phone"],
            )
            salon.add_client(client)
            clients[client.id] = client

        for tool_data in data.get("tools", []):
            tool = Tool(tool_data["id"], tool_data["name"])
            salon.add_tool(tool)
            tools[tool.id] = tool

        for service_data in data.get("services", []):
            service = Service(
                service_data["id"],
                service_data["name"],
                service_data["duration"],
                service_data["price"],
            )
            salon.add_service(service)
            services[service.id] = service

        for hairdresser_data in data.get("hairdressers", []):
            hairdresser = Hairdresser(
                hairdresser_data["id"],
                hairdresser_data["name"],
            )
            salon.add_hairdresser(hairdresser)
            hairdressers[hairdresser.id] = hairdresser

            for service_id in hairdresser_data.get("services", []):
                service = services.get(service_id)
                if service is not None:
                    hairdresser.add_service(service)

            for tool_id in hairdresser_data.get("tools", []):
                tool = tools.get(tool_id)
                if tool is not None:
                    hairdresser.add_tool(tool)

        for mirror_data in data.get("mirrors", []):
            mirror = Mirror(mirror_data["id"], mirror_data["label"])
            salon.add_mirror(mirror)
            mirrors[mirror.id] = mirror

        for chair_data in data.get("chairs", []):
            chair = Chair(chair_data["id"], chair_data["label"])
            salon.add_chair(chair)
            chairs[chair.id] = chair

        for appointment_data in data.get("appointments", []):
            hairdresser_id = appointment_data.get("hairdresser")
            chair_id = appointment_data.get("chair")
            mirror_id = appointment_data.get("mirror")

            if hairdresser_id not in hairdressers:
                continue

            if chair_id not in chairs or mirror_id not in mirrors:
                continue

            appointment = Appointment(
                id=appointment_data["id"],
                client=clients[appointment_data["client"]],
                hairdresser=hairdressers[hairdresser_id],
                service=services[appointment_data["service"]],
                chair=chairs[chair_id],
                mirror=mirrors[mirror_id],
                time=datetime.fromisoformat(appointment_data["time"]),
                consultation_notes=appointment_data.get("consultation_notes", ""),
                used_tools=[
                    tools[tool_id]
                    for tool_id in appointment_data.get("used_tools", [])
                    if tool_id in tools
                ],
                status=AppointmentStatus(
                    appointment_data.get(
                        "status",
                        AppointmentStatus.BOOKED.value,
                    )
                ),
                paid=appointment_data.get("paid", False),
                payment_amount=appointment_data.get("payment_amount", 0.0),
            )

            salon.add_appointment(appointment)

            if appointment.status == AppointmentStatus.BOOKED:
                appointment.hairdresser.book_time(appointment.time)
                appointment.chair.book_time(appointment.time)
                appointment.mirror.book_time(appointment.time)

        return salon
