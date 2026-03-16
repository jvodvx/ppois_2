from datetime import datetime

from ..domain.salon import Salon
from ..domain.client import Client
from ..domain.master import Master
from ..domain.service import Service
from ..domain.appointment import Appointment
from ..infrastructure.salon_repository import SalonRepository

from ..exceptions import NotFoundError, BookingError

class SalonManager:

    def __init__(self, salon: Salon):

        self.salon = salon
        self.repo = SalonRepository()
        self.client_id = self._next_id(self.salon.clients)
        self.master_id = self._next_id(self.salon.masters)
        self.service_id = self._next_id(self.salon.services)
        self.appointment_id = self._next_id(self.salon.appointments)

    def _next_id(self, items):

        if not items:
            return 1

        return max(item.id for item in items) + 1

    def create_client(self, name: str, phone: str) -> Client:
        client = Client(self.client_id, name, phone)
        self.client_id += 1
        self.salon.add_client(client)
        self.repo.save(self.salon)
        return client

    def create_master(self, name: str, service_ids: list[int]) -> Master:

        master = Master(self.master_id, name)

        for sid in service_ids:

            service = next(
                (s for s in self.salon.services if s.id == sid),
                None
            )

            if service:
                master.add_service(service)

        self.master_id += 1

        self.salon.add_master(master)

        self.repo.save(self.salon)

        return master

    def create_service(self, name: str, duration: int, price: float) -> Service:
        service = Service(self.service_id, name, duration, price)
        self.service_id += 1
        self.salon.add_service(service)
        self.repo.save(self.salon)
        return service

    def book_appointment(
            self,
            client_id: int,
            master_id: int,
            service_id: int,
            time: datetime,
    ) -> Appointment:

        client = next(
            (c for c in self.salon.clients if c.id == client_id),
            None
        )
        if not client:
            raise NotFoundError("Client not found")

        master = next(
            (m for m in self.salon.masters if m.id == master_id),
            None
        )
        if not master:
            raise NotFoundError("Master not found")

        service = next(
            (s for s in self.salon.services if s.id == service_id),
            None
        )
        if not service:
            raise NotFoundError("Service not found")

        if not master.can_do_service(service):
            raise BookingError("Master cannot perform this service")

        if not master.is_available(time):
            raise BookingError("Master is busy at this time")

        appointment = Appointment(
            self.appointment_id,
            client,
            master,
            service,
            time,
        )

        self.appointment_id += 1

        self.salon.add_appointment(appointment)

        master.book_time(time)

        if hasattr(self, "repo"):
            self.repo.save(self.salon)

        return appointment

    def cancel_appointment(self, appointment_id: int):

        appointment = next(
            (a for a in self.salon.appointments if a.id == appointment_id),
            None,
        )

        if not appointment:
            raise NotFoundError("Appointment not found")

        appointment.cancel()

    def list_appointments(self):
        return self.salon.appointments