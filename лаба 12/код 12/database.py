"""Подключение к базе данных через SQLAlchemy (ЛР12, вариант 8).

Используется SQLite для локального запуска; строка подключения задаётся
переменной окружения DATABASE_URL (можно переключить на PostgreSQL).
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///" + os.path.join(os.path.dirname(__file__), "flights.db"),
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Базовый класс всех ORM-моделей."""


def get_session() -> Session:
    """Создаёт новую сессию SQLAlchemy."""
    return SessionLocal()


def init_db() -> None:
    """Создаёт таблицы по описаниям моделей."""
    import models  # noqa: F401  (регистрирует модели в Base.metadata)
    Base.metadata.create_all(engine)