"""ORM-модели авиакомпании (ЛР12, вариант 8).

Сущности: Passenger, Flight, Ticket. Связь 1:N (Passenger - Tickets,
Flight - Tickets). Транзакционная операция — покупка/отмена билета.
"""
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Passenger(Base):
    """Пассажир."""
    __tablename__ = "passengers"
    __table_args__ = (UniqueConstraint("email", name="uq_passenger_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    passport: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), default="")

    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="passenger", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Passenger {self.id} {self.full_name}>"


class Flight(Base):
    """Рейс."""
    __tablename__ = "flights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[str] = mapped_column(String(20), nullable=False)
    origin: Mapped[str] = mapped_column(String(80), nullable=False)
    destination: Mapped[str] = mapped_column(String(80), nullable=False)
    departure: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    total_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    sold_seats: Mapped[int] = mapped_column(Integer, default=0)

    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="flight", cascade="all, delete-orphan")

    @property
    def free_seats(self) -> int:
        return self.total_seats - self.sold_seats

    def __repr__(self) -> str:
        return f"<Flight {self.number} {self.origin}->{self.destination}>"


class Ticket(Base):
    """Билет (связь пассажира и рейса)."""
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    passenger_id: Mapped[int] = mapped_column(
        ForeignKey("passengers.id", ondelete="CASCADE"), nullable=False)
    flight_id: Mapped[int] = mapped_column(
        ForeignKey("flights.id", ondelete="CASCADE"), nullable=False)
    seat: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="оформлен")
    booked_at: Mapped[datetime] = mapped_column(DateTime,
                                                default=lambda: datetime.now().replace(microsecond=0))

    passenger: Mapped["Passenger"] = relationship(back_populates="tickets")
    flight: Mapped["Flight"] = relationship(back_populates="tickets")

    def __repr__(self) -> str:
        return f"<Ticket {self.id} flight={self.flight_id} seat={self.seat}>"