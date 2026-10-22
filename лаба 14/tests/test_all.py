# -*- coding: utf-8 -*-
"""Автоматические тесты ЛР14: репозиторий, сервис, FastAPI."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient

from main import app
from repository import Client, ClientRepository
from routers import _service
from service import ClientNotFoundError


@pytest.fixture()
def client_service():
    repo = ClientRepository()
    svc = type(_service)(repo)
    svc.create_client({"name": "Иванов", "age": 27, "membership": "годовой",
                       "membership_status": "активен", "trainer": "Мария"})
    svc.create_client({"name": "Петров", "age": 30, "membership": "месячный",
                       "membership_status": "истёк", "trainer": "Сергей"})
    return svc


@pytest.fixture()
def api():
    # сбрасываем глобальный репозиторий и загружаем демо-данные
    _service.repository._items.clear()
    _service.repository._next_id = 1
    for item in [
        {"name": "Иванов Иван", "age": 27, "membership": "годовой",
         "membership_status": "активен", "goals": ["похудение"], "trainer": "Мария"},
        {"name": "Петрова Анна", "age": 31, "membership": "месячный",
         "membership_status": "активен", "goals": ["тонус"], "trainer": "Мария"},
        {"name": "Сидоров Павел", "age": 25, "membership": "разовый",
         "membership_status": "истёк", "goals": [], "trainer": "Сергей"},
        {"name": "Козлов Артём", "age": 40, "membership": "годовой",
         "membership_status": "заморожен", "goals": [], "trainer": "Сергей"},
        {"name": "Смоленская Ольга", "age": 22, "membership": "месячный",
         "membership_status": "активен", "goals": ["кардио"], "trainer": "Мария"},
    ]:
        _service.create_client(item)
    return TestClient(app)


# ---------- Repository ----------
def test_repo_create_get():
    repo = ClientRepository()
    c = repo.create(Client(id=0, name="Тест", age=20, membership="разовый",
                           membership_status="активен"))
    assert c.id == 1
    assert repo.get_by_id(1).name == "Тест"


def test_repo_delete():
    repo = ClientRepository()
    c = repo.create(Client(id=0, name="Т", age=20, membership="разовый",
                           membership_status="активен"))
    assert repo.delete(c.id) is True
    assert repo.delete(999) is False


# ---------- Service ----------
def test_service_create(client_service):
    assert len(client_service.list_clients()) == 2


def test_service_get_missing(client_service):
    with pytest.raises(ClientNotFoundError):
        client_service.get_client(99)


def test_service_update(client_service):
    c = client_service.update_client(1, {"age": 28})
    assert c.age == 28
    assert c.name == "Иванов"


def test_service_active_memberships(client_service):
    active = client_service.active_memberships()
    assert [c.name for c in active] == ["Иванов"]


def test_service_statistics(client_service):
    stats = client_service.statistics()
    assert stats["total"] == 2
    assert stats["by_status"]["активен"] == 1


def test_service_search(client_service):
    assert len(client_service.search("ив")) == 1
    assert len(client_service.search("zzz")) == 0


# ---------- API ----------
def test_api_get_list(api):
    r = api.get("/clients")
    assert r.status_code == 200
    assert r.json()["total"] == 5  # демо из lifespan


def test_api_get_one(api):
    r = api.get("/clients/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_api_get_404(api):
    r = api.get("/clients/99999")
    assert r.status_code == 404


def test_api_post_create(api):
    r = api.post("/clients", json={"name": "Новый", "age": 21, "membership": "месячный",
                                   "membership_status": "активен"})
    assert r.status_code == 201
    assert r.json()["name"] == "Новый"


def test_api_post_validation_422(api):
    r = api.post("/clients", json={"name": "", "age": 200, "membership": "несуществующий",
                                   "membership_status": "активен"})
    assert r.status_code == 422  # ошибка валидации Pydantic


def test_api_put(api):
    r = api.put("/clients/1", json={"name": "Изменённый", "age": 29,
                                    "membership": "годовой", "membership_status": "активен"})
    assert r.status_code == 200
    assert r.json()["name"] == "Изменённый"


def test_api_patch(api):
    r = api.patch("/clients/2", json={"trainer": "Анна"})
    assert r.status_code == 200
    assert r.json()["trainer"] == "Анна"
    assert r.json()["name"]  # остальные поля сохранены


def test_api_delete_and_repeat(api):
    assert api.delete("/clients/1").status_code == 204
    assert api.get("/clients/1").status_code == 404
    # повторное удаление -> 404
    assert api.delete("/clients/1").status_code == 404


def test_api_filter(api):
    r = api.get("/clients", params={"status": "активен"})
    assert all(x["membership_status"] == "активен" for x in r.json()["items"])


def test_api_sort(api):
    r = api.get("/clients", params={"sort": "age", "order": "desc"})
    ages = [x["age"] for x in r.json()["items"]]
    assert ages == sorted(ages, reverse=True)


def test_api_pagination(api):
    r = api.get("/clients", params={"limit": 2, "offset": 0})
    assert len(r.json()["items"]) == 2


def test_api_search(api):
    r = api.get("/clients/search", params={"q": "Иван"})
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_api_statistics(api):
    r = api.get("/clients/statistics")
    assert r.status_code == 200
    assert r.json()["total"] >= 5


def test_api_special_active(api):
    r = api.get("/clients/active")
    assert r.status_code == 200
    assert all(x["membership_status"] == "активен" for x in r.json())


def test_api_health_async(api):
    r = api.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"