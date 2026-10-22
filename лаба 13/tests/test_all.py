# -*- coding: utf-8 -*-
"""Автоматические тесты ЛР13: MongoDB (mongomock) + Redis (fakeredis)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from config import make_mongo_client, make_redis_client
from mongodb_repo import MongoRepository
from redis_cache import RedisCache
from seed import seed_data
from service import FitnessService


@pytest.fixture()
def repo():
    mongo = make_mongo_client()
    repo = MongoRepository(mongo)
    repo.ensure_indexes()
    for doc in seed_data():
        repo.insert(doc)
    return repo


@pytest.fixture()
def cache():
    return RedisCache(make_redis_client())


@pytest.fixture()
def service(repo, cache):
    return FitnessService(repo, cache)


# ---------- MongoDB CRUD ----------
def test_insert_and_find(repo):
    assert len(repo.find_all()) >= 20  # из seed


def test_find_by_id(repo):
    doc = repo.find_all()[0]
    found = repo.find_by_id(doc["_id"])
    assert found["full_name"] == doc["full_name"]


def test_update(repo):
    doc = repo.find_all()[0]
    ok = repo.update(doc["_id"], {"age": doc["age"] + 1})
    assert ok is True
    assert repo.find_by_id(doc["_id"])["age"] == doc["age"] + 1


def test_delete(repo):
    doc = repo.find_all()[0]
    assert repo.delete(doc["_id"]) is True
    assert repo.find_by_id(doc["_id"]) is None


# ---------- MongoDB запросы ----------
def test_find_by_status(repo):
    active = repo.find_by_status("активен")
    assert all(c["status"] == "активен" for c in active)
    assert len(active) > 0


def test_find_by_trainer(repo):
    trainer = repo.find_all()[0]["trainer"]
    res = repo.find_by_trainer(trainer)
    assert all(c["trainer"] == trainer for c in res)


def test_find_by_nested_field(repo):
    # запрос по вложенному полю address.city
    all_docs = repo.find_all()
    city = all_docs[0]["address"]["city"]
    res = repo.find_in_city(city)
    assert all(c["address"]["city"] == city for c in res)


def test_find_by_array_element(repo):
    # запрос по элементу массива goals
    all_docs = repo.find_all()
    goal = all_docs[0]["goals"][0]
    res = repo.find_by_goal(goal)
    assert all(goal in c["goals"] for c in res)


def test_aggregate_status(repo):
    groups = repo.aggregate_by_status()
    total = sum(g["count"] for g in groups)
    assert total == len(repo.find_all())


def test_aggregate_avg_age(repo):
    assert repo.aggregate_avg_age() > 0


# ---------- Redis ----------
def test_redis_string_set_get(cache):
    cache.set_json("k", {"x": 1}, ttl=30)
    assert cache.get_json("k") == {"x": 1}


def test_redis_ttl(cache):
    cache.set_json("k", "v", ttl=60)
    assert 0 < cache.ttl("k") <= 60


def test_redis_delete(cache):
    cache.set_json("k", "v")
    cache.delete("k")
    assert cache.get_json("k") is None


def test_redis_workout_hash(cache):
    cache.set_current_workout(1, {"exercise": "йога", "duration": 60})
    assert cache.get_current_workout(1)["exercise"] == "йога"


def test_redis_visits_list(cache):
    cache.push_visit(1, "a")
    cache.push_visit(1, "b")
    cache.push_visit(1, "c")
    assert cache.last_visits(1)[:3] == ["c", "b", "a"]


def test_redis_activity_sorted(cache):
    cache.add_activity(1, 1)
    cache.add_activity(2, 9)
    top = cache.top_clients(1)
    assert str(top[0][0]) == "2"


# ---------- Cache-Aside / инвалидация ----------
def test_cache_aside(service, repo):
    doc = repo.find_all()[0]
    doc_id = str(doc["_id"])
    data, hit = service.get_client_cached(doc_id)
    assert hit is False and data is not None
    _, hit = service.get_client_cached(doc_id)
    assert hit is True


def test_cache_invalidation(service, repo):
    doc = repo.find_all()[0]
    doc_id = str(doc["_id"])
    service.get_client_cached(doc_id)
    service.update_client(doc_id, {"age": 99})
    _, hit = service.get_client_cached(doc_id)
    assert hit is False  # после обновления кэш удалён


# ---------- Service валидация ----------
def test_service_validation(service):
    with pytest.raises(ValueError):
        service.create_client({"full_name": "", "age": 20, "status": "активен"})
    with pytest.raises(ValueError):
        service.create_client({"full_name": "X", "age": 200, "status": "активен"})
    with pytest.raises(ValueError):
        service.create_client({"full_name": "X", "age": 20, "status": "неизвестный"})