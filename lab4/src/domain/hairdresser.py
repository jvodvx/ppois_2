from dataclasses import dataclass, field
from datetime import datetime

from .person import Person
from .service import Service
from .tool import Tool
from ..exceptions import ScheduleError


@dataclass
class Hairdresser(Person):
    services: list[Service] = field(default_factory=list)
    tools: list[Tool] = field(default_factory=list)
    schedule: list[datetime] = field(default_factory=list)

    def add_service(self, service: Service) -> None:
        if service not in self.services:
            self.services.append(service)

    def add_tool(self, tool: Tool) -> None:
        if tool not in self.tools:
            self.tools.append(tool)

    def can_do_service(self, service: Service) -> bool:
        return service in self.services

    def has_tools(self, tools: list[Tool]) -> bool:
        return all(tool in self.tools for tool in tools)

    def is_available(self, time: datetime) -> bool:
        return time not in self.schedule

    def book_time(self, time: datetime) -> None:
        if time in self.schedule:
            raise ScheduleError("Hairdresser is busy at this time")

        self.schedule.append(time)

    def release_time(self, time: datetime) -> None:
        if time in self.schedule:
            self.schedule.remove(time)
