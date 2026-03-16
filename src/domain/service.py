from dataclasses import dataclass
from ..exceptions import ValidationError

@dataclass
class Service:
    id: int
    name: str
    duration: int
    price: float

    def __post_init__(self):
        if self.duration <= 0:
            raise ValidationError("Service duration must be positive")

        if self.price < 0:
            raise ValidationError("Service price cannot be negative")