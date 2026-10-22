"""Сервисный слой авиакомпании (ЛР12, вариант 8).

Покупка и отмена билета выполняются как транзакция: изменение количества
проданных мест на рейсе и создание/удаление билета происходят атомарно.
"""
import datetime as dt

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Ticket
from repository import AirlineRepository


class PassengerNotFoundError(Exception):
    pass


class FlightNotFoundError(Exception):
    pass


class TicketNotFoundError(Exception):
    pass


class NoFreeSeatsError(Exception):
    pass


class InvalidOperationError(Exception):
    pass


class AirlineService:
    """Бизнес-логика: регистрация пассажиров, рейсов, покупка/отмена билетов."""

    def __init__(self, session: Session, repository: AirlineRepository | None = None) -> None:
        self.session = session
        self.repository = repository or AirlineRepository(session)

    # ---------- пассажиры ----------
    def register_passenger(self, full_name: str, passport: str, email: str, phone: str = ""):
        if not full_name.strip() or not passport.strip():
            raise ValueError("Имя и паспорт обязательны")
        if self.repository.find_passenger_by_email(email.strip().lower()):
            raise InvalidOperationError(f"Пассажир с email {email} уже зарегистрирован")
        return self.repository.add_passenger(full_name.strip(), passport.strip(),
                                             email.strip(), phone.strip())

    def get_passenger(self, passenger_id: int):
        passenger = self.repository.get_passenger(passenger_id)
        if passenger is None:
            raise PassengerNotFoundError(f"Пассажир с номером {passenger_id} не найден")
        return passenger

    # ---------- рейсы ----------
    def create_flight(self, number: str, origin: str, destination: str,
                      departure: dt.datetime, price: float, total_seats: int):
        if price <= 0 or total_seats <= 0:
            raise ValueError("Цена и количество мест должны быть положительными")
        return self.repository.add_flight(number.strip(), origin.strip(),
                                          destination.strip(), departure, price, total_seats)

    def get_flight(self, flight_id: int):
        flight = self.repository.get_flight(flight_id)
        if flight is None:
            raise FlightNotFoundError(f"Рейс с номером {flight_id} не найден")
        return flight

    def search_flights(self, origin: str, destination: str = ""):
        flights = self.repository.list_flights_by_origin(
            origin.strip(), after=dt.datetime.now() - dt.timedelta(days=1))
        if destination.strip():
            flights = [f for f in flights if f.destination.lower() == destination.strip().lower()]
        return flights

    # ---------- покупка билета (транзакция) ----------
    def buy_ticket(self, passenger_id: int, flight_id: int, seat: str) -> Ticket:
        passenger = self.get_passenger(passenger_id)
        flight = self.get_flight(flight_id)
        if flight.free_seats <= 0:
            raise NoFreeSeatsError(f"На рейсе {flight.number} нет свободных мест")
        try:
            ticket = Ticket(passenger_id=passenger.id, flight_id=flight.id,
                            seat=seat.strip(), status="оформлен")
            self.session.add(ticket)
            flight.sold_seats += 1
            self.session.commit()
            return ticket
        except IntegrityError:
            self.session.rollback()
            raise InvalidOperationError(f"Место {seat} уже занято или билет не может быть оформлен")

    # ---------- отмена билета (транзакция) ----------
    def cancel_ticket(self, ticket_id: int) -> Ticket:
        ticket = self.repository.get_ticket(ticket_id)
        if ticket is None:
            raise TicketNotFoundError(f"Билет №{ticket_id} не найден")
        if ticket.status == "отменён":
            raise InvalidOperationError("Билет уже отменён")
        try:
            ticket.status = "отменён"
            flight = self.repository.get_flight(ticket.flight_id)
            if flight is not None and flight.sold_seats > 0:
                flight.sold_seats -= 1
            self.session.commit()
            return ticket
        except IntegrityError:
            self.session.rollback()
            raise


    # ---------- просмотр ----------
    def passenger_tickets(self, passenger_id: int):
        self.get_passenger(passenger_id)
        return self.repository.list_tickets_of_passenger(passenger_id)

    def flight_tickets(self, flight_id: int):
        self.get_flight(flight_id)
        return self.repository.list_tickets_of_flight(flight_id)

    def list_flights(self):
        return self.repository.list_flights()

    def list_passengers(self):
        return self.repository.list_passengers()