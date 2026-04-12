from abc import ABC
from dataclasses import dataclass


@dataclass
class Person(ABC):
    id: int
    name: str