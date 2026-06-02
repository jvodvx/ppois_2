from pathlib import Path

from .application.salon_manager import SalonManager
from .infrastructure.salon_repository import SalonRepository


def build_manager(data_file: str = "salon_data.json") -> SalonManager:
    repository = SalonRepository(Path(data_file))
    salon = repository.load()
    return SalonManager(salon, repository)
