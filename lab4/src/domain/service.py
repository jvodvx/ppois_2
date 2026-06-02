from dataclasses import dataclass

from ..exceptions import ValidationError


@dataclass
class Service:
    TOOL_BASED = "tool_based"
    CONSULTATION = "consultation"
    EXECUTION_MODES = {TOOL_BASED, CONSULTATION}

    id: int
    name: str
    duration: int
    price: float
    execution_mode: str = TOOL_BASED

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError("Service name cannot be empty")

        if self.duration <= 0:
            raise ValidationError("Service duration must be positive")

        if self.price < 0:
            raise ValidationError("Service price cannot be negative")

        if self.execution_mode not in self.EXECUTION_MODES:
            raise ValidationError("Unsupported service execution mode")

    @property
    def requires_tools(self) -> bool:
        return self.execution_mode == self.TOOL_BASED

    @property
    def requires_notes(self) -> bool:
        return self.execution_mode == self.CONSULTATION

    @classmethod
    def default_execution_mode(cls, service_name: str) -> str:
        return cls.CONSULTATION if service_name == "Consultation" else cls.TOOL_BASED
