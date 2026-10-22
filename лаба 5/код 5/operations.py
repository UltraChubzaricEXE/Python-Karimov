"""Функции обработки коллекций объектов (функции высшего порядка) (ЛР5, вариант 8)."""

from functools import reduce

from models import STATUS_CANCELLED


def filter_objects(objects, predicate):
    """Отбирает объекты, для которых predicate вернул True."""
    return filter(predicate, objects)


def transform_objects(objects, operation):
    """Применяет operation к каждому объекту."""
    return map(operation, objects)


def sort_objects(objects, key_function, reverse=False):
    """Сортирует объекты по ключу, возвращаемому key_function."""
    return sorted(objects, key=key_function, reverse=reverse)


def make_cost_filter(minimum):
    """Возвращает функцию-предикат «стоимость не меньше minimum» (замыкание)."""
    return lambda order: order.cost >= minimum


def calculate_total(orders):
    """Общая стоимость заказов (через reduce)."""
    return reduce(lambda total, order: total + order.cost, orders, 0)


def has_cancelled(orders):
    """Есть ли среди заказов отменённые."""
    return any(order.status == STATUS_CANCELLED for order in orders)


def all_costs_positive(orders):
    """Все ли заказы имеют стоимость больше нуля."""
    return all(order.cost > 0 for order in orders)