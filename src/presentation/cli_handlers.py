from datetime import datetime

from ..application.salon_manager import SalonManager
from ..exceptions import SalonError


class SalonCLI:

    def __init__(self, manager: SalonManager):
        self.manager = manager

    def run(self):

        while True:

            print("\n--- Hair Salon System ---")
            print("1 Add client")
            print("2 Add master")
            print("3 Add service")
            print("4 Book appointment")
            print("5 Show appointments")
            print("6 Cancel appointment")
            print("7 Complete appointment")
            print("0 Exit")

            choice = input("Choose action: ")

            try:

                if choice == "1":
                    self.add_client()

                elif choice == "2":
                    self.add_master()

                elif choice == "3":
                    self.add_service()

                elif choice == "4":
                    self.book_appointment()

                elif choice == "5":
                    self.show_appointments()

                elif choice == "6":
                    self.cancel_appointment()

                elif choice == "7":
                    self.complete_appointment()

                elif choice == "0":
                    break

            except SalonError as e:
                print("Error:", e)

            except ValueError:
                print("Invalid input")

            except Exception as e:
                print("Unexpected error:", e)

    def show_clients(self):

        print("\nClients:")

        if not self.manager.salon.clients:
            print("No clients available")
            return

        print("ID | Name | Phone")

        for c in self.manager.salon.clients:
            print(f"{c.id} | {c.name} | {c.phone}")

    def show_masters(self):

        print("\nMasters:")

        if not self.manager.salon.masters:
            print("No masters available")
            return

        print("ID | Name")

        for m in self.manager.salon.masters:
            print(f"{m.id} | {m.name}")

    def show_services(self):

        print("\nServices:")

        if not self.manager.salon.services:
            print("No services available")
            return

        print("ID | Name | Duration | Price")

        for s in self.manager.salon.services:
            print(f"{s.id} | {s.name} | {s.duration} min | {s.price}")

    def add_client(self):

        name = input("Client name: ")
        phone = input("Phone: ")

        client = self.manager.create_client(name, phone)

        print("Client created:", client)

    def add_master(self):

        name = input("Master name: ")

        self.show_services()

        services_input = input(
            "Enter service IDs (comma separated): "
        )

        service_ids = [
            int(x.strip()) for x in services_input.split(",")
        ]

        master = self.manager.create_master(name, service_ids)

        print("Master created:", master.name)

    def add_service(self):

        name = input("Service name: ")
        duration = self.read_int("Duration minutes: ")

        while True:
            try:
                price = float(input("Price: "))
                break
            except ValueError:
                print("Enter a valid price")

        service = self.manager.create_service(name, duration, price)

        print("Service created:", service)

    def book_appointment(self):
        if not self.manager.salon.clients:
            print("No clients available")
            return

        if not self.manager.salon.masters:
            print("No masters available")
            return

        if not self.manager.salon.services:
            print("No services available")
            return
        self.show_clients()
        client_id = self.read_int("\nEnter client id: ")

        if not any(c.id == client_id for c in self.manager.salon.clients):
            print("Client not found")
            return

        self.show_masters()
        master_id = self.read_int("\nEnter master id: ")

        if not any(m.id == master_id for m in self.manager.salon.masters):
            print("Master not found")
            return

        self.show_services()
        service_id = self.read_int("\nEnter service id: ")

        if not any(s.id == service_id for s in self.manager.salon.services):
            print("Service not found")
            return

        time = self.read_datetime("Time (YYYY-MM-DD HH:MM): ")

        appointment = self.manager.book_appointment(
            client_id,
            master_id,
            service_id,
            time,
        )

        print("Appointment created")

    def show_appointments(self):

        print("\nAppointments:")

        if not self.manager.salon.appointments:
            print("No appointments")
            return

        print("ID | Client | Master | Service | Time | Status")

        for a in self.manager.list_appointments():
            print(
                f"{a.id} | "
                f"{a.client.name} | "
                f"{a.master.name} | "
                f"{a.service.name} | "
                f"{a.time} | "
                f"{a.status.value}"
            )

    def cancel_appointment(self):
        self.show_appointments()
        appointment_id = int(input("Appointment id: "))
        self.manager.cancel_appointment(appointment_id)

        print("Appointment cancelled")

    def complete_appointment(self):

        self.show_appointments()

        appointment_id = self.read_int("Enter appointment id: ")

        self.manager.complete_appointment(appointment_id)

        print("Appointment completed")

    def read_int(self, message: str) -> int:
        while True:
            try:
                return int(input(message))
            except ValueError:
                print("Please enter a valid number")

    def read_datetime(self, message: str) -> datetime:
        while True:
            try:
                value = input(message)
                return datetime.strptime(value, "%Y-%m-%d %H:%M")
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD HH:MM")