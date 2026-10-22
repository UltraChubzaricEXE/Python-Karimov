"""REST API маршруты авиакомпании (ЛР15, вариант 8).

Возвращают JSON с корректными HTTP-кодами.
"""
from flask import Blueprint, jsonify, request

from repository import AirlineService

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/flights")
def api_list_flights():
    service = AirlineService()
    flights = service.repo.list_flights()
    return jsonify([dict(f) for f in flights])


@api_bp.get("/flights/<int:flight_id>")
def api_get_flight(flight_id):
    service = AirlineService()
    flight = service.repo.get_flight(flight_id)
    if flight is None:
        return jsonify({"error": "Рейс не найден"}), 404
    return jsonify(dict(flight))


@api_bp.post("/flights")
def api_create_flight():
    service = AirlineService()
    data = request.get_json(silent=True) or {}
    required = ("number", "origin", "destination", "departure", "price", "total_seats")
    for key in required:
        if key not in data:
            return jsonify({"error": f"Отсутствует поле {key}"}), 400
    if float(data["price"]) <= 0 or int(data["total_seats"]) <= 0:
        return jsonify({"error": "Цена и места должны быть положительными"}), 400
    fid = service.repo.create_flight(data["number"], data["origin"], data["destination"],
                                     data["departure"], float(data["price"]),
                                     int(data["total_seats"]))
    return jsonify({"id": fid, "created": True}), 201


@api_bp.delete("/flights/<int:flight_id>")
def api_delete_flight(flight_id):
    service = AirlineService()
    if service.repo.get_flight(flight_id) is None:
        return jsonify({"error": "Рейс не найден"}), 404
    service.repo.delete_flight(flight_id)
    return "", 204


@api_bp.post("/tickets")
def api_buy_ticket():
    service = AirlineService()
    data = request.get_json(silent=True) or {}
    flight_id = data.get("flight_id")
    passenger_id = data.get("passenger_id")
    seat = data.get("seat", "").strip()
    if not flight_id or not passenger_id or not seat:
        return jsonify({"error": "Укажите flight_id, passenger_id и seat"}), 400
    ok, result = service.buy_ticket(flight_id, passenger_id, seat)
    if not ok:
        return jsonify({"error": result}), 409
    return jsonify({"ticket_id": result}), 201


@api_bp.get("/flights/<int:flight_id>/tickets")
def api_flight_tickets(flight_id):
    service = AirlineService()
    tickets = service.repo.tickets_of_flight(flight_id)
    return jsonify([dict(t) for t in tickets])