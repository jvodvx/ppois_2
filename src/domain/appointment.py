from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .client import Client
from .chair import Chair
from .hairdresser import Hairdresser
from .mirror import Mirror
from .service import Service
from .tool import Tool
from ..exceptions import BookingError, PaymentError, ValidationError


class AppointmentStatus(Enum):
    BOOKED = "booked"
    SERVICED = "serviced"
    CANCELLED = "cancelled"


@dataclass
class Appointment:
    id: int
    client: Client
    hairdresser: Hairdresser
    service: Service
    chair: Chair
    mirror: Mirror
    time: datetime
    consultation_notes: str = ""
    used_tools: list[Tool] = field(default_factory=list)
    status: AppointmentStatus = AppointmentStatus.BOOKED
    paid: bool = False
    payment_amount: float = 0.0

    def cancel(self) -> None:
        if self.status != AppointmentStatus.BOOKED:
            raise BookingError("Cannot cancel appointment")
        self.status = AppointmentStatus.CANCELLED

    def perform_service(self, tools: list[Tool]) -> None:
        if self.status != AppointmentStatus.BOOKED:
            raise BookingError("Cannot perform service for this appointment")

        if not tools:
            raise ValidationError("At least one tool is required")

        self.used_tools = list(tools)
        self.status = AppointmentStatus.SERVICED

    def add_consultation(self, notes: str) -> None:
        if not notes.strip():
            raise ValidationError("Consultation notes cannot be empty")

        self.consultation_notes = notes

    def pay(self) -> float:
        if self.status != AppointmentStatus.SERVICED:
            raise PaymentError("Cannot accept payment before service is completed")

        if self.paid:
            raise PaymentError("Appointment is already paid")

        self.paid = True
        self.payment_amount = self.service.price
        return self.payment_amount
