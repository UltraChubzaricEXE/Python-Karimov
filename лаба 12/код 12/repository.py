"""Репозиторий авиакомпании через SQLAlchemy ORM (ЛР12, вариант 8).

Repository изолирует работу с базой через ORM; сервис использует его,
не обращаясь к Session напрямую.
"""
from datetime import datetime
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Flight, Passenger, Ticket


class AirlineRepository:
    """Доступ к данным о пассажирах, рейсах и билетах."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # ---------- пассажиры ----------
    def add_passenger(self, full_name: str, passport: str, email: str,
                      phone: str = "") -> Passenger:
        passenger = Passenger(full_name=full_name, passport=passport,
                              email=email, phone=phone)
        self.session.add(passenger)
        self.session.commit()
        return passenger

    def get_passenger(self, passenger_id: int) -> Passenger | None:
        return self.session.get(Passenger, passenger_id)

    def list_passengers(self) -> Iterable[Passenger]:
        return self.session.scalars(select(Passenger).order_by(Passenger.id)).all()

    def find_passenger_by_email(self, email: str) -> Passenger | None:
        stmt = select(Passenger).where(Passenger.email == email)
        return self.session.scalars(stmt).first()

    # ---------- рейсы ----------
    def add_flight(self, number: str, origin: str, destination: str,
                   departure: datetime, price: float, total_seats: int) -> Flight:
        flight = Flight(number=number, origin=origin, destination=destination,
                        departure=departure, price=price, total_seats=total_seats)
        self.session.add(flight)
        self.session.commit()
        return flight

    def get_flight(self, flight_id: int) -> Flight | None:
        return self.session.get(Flight, flight_id)

    def list_flights(self) -> Iterable[Flight]:
        return self.session.scalars(select(Flight).order_by(Flight.departure)).all()

    def list_flights_by_origin(self, origin: str, after: datetime | None = None):
        stmt = select(Flight).where(Flight.origin == origin)
        if after is not None:
            stmt = stmt.where(Flight.departure >= after)
        return self.session.scalars(stmt.order_by(Flight.departure)).all()

    # ---------- билеты ----------
    def get_ticket(self, ticket_id: int) -> Ticket | None:
        return self.session.get(Ticket, ticket_id)

    def list_tickets_of_passenger(self, passenger_id: int) -> Iterable[Ticket]:
        stmt = (select(Ticket)
                .where(Ticket.passenger_id == passenger_id)
                .order_by(Ticket.id))
        return self.session.scalars(stmt).all()

    def list_tickets_of_flight(self, flight_id: int) -> Iterable[Ticket]:
        stmt = (select(Ticket)
                .where(Ticket.flight_id == flight_id)
                .order_by(Ticket.seat))
        return self.session.scalars(stmt).all()

    def delete_passenger(self, passenger_id: int) -> bool:
        passenger = self.get_passenger(passenger_id)
        if passenger is None:
            return False
        self.session.delete(passenger)
        self.session.commit()
        return True

    def delete_flight(self, flight_id: int) -> bool:
        flight = self.get_flight(flight_id)
        if flight is None:
            return False
        self.session.delete(flight)
        self.session.commit()
        return True