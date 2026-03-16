from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .client import Client
from .master import Master
from .service import Service


class AppointmentStatus(Enum):
    CREATED = "created"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Appointment:
    id: int
    client: Client
    master: Master
    service: Service
    time: datetime
    status: AppointmentStatus = AppointmentStatus.CREATED

    def cancel(self) -> None:
        if self.status != AppointmentStatus.CREATED:
            raise ValueError("Cannot cancel appointment")
        self.status = AppointmentStatus.CANCELLED

    def complete(self) -> None:
        if self.status != AppointmentStatus.CREATED:
            raise ValueError("Cannot complete appointment")
        self.status = AppointmentStatus.COMPLETED