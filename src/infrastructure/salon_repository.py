import json
from datetime import datetime
from pathlib import Path

from ..domain.client import Client
from ..domain.master import Master
from ..domain.service import Service
from ..domain.appointment import Appointment, AppointmentStatus
from ..domain.salon import Salon


class SalonRepository:

    def __init__(self, filename: str = "salon_data.json"):
        self.filename = Path(filename)

    def save(self, salon: Salon, filename: str | None = None):
        target = Path(filename) if filename is not None else self.filename

        data = {
            "clients": [
                {"id": c.id, "name": c.name, "phone": c.phone}
                for c in salon.clients
            ],
            "masters": [
                {
                    "id": m.id,
                    "name": m.name,
                    "services": [s.id for s in m.services]
                }
                for m in salon.masters
            ],
            "services": [
                {
                    "id": s.id,
                    "name": s.name,
                    "duration": s.duration,
                    "price": s.price,
                }
                for s in salon.services
            ],
            "appointments": [
                {
                    "id": a.id,
                    "client": a.client.id,
                    "master": a.master.id,
                    "service": a.service.id,
                    "time": a.time.isoformat(),
                    "status": a.status.value,
                }
                for a in salon.appointments
            ],
        }

        with target.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load(self, filename: str | None = None) -> Salon:
        target = Path(filename) if filename is not None else self.filename
        salon = Salon()

        try:
            with target.open(encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return salon

        clients = {}
        masters = {}
        services = {}

        for c in data.get("clients", []):
            client = Client(c["id"], c["name"], c["phone"])
            salon.clients.append(client)
            clients[c["id"]] = client

        for s in data.get("services", []):
            service = Service(s["id"], s["name"], s["duration"], s["price"])
            salon.services.append(service)
            services[s["id"]] = service

        for m in data.get("masters", []):

            master = Master(m["id"], m["name"])
            masters[m["id"]] = master
            salon.masters.append(master)

            for service_id in m.get("services", []):
                service = services.get(service_id)

                if service:
                    master.add_service(service)

        for a in data.get("appointments", []):
            appointment = Appointment(
                a["id"],
                clients[a["client"]],
                masters[a["master"]],
                services[a["service"]],
                datetime.fromisoformat(a["time"]),
                AppointmentStatus(a.get("status", AppointmentStatus.CREATED.value)),
            )

            salon.appointments.append(appointment)

            if appointment.status == AppointmentStatus.CREATED:
                appointment.master.book_time(appointment.time)

        return salon
