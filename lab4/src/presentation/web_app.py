from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

from ..application.salon_manager import SalonManager
from ..exceptions import SalonError


def create_app(manager: SalonManager) -> Flask:
    project_root = Path(__file__).resolve().parents[2]
    app = Flask(
        __name__,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )
    app.config["SECRET_KEY"] = "ppois-lab4-secret-key"

    @app.template_filter("datetime_local")
    def datetime_local(value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M")

    def redirect_to_index(anchor: str = ""):
        return redirect(url_for("index", _anchor=anchor or None))

    def get_min_booking_time() -> str:
        now = datetime.now().replace(second=0, microsecond=0)
        if now.hour >= manager.WORKDAY_END_HOUR:
            next_slot = now.replace(
                hour=manager.WORKDAY_START_HOUR,
                minute=0,
            ) + timedelta(days=1)
            return next_slot.strftime("%Y-%m-%dT%H:%M")

        if now.hour < manager.WORKDAY_START_HOUR:
            opening_slot = now.replace(
                hour=manager.WORKDAY_START_HOUR,
                minute=0,
            )
            return opening_slot.strftime("%Y-%m-%dT%H:%M")

        return now.strftime("%Y-%m-%dT%H:%M")

    def render_dashboard():
        selected_client_id = request.args.get("client_id", type=int)
        appointments = manager.list_appointments(selected_client_id)
        booked_appointments = [
            appointment
            for appointment in manager.list_appointments()
            if appointment.status.value == "booked"
        ]
        completed_unpaid_appointments = [
            appointment
            for appointment in manager.list_appointments()
            if appointment.status.value == "completed" and not appointment.paid
        ]

        return render_template(
            "index.html",
            appointments=appointments,
            booked_appointments=booked_appointments,
            completed_unpaid_appointments=completed_unpaid_appointments,
            clients=manager.list_clients(),
            hairdressers=manager.list_hairdressers(),
            services=manager.list_services(),
            tools=manager.list_tools(),
            mirrors=manager.list_mirrors(),
            chairs=manager.list_chairs(),
            selected_client_id=selected_client_id,
            min_booking_time=get_min_booking_time(),
            stats={
                "clients": len(manager.list_clients()),
                "hairdressers": len(manager.list_hairdressers()),
                "appointments": len(manager.list_appointments()),
                "paid": sum(1 for item in manager.list_appointments() if item.paid),
                "resources": (
                    len(manager.list_chairs())
                    + len(manager.list_mirrors())
                    + len(manager.list_tools())
                ),
            },
        )

    @app.get("/")
    def index():
        return render_dashboard()

    @app.post("/clients")
    def create_client():
        try:
            client = manager.create_client(
                request.form["name"],
                request.form["phone"],
            )
            flash(f"Client #{client.id} created.", "success")
        except (SalonError, ValueError) as error:
            flash(str(error), "error")

        return redirect_to_index(request.form.get("next_anchor", "people-space"))

    @app.post("/services")
    def create_service():
        try:
            service = manager.create_service(
                request.form["name"],
                int(request.form["duration"]),
                float(request.form["price"]),
                request.form["execution_mode"],
            )
            flash(f"Service #{service.id} created.", "success")
        except (SalonError, ValueError) as error:
            flash(str(error), "error")

        return redirect_to_index(request.form.get("next_anchor", "registry-section"))

    @app.post("/tools")
    def create_tool():
        try:
            tool = manager.create_tool(request.form["name"])
            flash(f"Tool #{tool.id} created.", "success")
        except (SalonError, ValueError) as error:
            flash(str(error), "error")

        return redirect_to_index(request.form.get("next_anchor", "salon-space"))

    @app.post("/mirrors")
    def create_mirror():
        try:
            mirror = manager.create_mirror(request.form["label"])
            flash(f"Mirror #{mirror.id} created.", "success")
        except (SalonError, ValueError) as error:
            flash(str(error), "error")

        return redirect_to_index(request.form.get("next_anchor", "salon-space"))

    @app.post("/chairs")
    def create_chair():
        try:
            chair = manager.create_chair(request.form["label"])
            flash(f"Chair #{chair.id} created.", "success")
        except (SalonError, ValueError) as error:
            flash(str(error), "error")

        return redirect_to_index(request.form.get("next_anchor", "salon-space"))

    @app.post("/hairdressers")
    def create_hairdresser():
        try:
            hairdresser = manager.create_hairdresser(
                request.form["name"],
                [int(item) for item in request.form.getlist("service_ids")],
                [int(item) for item in request.form.getlist("tool_ids")],
            )
            flash(f"Hairdresser #{hairdresser.id} created.", "success")
        except (SalonError, ValueError) as error:
            flash(str(error), "error")

        return redirect_to_index(request.form.get("next_anchor", "people-space"))

    @app.post("/appointments")
    def book_appointment():
        try:
            appointment = manager.book_haircut(
                int(request.form["client_id"]),
                int(request.form["hairdresser_id"]),
                int(request.form["service_id"]),
                int(request.form["chair_id"]),
                int(request.form["mirror_id"]),
                datetime.strptime(request.form["time"], "%Y-%m-%dT%H:%M"),
            )
            flash(f"Appointment #{appointment.id} created.", "success")
        except (SalonError, ValueError) as error:
            flash(str(error), "error")

        return redirect_to_index(request.form.get("next_anchor", "booking-section"))

    @app.post("/appointments/<int:appointment_id>/complete")
    def complete_appointment(appointment_id: int):
        try:
            appointment = manager.get_appointment(appointment_id)
            if appointment.service.requires_notes:
                manager.complete_appointment(
                    appointment_id,
                    notes=request.form.get("notes", ""),
                )
            else:
                manager.complete_appointment(
                    appointment_id,
                    tool_ids=[int(item) for item in request.form.getlist("tool_ids")],
                )
            flash(f"Appointment #{appointment_id} completed.", "success")
        except (SalonError, ValueError) as error:
            flash(str(error), "error")

        return redirect_to_index(request.form.get("next_anchor", "workflow-section"))

    @app.post("/appointments/<int:appointment_id>/pay")
    def pay_appointment(appointment_id: int):
        try:
            amount = manager.pay_for_service(appointment_id)
            flash(
                f"Payment accepted for appointment #{appointment_id}: {amount:.2f}.",
                "success",
            )
        except (SalonError, ValueError) as error:
            flash(str(error), "error")

        return redirect_to_index(request.form.get("next_anchor", "workflow-section"))

    @app.post("/appointments/<int:appointment_id>/cancel")
    def cancel_appointment(appointment_id: int):
        try:
            manager.cancel_appointment(appointment_id)
            flash(f"Appointment #{appointment_id} cancelled.", "success")
        except (SalonError, ValueError) as error:
            flash(str(error), "error")

        return redirect_to_index(request.form.get("next_anchor", "workflow-section"))

    return app
