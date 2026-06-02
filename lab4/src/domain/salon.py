from typing import List

from .client import Client
from .chair import Chair
from .hairdresser import Hairdresser
from .mirror import Mirror
from .service import Service
from .appointment import Appointment
from .tool import Tool


class Salon:

    def __init__(self):
        self.clients: List[Client] = []
        self.hairdressers: List[Hairdresser] = []
        self.services: List[Service] = []
        self.tools: List[Tool] = []
        self.mirrors: List[Mirror] = []
        self.chairs: List[Chair] = []
        self.appointments: List[Appointment] = []

    def add_client(self, client: Client) -> None:
        self.clients.append(client)

    def add_hairdresser(self, hairdresser: Hairdresser) -> None:
        self.hairdressers.append(hairdresser)

    def add_service(self, service: Service) -> None:
        self.services.append(service)

    def add_tool(self, tool: Tool) -> None:
        self.tools.append(tool)

    def add_mirror(self, mirror: Mirror) -> None:
        self.mirrors.append(mirror)

    def add_chair(self, chair: Chair) -> None:
        self.chairs.append(chair)

    def add_appointment(self, appointment: Appointment) -> None:
        self.appointments.append(appointment)
