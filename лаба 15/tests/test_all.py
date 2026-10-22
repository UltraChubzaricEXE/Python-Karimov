# -*- coding: utf-8 -*-
"""Автоматические тесты ЛР15: Flask веб-приложение авиакомпании."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from app import create_app
from repository import AirlineService


@pytest.fixture()
def app():
    # тестовая БД во временной папке
    _tmpdir = tempfile.mkdtemp()
    test_db = os.path.join(_tmpdir, "test_airlines.db")
    app = create_app()
    app.config.update(TESTING=True, DATABASE=test_db)
    from database import init_db
    with app.app_context():
        init_db(app)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def service(app):
    with app.app_context():
        yield AirlineService()


# ---------- Маршруты веб ----------
def test_index_page(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"\xd0\x90\xd0\xb2\xd0\xb8\xd0\xb0\xd0\xba\xd0\xbe\xd0\xbc\xd0\xbf\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x8f" in r.data or "Авиакомпания".encode() in r.data


def test_flights_list(client):
    r = client.get("/flights")
    assert r.status_code == 200
    assert b"SU-1001" in r.data


def test_flight_detail(client):
    r = client.get("/flights/1")
    assert r.status_code == 200
    assert b"\xd0\x9a\xd1\x83\xd0\xbf\xd0\xb8\xd1\x82\xd1\x8c" in r.data or "Купить".encode() in r.data


def test_flight_detail_404(client):
    r = client.get("/flights/99999")
    assert r.status_code == 404
    assert b"404" in r.data


def test_passengers_page(client):
    r = client.get("/passengers")
    assert r.status_code == 200
    assert b"ivan@example.com" in r.data


def test_search_flights(client):
    r = client.get("/flights", query_string={"search": "Сочи"})
    assert r.status_code == 200
    assert b"SU-1002" in r.data


def test_filter_origin(client):
    r = client.get("/flights", query_string={"origin": "Москва"})
    assert r.status_code == 200
    assert b"SU-1001" in r.data


def test_sort_price(client):
    # сортировка по цене: первый рейс должен быть дешёвым (3500)
    r = client.get("/flights", query_string={"sort": "price"})
    assert r.status_code == 200


# ---------- Бизнес-логика (Service) ----------
def test_buy_ticket(service):
    ok, result = service.buy_ticket(1, 1, "99A")
    assert ok is True
    assert result is not None


def test_buy_ticket_no_seats(service, app):
    with app.app_context():
        # создаём рейс с 1 местом и заполняем его
        service.repo.create_flight("SU-X", "Казань", "Москва", "2024-12-01 10:00", 5000, 1)
        # рейс id будет последним
        rows = service.repo.db.execute("SELECT id FROM flights ORDER BY id DESC LIMIT 1").fetchone()
        fid = rows["id"]
        ok, _ = service.buy_ticket(fid, 1, "01A")
        assert ok is True
        ok2, err = service.buy_ticket(fid, 2, "01B")
        assert ok2 is False
        assert "нет свободных" in err.lower() or "свободных" in err


def test_cancel_ticket(service):
    ok, result = service.buy_ticket(1, 1, "88A")
    assert ok is True
    ok2, _ = service.cancel_ticket(result)
    assert ok2 is True


def test_cancel_ticket_missing(service):
    ok, _ = service.cancel_ticket(99999)
    assert ok is False


def test_cancel_ticket_twice(service):
    ok, result = service.buy_ticket(1, 1, "77A")
    service.cancel_ticket(result)
    ok2, err = service.cancel_ticket(result)
    assert ok2 is False
    assert "отмен" in err


# ---------- REST API ----------
def test_api_list_flights(client):
    r = client.get("/api/flights")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


def test_api_get_flight(client):
    r = client.get("/api/flights/1")
    assert r.status_code == 200
    assert r.get_json()["number"] == "SU-1001"


def test_api_get_flight_404(client):
    r = client.get("/api/flights/99999")
    assert r.status_code == 404


def test_api_create_flight(client):
    r = client.post("/api/flights", json={
        "number": "SU-NEW", "origin": "Казань", "destination": "Москва",
        "departure": "2024-12-01 10:00", "price": 5000, "total_seats": 50})
    assert r.status_code == 201
    assert r.get_json()["created"] is True


def test_api_create_flight_bad(client):
    r = client.post("/api/flights", json={"number": "X"})
    assert r.status_code == 400


def test_api_delete_flight(client):
    r = client.delete("/api/flights/3")
    assert r.status_code == 204
    assert client.get("/api/flights/3").status_code == 404


def test_api_delete_flight_404(client):
    assert client.delete("/api/flights/99999").status_code == 404


def test_api_buy_ticket(client):
    r = client.post("/api/tickets", json={"flight_id": 1, "passenger_id": 1, "seat": "55A"})
    assert r.status_code == 201
    assert "ticket_id" in r.get_json()


def test_api_buy_ticket_conflict(client):
    # сначала покупаем место, затем повторно - конфликт 409
    client.post("/api/tickets", json={"flight_id": 1, "passenger_id": 1, "seat": "66A"})
    r = client.post("/api/tickets", json={"flight_id": 1, "passenger_id": 2, "seat": "66A"})
    assert r.status_code == 409


def test_api_buy_ticket_bad(client):
    r = client.post("/api/tickets", json={"seat": "1A"})
    assert r.status_code == 400