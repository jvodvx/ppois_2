from datetime import datetime

from ..application.salon_manager import SalonManager
from ..exceptions import SalonError


class SalonCLI:

    def __init__(self, manager: SalonManager):
        self.manager = manager

    def run(self) -> None:
        while True:
            print("\n--- Hairdresser System ---")
            print("1 Add client")
            print("2 Add hairdresser")
            print("3 Show services")
            print("4 Add tool")
            print("5 Add mirror")
            print("6 Add chair")
            print("7 Book appointment")
            print("8 Complete booking")
            print("9 Pay for service")
            print("10 Show client bookings")
            print("11 Cancel booking")
            print("0 Exit")

            choice = input("Choose action: ")

            try:
                if choice == "1":
                    self.add_client()
                elif choice == "2":
                    self.add_hairdresser()
                elif choice == "3":
                    self.show_services()
                elif choice == "4":
                    self.add_tool()
                elif choice == "5":
                    self.add_mirror()
                elif choice == "6":
                    self.add_chair()
                elif choice == "7":
                    self.book_haircut()
                elif choice == "8":
                    self.complete_booking()
                elif choice == "9":
                    self.pay_for_service()
                elif choice == "10":
                    self.show_client_bookings()
                elif choice == "11":
                    self.cancel_booking()
                elif choice == "0":
                    break
            except SalonError as error:
                print("Error:", error)
            except ValueError:
                print("Invalid input")
            except Exception as error:
                print("Unexpected error:", error)

    def show_clients(self) -> None:
        print("\nClients:")
        if not self.manager.salon.clients:
            print("No clients available")
            return

        print("ID | Name | Phone")
        for client in self.manager.salon.clients:
            print(f"{client.id} | {client.name} | {client.phone}")

    def show_hairdressers(self) -> None:
        print("\nHairdressers:")
        if not self.manager.salon.hairdressers:
            print("No hairdressers available")
            return

        print("ID | Name | Services | Tools")
        for hairdresser in self.manager.salon.hairdressers:
            service_names = ", ".join(service.name for service in hairdresser.services)
            tool_names = ", ".join(tool.name for tool in hairdresser.tools)
            print(
                f"{hairdresser.id} | "
                f"{hairdresser.name} | "
                f"{service_names or '-'} | "
                f"{tool_names or '-'}"
            )

    def show_services(self) -> None:
        print("\nServices:")
        if not self.manager.salon.services:
            print("No services available")
            return

        print("ID | Name | Duration | Price")
        for service in self.manager.salon.services:
            print(
                f"{service.id} | "
                f"{service.name} | "
                f"{service.duration} min | "
                f"{service.price}"
            )

    def show_tools(self) -> None:
        print("\nTools:")
        if not self.manager.salon.tools:
            print("No tools available")
            return

        print("ID | Name")
        for tool in self.manager.salon.tools:
            print(f"{tool.id} | {tool.name}")

    def show_mirrors(self) -> None:
        print("\nMirrors:")
        if not self.manager.salon.mirrors:
            print("No mirrors available")
            return

        print("ID | Label")
        for mirror in self.manager.salon.mirrors:
            print(f"{mirror.id} | {mirror.label}")

    def show_chairs(self) -> None:
        print("\nChairs:")
        if not self.manager.salon.chairs:
            print("No chairs available")
            return

        print("ID | Label")
        for chair in self.manager.salon.chairs:
            print(f"{chair.id} | {chair.label}")

    def add_client(self) -> None:
        name = input("Client name: ")
        phone = input("Phone: ")
        client = self.manager.create_client(name, phone)
        print("Client created:", client)

    def add_hairdresser(self) -> None:
        name = input("Hairdresser name: ")
        self.show_services()
        service_ids = self.read_ids("Enter service IDs (comma separated): ")
        self.show_tools()
        tool_ids = self.read_ids("Enter tool IDs (comma separated): ")
        hairdresser = self.manager.create_hairdresser(name, service_ids, tool_ids)
        print("Hairdresser created:", hairdresser.name)

    def add_tool(self) -> None:
        tool = self.manager.create_tool(input("Tool name: "))
        print("Tool created:", tool)

    def add_mirror(self) -> None:
        mirror = self.manager.create_mirror(input("Mirror label: "))
        print("Mirror created:", mirror)

    def add_chair(self) -> None:
        chair = self.manager.create_chair(input("Chair label: "))
        print("Chair created:", chair)

    def book_haircut(self) -> None:
        if not self.manager.salon.clients:
            print("No clients available")
            return
        if not self.manager.salon.hairdressers:
            print("No hairdressers available")
            return
        if not self.manager.salon.services:
            print("No services available")
            return
        if not self.manager.salon.chairs:
            print("No chairs available")
            return
        if not self.manager.salon.mirrors:
            print("No mirrors available")
            return

        self.show_clients()
        client_id = self.read_int("\nEnter client id: ")
        self.show_hairdressers()
        hairdresser_id = self.read_int("\nEnter hairdresser id: ")
        self.show_services()
        service_id = self.read_int("\nEnter service id: ")
        self.show_chairs()
        chair_id = self.read_int("\nEnter chair id: ")
        self.show_mirrors()
        mirror_id = self.read_int("\nEnter mirror id: ")
        time = self.read_datetime("Time (YYYY-MM-DD HH:MM): ")

        appointment = self.manager.book_haircut(
            client_id,
            hairdresser_id,
            service_id,
            chair_id,
            mirror_id,
            time,
        )
        print("Booking created:", appointment.id)

    def complete_booking(self) -> None:
        self.show_appointments()
        appointment_id = self.read_int("Enter booking id: ")
        appointment = self.manager.list_appointments()
        selected = next((item for item in appointment if item.id == appointment_id), None)

        if selected is None:
            print("Booking not found")
            return

        if selected.service.name == "Consultation":
            notes = input("Consultation notes: ")
            completed = self.manager.complete_appointment(
                appointment_id,
                notes=notes,
            )
        else:
            self.show_tools()
            tool_ids = self.read_ids("Enter used tool IDs (comma separated): ")
            completed = self.manager.complete_appointment(
                appointment_id,
                tool_ids=tool_ids,
            )

        print("Service completed for booking:", completed.id)

    def pay_for_service(self) -> None:
        self.show_appointments()
        appointment_id = self.read_int("Enter booking id: ")
        amount = self.manager.pay_for_service(appointment_id)
        print(f"Payment accepted: {amount}")

    def show_client_bookings(self) -> None:
        self.show_clients()
        client_id = self.read_int("Enter client id: ")
        self.show_appointments(client_id)

    def show_appointments(self, client_id: int | None = None) -> None:
        appointments = self.manager.list_appointments(client_id)
        print("\nBookings:")
        if not appointments:
            print("No bookings")
            return

        print("ID | Client | Hairdresser | Service | Chair | Mirror | Time | Status | Paid")
        for appointment in appointments:
            print(
                f"{appointment.id} | "
                f"{appointment.client.name} | "
                f"{appointment.hairdresser.name} | "
                f"{appointment.service.name} | "
                f"{appointment.chair.label} | "
                f"{appointment.mirror.label} | "
                f"{appointment.time} | "
                f"{appointment.status.value} | "
                f"{appointment.paid}"
            )

    def cancel_booking(self) -> None:
        self.show_appointments()
        appointment_id = self.read_int("Enter booking id: ")
        self.manager.cancel_appointment(appointment_id)
        print("Booking cancelled")

    def read_int(self, message: str) -> int:
        while True:
            try:
                return int(input(message))
            except ValueError:
                print("Please enter a valid number")

    def read_datetime(self, message: str) -> datetime:
        while True:
            try:
                return datetime.strptime(input(message), "%Y-%m-%d %H:%M")
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD HH:MM")

    def read_ids(self, message: str) -> list[int]:
        raw_value = input(message).strip()
        if not raw_value:
            return []

        return [int(value.strip()) for value in raw_value.split(",") if value.strip()]
