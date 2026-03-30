from datetime import datetime, timedelta
from typing import Iterable, Optional

from ..domain.salon import Salon
from ..domain.client import Client
from ..domain.master import Master
from ..domain.service import Service
from ..domain.appointment import Appointment, AppointmentStatus
from ..infrastructure.salon_repository import SalonRepository

from ..exceptions import NotFoundError, BookingError

class SalonManager:

    def __init__(
        self,
        salon: Salon,
        repo: Optional[SalonRepository] = None,
    ):
        self.salon = salon
        self.repo = repo
        self.client_id = self._next_id(self.salon.clients)
        self.master_id = self._next_id(self.salon.masters)
        self.service_id = self._next_id(self.salon.services)
        self.appointment_id = self._next_id(self.salon.appointments)

    def _next_id(self, items: Iterable[object]) -> int:
        if not items:
            return 1

        return max(item.id for item in items) + 1

    def _save(self) -> None:
        if self.repo is not None:
            self.repo.save(self.salon)

    @staticmethod
    def _find_by_id(items: Iterable[object], item_id: int):
        return next((item for item in items if item.id == item_id), None)

    def _master_has_time_conflict(
        self,
        master: Master,
        service: Service,
        time: datetime,
    ) -> bool:
        new_end = time + timedelta(minutes=service.duration)

        for appointment in self.salon.appointments:
            if appointment.master.id != master.id:
                continue

            if appointment.status != AppointmentStatus.CREATED:
                continue

            current_start = appointment.time
            current_end = current_start + timedelta(
                minutes=appointment.service.duration
            )

            if time < current_end and current_start < new_end:
                return True

        return False

    def create_client(self, name: str, phone: str) -> Client:
        client = Client(self.client_id, name, phone)
        self.client_id += 1
        self.salon.add_client(client)
        self._save()
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

        self._save()

        return master

    def create_service(self, name: str, duration: int, price: float) -> Service:
        service = Service(self.service_id, name, duration, price)
        self.service_id += 1
        self.salon.add_service(service)
        self._save()
        return service

    def book_appointment(
            self,
            client_id: int,
            master_id: int,
            service_id: int,
            time: datetime,
    ) -> Appointment:

        client = self._find_by_id(self.salon.clients, client_id)
        if not client:
            raise NotFoundError("Client not found")

        master = self._find_by_id(self.salon.masters, master_id)
        if not master:
            raise NotFoundError("Master not found")

        service = self._find_by_id(self.salon.services, service_id)
        if not service:
            raise NotFoundError("Service not found")

        if not master.can_do_service(service):
            raise BookingError("Master cannot perform this service")

        if self._master_has_time_conflict(master, service, time):
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

        self._save()

        return appointment

    def cancel_appointment(self, appointment_id: int) -> None:
        appointment = self._find_by_id(self.salon.appointments, appointment_id)

        if not appointment:
            raise NotFoundError("Appointment not found")

        appointment.cancel()
        appointment.master.release_time(appointment.time)
        self._save()

    def list_appointments(self):
        return self.salon.appointments

    def complete_appointment(self, appointment_id: int) -> None:
        appointment = self._find_by_id(self.salon.appointments, appointment_id)

        if not appointment:
            raise NotFoundError("Appointment not found")

        appointment.complete()
        appointment.master.release_time(appointment.time)
        self._save()
