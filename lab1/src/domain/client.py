from dataclasses import dataclass
from .person import Person
from ..exceptions import ValidationError


@dataclass
class Client(Person):
    phone: str

    def update_phone(self, phone: str) -> None:
        if not phone.strip():
            raise ValidationError("Phone cannot be empty")

        self.phone = phone