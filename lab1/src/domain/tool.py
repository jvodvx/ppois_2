from dataclasses import dataclass

from ..exceptions import ValidationError


@dataclass
class Tool:
    id: int
    name: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError("Tool name cannot be empty")
