import json
from datetime import datetime

from ..domain.client import Client
from ..domain.master import Master
from ..domain.service import Service
from ..domain.appointment import Appointment
from ..domain.salon import Salon


class SalonRepository:

    def save(self, salon: Salon, filename="salon_data.json"):

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

        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def load(self, filename="salon_data.json") -> Salon:

        salon = Salon()

        try:
            with open(filename) as f:
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
            )

            salon.appointments.append(appointment)

        return salon