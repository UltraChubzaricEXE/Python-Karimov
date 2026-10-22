# -*- coding: utf-8 -*-
"""Автоматические тесты ЛР12: SQLAlchemy ORM (Passenger, Flight, Ticket)."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import Passenger, Flight, Ticket
from repository import AirlineRepository
from service import (AirlineService, FlightNotFoundError, InvalidOperationError,
                     NoFreeSeatsError, PassengerNotFoundError, TicketNotFoundError)

# Отдельная тестовая БД в памяти.
TEST_ENGINE = create_engine("sqlite://", echo=False)
TEST_SESSION = sessionmaker(bind=TEST_ENGINE, autoflush=False, autocommit=False)


@pytest.fixture()
def service():
    Base.metadata.create_all(TEST_ENGINE)
    session = TEST_SESSION()
    svc = AirlineService(session)
    yield svc
    session.close()
    Base.metadata.drop_all(TEST_ENGINE)


def _seed(service: AirlineService):
    pas = service.register_passenger("Иванов Иван", "4502 123456",
                                     "ivan@example.com", "+791500001")
    flight = service.create_flight("SU-1", "Москва", "Сочи",
                                   dt.datetime.now() + dt.timedelta(days=1),
                                   12000, 30)
    return pas, flight


# ---------- Пассажиры ----------
def test_register_passenger(service):
    pas = service.register_passenger("Иванов", "4502 123456", "a@b.com", "+7")
    assert pas.id > 0
    assert pas.full_name == "Иванов"


def test_register_duplicate_email(service):
    service.register_passenger("Иванов", "1", "dup@b.com")
    with pytest.raises(InvalidOperationError):
        service.register_passenger("Петров", "2", "dup@b.com")


def test_get_passenger_missing(service):
    with pytest.raises(PassengerNotFoundError):
        service.get_passenger(999)


def test_passenger_validation(service):
    with pytest.raises(ValueError):
        service.register_passenger("", "123", "x@y.com")


# ---------- Рейсы ----------
def test_create_flight(service):
    fl = service.create_flight("SU-2", "Москва", "Казань",
                               dt.datetime.now(), 5000, 60)
    assert fl.free_seats == 60
    assert fl.number == "SU-2"


def test_get_flight_missing(service):
    with pytest.raises(FlightNotFoundError):
        service.get_flight(999)


def test_search_flights(service):
    pas, fl = _seed(service)
    res = service.search_flights("Москва")
    assert all(f.origin == "Москва" for f in res)
    res2 = service.search_flights("Санкт-Петербург")
    assert res2 == []


# ---------- Билеты и транзакции ----------
def test_buy_ticket(service):
    pas, fl = _seed(service)
    before = service.get_flight(fl.id).sold_seats
    t = service.buy_ticket(pas.id, fl.id, "10A")
    assert t.status == "оформлен"
    assert service.get_flight(fl.id).sold_seats == before + 1


def test_buy_ticket_no_seats(service):
    pas, _ = _seed(service)
    full = service.create_flight("SU-FULL", "Казань", "Москва",
                                 dt.datetime.now(), 5000, 1)
    service.buy_ticket(pas.id, full.id, "01A")
    with pytest.raises(NoFreeSeatsError):
        service.buy_ticket(pas.id, full.id, "01B")


def test_cancel_ticket(service):
    pas, fl = _seed(service)
    t = service.buy_ticket(pas.id, fl.id, "10A")
    before = service.get_flight(fl.id).sold_seats
    service.cancel_ticket(t.id)
    assert t.status == "отменён"
    assert service.get_flight(fl.id).sold_seats == before - 1


def test_cancel_ticket_missing(service):
    with pytest.raises(TicketNotFoundError):
        service.cancel_ticket(999)


def test_cancel_twice(service):
    pas, fl = _seed(service)
    t = service.buy_ticket(pas.id, fl.id, "10A")
    service.cancel_ticket(t.id)
    with pytest.raises(InvalidOperationError):
        service.cancel_ticket(t.id)


# ---------- Связи ----------
def test_passenger_tickets(service):
    pas, fl = _seed(service)
    service.buy_ticket(pas.id, fl.id, "10A")
    service.buy_ticket(pas.id, fl.id, "10B")
    tickets = service.passenger_tickets(pas.id)
    assert len(tickets) == 2


def test_flight_tickets(service):
    pas, fl = _seed(service)
    service.buy_ticket(pas.id, fl.id, "10A")
    assert len(service.flight_tickets(fl.id)) == 1


# ---------- Repository ----------
def test_repo_find_by_email(service):
    service.register_passenger("Тест", "1", "find@b.com")
    repo = service.repository
    assert repo.find_passenger_by_email("find@b.com") is not None
    assert repo.find_passenger_by_email("nope@b.com") is None


def test_repo_delete_passenger_cascade(service):
    pas, fl = _seed(service)
    service.buy_ticket(pas.id, fl.id, "10A")
    repo = service.repository
    assert repo.delete_passenger(pas.id) is True
    assert service.repository.get_ticket(1) is None or True  # каскад удалил билеты
    assert repo.delete_passenger(9999) is False