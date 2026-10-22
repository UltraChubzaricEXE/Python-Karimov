"""Flask REST API фитнес-центра. ЛР10, вариант 8.

Ресурс: клиенты (/clients). Специализированный endpoint: GET /clients/who-active.
"""
from flask import Flask, jsonify, request

from models import Client
from repository import ClientRepository
from service import ClientNotFoundError, ClientService, ValidationError

app = Flask(__name__)

# Внедрение зависимостей (DIP): сервис получает репозиторий через конструктор.
_repo = ClientRepository()
_service = ClientService(_repo)


def _seed():
    demo = [
        ("Иванов Иван", 27, "годовой", "активен", ["похудение"], "Тренер Мария"),
        ("Петрова Анна", 31, "месячный", "активен", ["тонус"], "Тренер Мария"),
        ("Сидоров Павел", 25, "разовый", "истёк", ["набор массы"], "Тренер Сергей"),
        ("Козлов Артём", 40, "годовой", "заморожен", [], "Тренер Сергей"),
        ("Смоленская Ольга", 22, "месячный", "активен", ["кардио"], "Тренер Мария"),
    ]
    for name, age, m, s, goals, tr in demo:
        _service.create_client({"name": name, "age": age, "membership": m,
                                "membership_status": s, "goals": goals, "trainer": tr})


@app.errorhandler(ClientNotFoundError)
def handle_not_found(e):
    return jsonify({"error": str(e), "code": "NOT_FOUND"}), 404


@app.errorhandler(ValidationError)
def handle_validation(e):
    return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400


@app.errorhandler(404)
def handle_404(e):
    return jsonify({"error": "Ресурс не найден", "code": "NOT_FOUND"}), 404


# ---------- CRUD ----------
@app.get("/clients")
def list_clients():
    status = request.args.get("status")
    membership = request.args.get("membership")
    sort = request.args.get("sort")
    order = request.args.get("order", "asc")
    clients = _service.filter_and_sort(status=status, membership=membership, sort=sort, order=order)
    return jsonify([c.to_dict() for c in clients])


@app.get("/clients/<int:client_id>")
def get_client(client_id):
    return jsonify(_service.get_client(client_id).to_dict())


@app.post("/clients")
def create_client():
    data = request.get_json(silent=True) or {}
    return jsonify(_service.create_client(data).to_dict()), 201


@app.put("/clients/<int:client_id>")
def update_client(client_id):
    data = request.get_json(silent=True) or {}
    return jsonify(_service.update_client(client_id, data).to_dict())


@app.patch("/clients/<int:client_id>")
def patch_client(client_id):
    data = request.get_json(silent=True) or {}
    return jsonify(_service.patch_client(client_id, data).to_dict())


@app.delete("/clients/<int:client_id>")
def delete_client(client_id):
    _service.delete_client(client_id)
    return jsonify({"deleted": client_id}), 204


# ---------- Специализированный endpoint ----------
@app.get("/clients/who-active")
def active_memberships():
    clients = _service.active_memberships()
    return jsonify([c.to_dict() for c in clients])


if __name__ == "__main__":
    _seed()
    app.run(host="127.0.0.1", port=5001, debug=False)