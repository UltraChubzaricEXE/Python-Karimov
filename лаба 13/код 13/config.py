"""Конфигурация подключения к MongoDB и Redis (ЛР13, вариант 8).

По умолчанию используется реальный MongoDB-клиент. Если сервер
недоступен, приложение автоматически переключается на mongomock
(эмуляция в памяти) — это позволяет запускать демонстрацию и тесты
на любом компьютере без установки MongoDB.
"""
import os

import redis
from pymongo import MongoClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://127.0.0.1:27017")
MONGO_DB = os.getenv("MONGO_DB", "fitness_center")
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")


def make_mongo_client(url: str = MONGO_URL):
    """Создаёт клиент MongoDB; при недоступности - mongomock."""
    try:
        client = MongoClient(url, serverSelectionTimeoutMS=1500)
        client.admin.command("ping")
        return client
    except Exception:
        import mongomock
        return mongomock.MongoClient()


def make_redis_client(url: str = REDIS_URL):
    """Создаёт Redis-клиент; при недоступности - fakeredis."""
    try:
        client = redis.Redis.from_url(url, decode_responses=True)
        client.ping()
        return client
    except Exception:
        from fakeredis import FakeRedis
        return FakeRedis(decode_responses=True)