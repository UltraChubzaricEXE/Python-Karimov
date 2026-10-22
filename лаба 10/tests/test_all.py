# -*- coding: utf-8 -*-
"""Автоматические тесты ЛР10: репозиторий, сервис, REST API."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from app import app, _repo, _seed
from models import Client
from repository import ClientRepository
from service import ClientNotFoundError, ClientService, ValidationError


def _reset_api_repo():
    """Очищает и заполняет глобальный репозиторий тестовыми данными."""
    _repo._items.clear()
    _repo._next_id = 1
    _seed()


@pytest.fixture()
def client_service():
    repo = ClientRepository()
    svc = ClientService(repo)
    svc.create_client({"name": "Иванов", "age": 27, "membership": "годовой",
                       "membership_status": "активен", "trainer": "Мария"})
    svc.create_client({"name": "Петров", "age": 30, "membership": "месячный",
                       "membership_status": "истёк", "trainer": "Сергей"})
    return svc


@pytest.fixture()
def api():
    app.config["TESTING"] = True
    _reset_api_repo()
    return app.test_client()


# ---------- Repository ----------
def test_repo_create_and_get():
    repo = ClientRepository()
    c = repo.create(Client(id=0, name="Тест", age=20, membership="разовый", membership_status="активен"))
    assert c.id == 1
    assert repo.get_by_id(1).name == "Тест"


def test_repo_delete():
    repo = ClientRepository()
    c = repo.create(Client(id=0, name="Тест", age=20, membership="разовый", membership_status="активен"))
    assert repo.delete(c.id) is True
    assert repo.delete(9999) is False


# ---------- Service ----------
def test_service_create(client_service):
    assert len(client_service.list_clients()) == 2


def test_service_get_missing_raises(client_service):
    with pytest.raises(ClientNotFoundError):
        client_service.get_client(99)


def test_service_invalid_age(client_service):
    with pytest.raises(ValidationError):
        client_service.create_client({"name": "X", "age": 200, "membership": "месячный",
                                      "membership_status": "активен"})


def test_service_invalid_membership(client_service):
    with pytest.raises(ValidationError):
        client_service.create_client({"name": "X", "age": 20, "membership": "премиум",
                                      "membership_status": "активен"})


def test_service_patch(client_service):
    updated = client_service.patch_client(1, {"age": 28})
    assert updated.age == 28
    assert updated.name == "Иванов"


def test_service_active_memberships(client_service):
    active = client_service.active_memberships()
    assert [c.name for c in active] == ["Иванов"]


# ---------- API ----------
def test_api_list(api):
    r = api.get("/clients")
    assert r.status_code == 200
    assert isinstance(r.json, list)
    assert len(r.json) == 5  # тестовые данные _seed()


def test_api_get_existing(api):
    r = api.get("/clients/1")
    assert r.status_code == 200
    assert r.json["id"] == 1


def test_api_get_404(api):
    r = api.get("/clients/99999")
    assert r.status_code == 404
    assert r.json["code"] == "NOT_FOUND"


def test_api_create(api):
    r = api.post("/clients", json={"name": "Новый", "age": 21, "membership": "месячный",
                                   "membership_status": "активен"})
    assert r.status_code == 201
    assert r.json["name"] == "Новый"
    assert r.json["age"] == 21


def test_api_validation_400(api):
    r = api.post("/clients",
                 json={"name": "", "age": 20, "membership": "месячный",
                       "membership_status": "активен"})
    assert r.status_code == 400
    assert r.json["code"] == "VALIDATION_ERROR"


def test_api_put(api):
    r = api.put("/clients/1",
                json={"name": "Изменённый", "age": 29, "membership": "годовой",
                      "membership_status": "активен"})
    assert r.status_code == 200
    assert r.json["name"] == "Изменённый"


def test_api_patch(api):
    r = api.patch("/clients/2", json={"trainer": "Новый тренер"})
    assert r.status_code == 200
    assert r.json["trainer"] == "Новый тренер"
    assert r.json["name"]  # остальные поля сохранились


def test_api_delete_and_repeat(api):
    assert api.delete("/clients/1").status_code == 204
    assert api.get("/clients/1").status_code == 404


def test_api_filter_and_sort(api):
    r = api.get("/clients", query_string={"status": "активен"})
    assert all(x["membership_status"] == "активен" for x in r.json)
    r = api.get("/clients", query_string={"sort": "age", "order": "desc"})
    ages = [x["age"] for x in r.json]
    assert ages == sorted(ages, reverse=True)


def test_api_special_endpoint(api):
    r = api.get("/clients/who-active")
    assert r.status_code == 200
    assert all(x["membership_status"] == "активен" for x in r.json)