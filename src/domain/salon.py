from typing import List

from .client import Client
from .master import Master
from .service import Service
from .appointment import Appointment


class Salon:

    def __init__(self):
        self.clients: List[Client] = []
        self.masters: List[Master] = []
        self.services: List[Service] = []
        self.appointments: List[Appointment] = []

    def add_client(self, client: Client) -> None:
        self.clients.append(client)

    def add_master(self, master: Master) -> None:
        self.masters.append(master)

    def add_service(self, service: Service) -> None:
        self.services.append(service)

    def add_appointment(self, appointment: Appointment) -> None:
        self.appointments.append(appointment)