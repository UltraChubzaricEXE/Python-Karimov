# -*- coding: utf-8 -*-
"""Автоматические тесты ЛР9: репозиторий, сервис, протокол."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from exceptions import MovieNotFoundError, ValidationError
from models import Movie
from protocol import decode_messages, encode_message, make_response
from repository import MovieRepository
from service import MovieService


def _demo_movie() -> Movie:
    return Movie(id=0, title="Начало", director="Кристофер Нолан",
                 genre="фантастика", year=2010, duration_min=148, rating=8.8)


@pytest.fixture()
def repo():
    return MovieRepository()


@pytest.fixture()
def service(repo):
    return MovieService(repo)


# ---------- Repository ----------
def test_add_object(repo):
    added = repo.add(_demo_movie())
    assert added.id == 1
    assert repo.get(1) is added


def test_get_object_missing(repo):
    assert repo.get(999) is None


def test_delete_object(repo):
    added = repo.add(_demo_movie())
    assert repo.delete(added.id) is True
    assert repo.delete(999) is False
    assert repo.get_all() == []


def test_find_object_by_genre(repo):
    repo.add(_demo_movie())
    repo.add(Movie(id=0, title="Матрица", director="Вачовски", genre="фантастика",
                   year=1999, duration_min=136, rating=8.7))
    repo.add(Movie(id=0, title="Криминальное чтиво", director="Тарантино", genre="криминал",
                   year=1994, duration_min=154, rating=8.9))
    found = repo.find_by_genre("фантастика")
    assert len(found) == 2


# ---------- Service ----------
VALID = {"title": "Тест", "director": "Автор", "genre": "драма",
         "year": 2020, "duration_min": 100, "rating": 7.5}


def test_create_movie(service):
    movie = service.create_movie(dict(VALID))
    assert movie.id == 1
    assert len(service.list_movies()) == 1


def test_service_get_missing_raises(service):
    with pytest.raises(MovieNotFoundError):
        service.get_movie(1)


def test_service_invalid_data(service):
    bad = dict(VALID)
    bad["rating"] = 99
    with pytest.raises(ValidationError):
        service.create_movie(bad)


def test_update_movie(service):
    created = service.create_movie(dict(VALID))
    updated = service.update_movie(created.id, {**VALID, "title": "Изменённый"})
    assert updated.title == "Изменённый"


def test_delete_via_service(service):
    created = service.create_movie(dict(VALID))
    assert service.delete_movie(created.id) is True
    with pytest.raises(MovieNotFoundError):
        service.delete_movie(created.id)


# ---------- Protocol ----------
def test_encode_messages_have_newline():
    payload = {"command": "list", "data": {}}
    raw = encode_message(payload)
    assert raw.endswith(b"\n")
    assert json.loads(raw.decode("utf-8"))["command"] == "list"


def test_decode_two_messages():
    a = encode_message({"command": "list", "data": {}}).decode("utf-8")
    b = encode_message({"command": "get", "data": {"id": 1}}).decode("utf-8")
    buffer = a + b[:-1]  # разорвём второе сообщение
    msgs, rest = decode_messages(buffer)
    assert len(msgs) == 1
    assert msgs[0]["command"] == "list"
    # дожимаем хвост
    msgs2, rest2 = decode_messages(rest + b[-1])
    assert msgs2[0]["command"] == "get"


def test_decode_invalid_json_raises():
    with pytest.raises(Exception):
        decode_messages('{"command": "list"}\n{"broken"}\n')


def test_make_response():
    assert make_response("ok", {"x": 1}) == {"status": "ok", "data": {"x": 1}}
    assert make_response("error", error="плохо")["status"] == "error"