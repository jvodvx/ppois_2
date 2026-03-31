from datetime import datetime, timedelta
from typing import Iterable, Optional

from ..domain.appointment import Appointment, AppointmentStatus
from ..domain.chair import Chair
from ..domain.client import Client
from ..domain.hairdresser import Hairdresser
from ..domain.mirror import Mirror
from ..domain.salon import Salon
from ..domain.service import Service
from ..domain.tool import Tool
from ..exceptions import BookingError, NotFoundError
from ..infrastructure.salon_repository import SalonRepository


class SalonManager:
    DEFAULT_SERVICES: list[tuple[str, int, float]] = [
        ("Haircut", 30, 25.0),
        ("Styling", 40, 20.0),
        ("Consultation", 20, 15.0),
    ]
    CONSULTATION_SERVICE_NAME = "Consultation"
    TOOL_BASED_SERVICES = {"Haircut", "Styling"}

    def __init__(
        self,
        salon: Salon,
        repo: Optional[SalonRepository] = None,
    ):
        self.salon = salon
        self.repo = repo
        self.client_id = self._next_id(self.salon.clients)
        self.hairdresser_id = self._next_id(self.salon.hairdressers)
        self.service_id = self._next_id(self.salon.services)
        self.tool_id = self._next_id(self.salon.tools)
        self.mirror_id = self._next_id(self.salon.mirrors)
        self.chair_id = self._next_id(self.salon.chairs)
        self.appointment_id = self._next_id(self.salon.appointments)
        self._ensure_default_services()

    @staticmethod
    def _next_id(items: Iterable[object]) -> int:
        items_list = list(items)

        if not items_list:
            return 1

        return max(item.id for item in items_list) + 1

    def _save(self) -> None:
        if self.repo is not None:
            self.repo.save(self.salon)

    def _ensure_default_services(self) -> None:
        if self.salon.services:
            return

        for name, duration, price in self.DEFAULT_SERVICES:
            service = Service(self.service_id, name, duration, price)
            self.salon.add_service(service)
            self.service_id += 1

        self._save()

    @staticmethod
    def _find_by_id(items: Iterable[object], item_id: int):
        return next((item for item in items if item.id == item_id), None)

    def _complete_appointment(self, appointment: Appointment) -> Appointment:
        appointment.complete()
        appointment.hairdresser.release_time(appointment.time)
        appointment.chair.release_time(appointment.time)
        appointment.mirror.release_time(appointment.time)
        self._save()
        return appointment

    def _get_appointment(self, appointment_id: int) -> Appointment:
        appointment = self._find_by_id(self.salon.appointments, appointment_id)
        if appointment is None:
            raise NotFoundError("Appointment not found")

        return appointment

    @staticmethod
    def _appointments_overlap(
        current_start: datetime,
        current_duration: int,
        requested_start: datetime,
        requested_duration: int,
    ) -> bool:
        current_end = current_start + timedelta(minutes=current_duration)
        requested_end = requested_start + timedelta(minutes=requested_duration)
        return requested_start < current_end and current_start < requested_end

    def _has_time_conflict(
        self,
        time: datetime,
        service: Service,
        hairdresser: Hairdresser,
        chair: Chair,
        mirror: Mirror,
    ) -> bool:
        for appointment in self.salon.appointments:
            if appointment.status != AppointmentStatus.BOOKED:
                continue

            if not self._appointments_overlap(
                appointment.time,
                appointment.service.duration,
                time,
                service.duration,
            ):
                continue

            if appointment.hairdresser.id == hairdresser.id:
                return True

            if appointment.chair.id == chair.id:
                return True

            if appointment.mirror.id == mirror.id:
                return True

        return False

    def create_client(self, name: str, phone: str) -> Client:
        client = Client(self.client_id, name, phone)
        self.client_id += 1
        self.salon.add_client(client)
        self._save()
        return client

    def create_hairdresser(
        self,
        name: str,
        service_ids: list[int],
        tool_ids: list[int],
    ) -> Hairdresser:
        hairdresser = Hairdresser(self.hairdresser_id, name)

        for service_id in service_ids:
            service = self._find_by_id(self.salon.services, service_id)
            if service is None:
                raise NotFoundError("Service not found")
            hairdresser.add_service(service)

        for tool_id in tool_ids:
            tool = self._find_by_id(self.salon.tools, tool_id)
            if tool is None:
                raise NotFoundError("Tool not found")
            hairdresser.add_tool(tool)

        self.hairdresser_id += 1
        self.salon.add_hairdresser(hairdresser)
        self._save()
        return hairdresser

    def get_service_by_name(self, name: str) -> Service:
        service = next(
            (item for item in self.salon.services if item.name == name),
            None,
        )
        if service is None:
            raise NotFoundError("Service not found")

        return service

    def create_tool(self, name: str) -> Tool:
        tool = Tool(self.tool_id, name)
        self.tool_id += 1
        self.salon.add_tool(tool)
        self._save()
        return tool

    def create_mirror(self, label: str) -> Mirror:
        mirror = Mirror(self.mirror_id, label)
        self.mirror_id += 1
        self.salon.add_mirror(mirror)
        self._save()
        return mirror

    def create_chair(self, label: str) -> Chair:
        chair = Chair(self.chair_id, label)
        self.chair_id += 1
        self.salon.add_chair(chair)
        self._save()
        return chair

    def book_haircut(
        self,
        client_id: int,
        hairdresser_id: int,
        service_id: int,
        chair_id: int,
        mirror_id: int,
        time: datetime,
    ) -> Appointment:
        client = self._find_by_id(self.salon.clients, client_id)
        if client is None:
            raise NotFoundError("Client not found")

        hairdresser = self._find_by_id(self.salon.hairdressers, hairdresser_id)
        if hairdresser is None:
            raise NotFoundError("Hairdresser not found")

        service = self._find_by_id(self.salon.services, service_id)
        if service is None:
            raise NotFoundError("Service not found")

        chair = self._find_by_id(self.salon.chairs, chair_id)
        if chair is None:
            raise NotFoundError("Chair not found")

        mirror = self._find_by_id(self.salon.mirrors, mirror_id)
        if mirror is None:
            raise NotFoundError("Mirror not found")

        if not hairdresser.can_do_service(service):
            raise BookingError("Hairdresser cannot perform this service")

        if self._has_time_conflict(time, service, hairdresser, chair, mirror):
            raise BookingError("Selected time slot is not available")

        appointment = Appointment(
            id=self.appointment_id,
            client=client,
            hairdresser=hairdresser,
            service=service,
            chair=chair,
            mirror=mirror,
            time=time,
        )

        self.appointment_id += 1
        self.salon.add_appointment(appointment)

        hairdresser.book_time(time)
        chair.book_time(time)
        mirror.book_time(time)
        self._save()

        return appointment

    def perform_haircut_and_styling(
        self,
        appointment_id: int,
        tool_ids: list[int],
    ) -> Appointment:
        return self.complete_appointment(appointment_id, tool_ids=tool_ids)

    def complete_appointment(
        self,
        appointment_id: int,
        tool_ids: Optional[list[int]] = None,
        notes: str = "",
    ) -> Appointment:
        appointment = self._get_appointment(appointment_id)
        service_name = appointment.service.name

        if service_name in self.TOOL_BASED_SERVICES:
            tools: list[Tool] = []
            for tool_id in tool_ids or []:
                tool = self._find_by_id(self.salon.tools, tool_id)
                if tool is None:
                    raise NotFoundError("Tool not found")
                tools.append(tool)

            if not appointment.hairdresser.has_tools(tools):
                raise BookingError("Hairdresser does not have the selected tools")

            appointment.perform_service(tools)
            return self._complete_appointment(appointment)

        if service_name == self.CONSULTATION_SERVICE_NAME:
            appointment.add_consultation(notes)
            return self._complete_appointment(appointment)

        raise BookingError("Unsupported service type")

    def provide_hair_care_consultation(
        self,
        appointment_id: int,
        notes: str,
    ) -> Appointment:
        return self.complete_appointment(appointment_id, notes=notes)

    def pay_for_service(self, appointment_id: int) -> float:
        appointment = self._get_appointment(appointment_id)
        amount = appointment.pay()
        self._save()
        return amount

    def cancel_appointment(self, appointment_id: int) -> None:
        appointment = self._get_appointment(appointment_id)
        appointment.cancel()
        appointment.hairdresser.release_time(appointment.time)
        appointment.chair.release_time(appointment.time)
        appointment.mirror.release_time(appointment.time)
        self._save()

    def list_appointments(self, client_id: int | None = None) -> list[Appointment]:
        if client_id is None:
            return self.salon.appointments

        return [
            appointment
            for appointment in self.salon.appointments
            if appointment.client.id == client_id
        ]
