from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from .person import Person
from .service import Service
from ..exceptions import ScheduleError


@dataclass
class Master(Person):
    services: List[Service] = field(default_factory=list)
    schedule: List[datetime] = field(default_factory=list)

    def add_service(self, service: Service):

        if service not in self.services:
            self.services.append(service)

    def can_do_service(self, service: Service) -> bool:
        return service in self.services

    def is_available(self, time: datetime) -> bool:
        return time not in self.schedule

    def book_time(self, time: datetime):
        if time in self.schedule:
            raise ScheduleError("This time slot is already booked")

        self.schedule.append(time)