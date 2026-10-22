"""Слой доступа к данным и бизнес-логика авиакомпании (ЛР15, вариант 8).

Repository выполняет SQL-запросы к SQLite; Service содержит бизнес-логику.
"""
from database import get_db


class AirlineRepository:
    """SQL-запросы к таблицам flights, passengers, tickets."""

    def __init__(self) -> None:
        self.db = get_db()

    # ---------- рейсы ----------
    def list_flights(self, search="", origin=""):
        sql = "SELECT * FROM flights WHERE 1=1"
        params = []
        if search:
            sql += " AND (number LIKE ? OR origin LIKE ? OR destination LIKE ?)"
            like = f"%{search}%"
            params += [like, like, like]
        if origin:
            sql += " AND origin = ?"
            params.append(origin)
        sql += " ORDER BY departure"
        return self.db.execute(sql, params).fetchall()

    def get_flight(self, flight_id):
        return self.db.execute(
            "SELECT * FROM flights WHERE id = ?", (flight_id,)).fetchone()

    def create_flight(self, number, origin, destination, departure, price, total_seats):
        cur = self.db.execute(
            "INSERT INTO flights (number, origin, destination, departure, price, total_seats) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (number, origin, destination, departure, price, total_seats))
        self.db.commit()
        return cur.lastrowid

    def update_flight(self, flight_id, number, origin, destination,
                      departure, price, total_seats):
        self.db.execute(
            "UPDATE flights SET number=?, origin=?, destination=?, departure=?, "
            "price=?, total_seats=? WHERE id=?",
            (number, origin, destination, departure, price, total_seats, flight_id))
        self.db.commit()

    def delete_flight(self, flight_id):
        self.db.execute("DELETE FROM flights WHERE id = ?", (flight_id,))
        self.db.commit()

    # ---------- пассажиры ----------
    def list_passengers(self):
        return self.db.execute("SELECT * FROM passengers ORDER BY id").fetchall()

    def get_passenger(self, passenger_id):
        return self.db.execute(
            "SELECT * FROM passengers WHERE id = ?", (passenger_id,)).fetchone()

    def create_passenger(self, full_name, passport, email):
        cur = self.db.execute(
            "INSERT INTO passengers (full_name, passport, email) VALUES (?, ?, ?)",
            (full_name, passport, email))
        self.db.commit()
        return cur.lastrowid

    # ---------- билеты ----------
    def create_ticket(self, flight_id, passenger_id, seat):
        cur = self.db.execute(
            "INSERT INTO tickets (flight_id, passenger_id, seat, status) "
            "VALUES (?, ?, ?, 'оформлен')",
            (flight_id, passenger_id, seat))
        self.db.commit()
        return cur.lastrowid

    def get_ticket(self, ticket_id):
        return self.db.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()

    def tickets_of_flight(self, flight_id):
        return self.db.execute(
            "SELECT t.*, p.full_name FROM tickets t "
            "JOIN passengers p ON p.id = t.passenger_id WHERE t.flight_id = ?",
            (flight_id,)).fetchall()

    def tickets_of_passenger(self, passenger_id):
        return self.db.execute(
            "SELECT t.*, f.number, f.origin, f.destination, f.departure FROM tickets t "
            "JOIN flights f ON f.id = t.flight_id WHERE t.passenger_id = ?",
            (passenger_id,)).fetchall()

    def cancel_ticket(self, ticket_id):
        self.db.execute("UPDATE tickets SET status = 'отменён' WHERE id = ?", (ticket_id,))
        self.db.commit()


class AirlineService:
    """Бизнес-логика поверх репозитория."""

    def __init__(self) -> None:
        self.repo = AirlineRepository()

    def buy_ticket(self, flight_id, passenger_id, seat) -> tuple:
        """Покупка билета с проверкой мест и транзакцией."""
        flight = self.repo.get_flight(flight_id)
        if flight is None:
            return False, "Рейс не найден"
        if flight["sold_seats"] >= flight["total_seats"]:
            return False, "На рейсе нет свободных мест"
        # проверка, что место не занято
        existing = self.repo.tickets_of_flight(flight_id)
        if any(t["seat"] == seat for t in existing):
            return False, f"Место {seat} уже занято"
        ticket_id = self.repo.create_ticket(flight_id, passenger_id, seat)
        # учёт проданного места
        self.repo.db.execute(
            "UPDATE flights SET sold_seats = sold_seats + 1 WHERE id = ?", (flight_id,))
        self.repo.db.commit()
        return True, ticket_id

    def cancel_ticket(self, ticket_id) -> tuple:
        ticket = self.repo.get_ticket(ticket_id)
        if ticket is None:
            return False, "Билет не найден"
        if ticket["status"] == "отменён":
            return False, "Билет уже отменён"
        self.repo.cancel_ticket(ticket_id)
        # освобождаем место
        self.repo.db.execute(
            "UPDATE flights SET sold_seats = MAX(0, sold_seats - 1) WHERE id = ?",
            (ticket["flight_id"],))
        self.repo.db.commit()
        return True, None