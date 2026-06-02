from dataclasses import dataclass, field
from datetime import datetime

from ..exceptions import ScheduleError, ValidationError


@dataclass
class Mirror:
    id: int
    label: str
    schedule: list[datetime] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValidationError("Mirror label cannot be empty")

    def is_available(self, time: datetime) -> bool:
        return time not in self.schedule

    def book_time(self, time: datetime) -> None:
        if time in self.schedule:
            raise ScheduleError("Mirror is already occupied at this time")

        self.schedule.append(time)

    def release_time(self, time: datetime) -> None:
        if time in self.schedule:
            self.schedule.remove(time)
