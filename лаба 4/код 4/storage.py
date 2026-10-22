"""Хранение данных: интерфейс Repository, JSON-хранилище, экспорт в CSV (ЛР4)."""

import csv
import json
from abc import ABC, abstractmethod

from exceptions import StorageError
from models import Order


class Repository(ABC):
    """Интерфейс хранилища заказов."""

    @abstractmethod
    def save(self, objects):
        ...

    @abstractmethod
    def load(self):
        ...


class JsonRepository(Repository):
    """Хранилище заказов в JSON-файле."""

    def __init__(self, path):
        self.path = path

    def save(self, objects):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = [order.to_dict() for order in objects]
        try:
            with open(self.path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except OSError as error:
            raise StorageError(f"Не удалось записать файл: {error}")

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return [Order.from_dict(item) for item in data]
        except FileNotFoundError:
            return []  # первый запуск: файла ещё нет
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            raise StorageError(f"Файл данных повреждён: {error}")


def export_csv(orders, path):
    """Экспорт основных характеристик заказов в CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "customer", "items", "cost", "status"])
        for order in orders:
            goods = "; ".join(f"{i.name} x{i.quantity}" for i in order.items)
            writer.writerow([order.order_id, order.customer, goods,
                             f"{order.total_cost():.2f}", order.status])