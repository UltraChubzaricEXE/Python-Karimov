"""Web-маршруты (HTML через Jinja2) авиакомпании (ЛР15, вариант 8)."""
from flask import Blueprint, abort, redirect, render_template, request, url_for

from repository import AirlineService

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def index():
    return render_template("index.html")


@web_bp.route("/flights")
def flights_list():
    service = AirlineService()
    search = request.args.get("search", "").strip()
    origin = request.args.get("origin", "").strip()
    sort = request.args.get("sort", "").strip()
    flights = list(service.repo.list_flights(search=search, origin=origin))
    if sort == "price":
        flights.sort(key=lambda f: f["price"])
    elif sort == "seats":
        flights.sort(key=lambda f: (f["total_seats"] - f["sold_seats"]))
    return render_template("flights.html", flights=flights, search=search,
                           origin=origin, sort=sort)


@web_bp.route("/flights/<int:flight_id>")
def flight_detail(flight_id):
    service = AirlineService()
    flight = service.repo.get_flight(flight_id)
    if flight is None:
        abort(404)
    tickets = service.repo.tickets_of_flight(flight_id)
    passengers = service.repo.list_passengers()
    return render_template("flight.html", flight=flight, tickets=tickets,
                           passengers=passengers)


@web_bp.route("/flights/<int:flight_id>/book", methods=["POST"])
def book_ticket(flight_id):
    service = AirlineService()
    passenger_id = request.form.get("passenger_id", type=int)
    seat = request.form.get("seat", "").strip()
    ok, result = service.buy_ticket(flight_id, passenger_id, seat)
    if ok:
        flash_msg = "Билет оформлен (ID=%s)" % result
    else:
        flash_msg = "Ошибка: %s" % result
    return redirect(url_for("web.flight_detail", flight_id=flight_id))


@web_bp.route("/passengers")
def passengers_list():
    service = AirlineService()
    passengers = service.repo.list_passengers()
    data = []
    for p in passengers:
        tickets = service.repo.tickets_of_passenger(p["id"])
        data.append({"passenger": p, "tickets": tickets})
    return render_template("passengers.html", data=data)


@web_bp.route("/tickets/<int:ticket_id>/cancel", methods=["POST"])
def cancel_ticket(ticket_id):
    service = AirlineService()
    ok, _ = service.cancel_ticket(ticket_id)
    return redirect(url_for("web.passengers_list"))