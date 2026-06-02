from src.bootstrap import build_manager
from src.presentation.cli_handlers import SalonCLI


def main() -> None:
    manager = build_manager()
    cli = SalonCLI(manager)
    cli.run()


if __name__ == "__main__":
    main()
