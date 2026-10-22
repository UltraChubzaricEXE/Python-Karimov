"""Лабораторная работа №15. Вариант 8. Авиакомпания (Flask).

Модели: Flight, Passenger, Ticket. Используется SQLite.
"""
import datetime as dt

from flask import current_app, g
import sqlite3


def get_db() -> sqlite3.Connection:
    """Возвращает открытое соединение с SQLite (на запрос)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app) -> None:
    """Создаёт таблицы и загружает демонстрационные данные."""
    from app import create_app  # noqa: F401
    with app.app_context():
        db = get_db()
        db.executescript("""
            DROP TABLE IF EXISTS tickets;
            DROP TABLE IF EXISTS flights;
            DROP TABLE IF EXISTS passengers;
            CREATE TABLE passengers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                passport TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL
            );
            CREATE TABLE flights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT NOT NULL,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                departure TEXT NOT NULL,
                price REAL NOT NULL,
                total_seats INTEGER NOT NULL,
                sold_seats INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flight_id INTEGER NOT NULL REFERENCES flights(id) ON DELETE CASCADE,
                passenger_id INTEGER NOT NULL REFERENCES passengers(id) ON DELETE CASCADE,
                seat TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'оформлен',
                UNIQUE(flight_id, seat)
            );
        """)
        # Демо-данные
        seed = get_db()
        seed.executemany(
            "INSERT INTO passengers (full_name, passport, email) VALUES (?,?,?)",
            [("Иванов Иван", "4502 111111", "ivan@example.com"),
             ("Петрова Анна", "4502 222222", "anna@example.com"),
             ("Сидоров Павел", "4502 333333", "pavel@example.com")])
        now = dt.datetime.now() + dt.timedelta(days=1)
        flights = [
            ("SU-1001", "Москва", "Санкт-Петербург",
             (now).strftime("%Y-%m-%d %H:%M"), 3500, 60),
            ("SU-1002", "Москва", "Сочи",
             (now + dt.timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), 12000, 40),
            ("SU-1003", "Санкт-Петербург", "Москва",
             (now + dt.timedelta(days=3)).strftime("%Y-%m-%d %H:%M"), 4000, 50),
        ]
        seed.executemany(
            "INSERT INTO flights (number, origin, destination, departure, price, total_seats) "
            "VALUES (?,?,?,?,?,?)", flights)
        db.commit()
        close_db()