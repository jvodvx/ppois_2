from src.infrastructure.salon_repository import SalonRepository
from src.application.salon_manager import SalonManager
from src.presentation.cli_handlers import SalonCLI


def main():
    repo = SalonRepository()
    salon = repo.load()

    manager = SalonManager(salon, repo)

    cli = SalonCLI(manager)

    try:
        cli.run()
    finally:
        repo.save(salon)


if __name__ == "__main__":
    main()
