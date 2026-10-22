"""Генераторы и итераторы (ЛР5, вариант 8)."""


def orders_of_customer(orders, customer):
    """Генератор: выдаёт заказы выбранного клиента по одному."""
    for order in orders:
        if order.customer == customer:
            yield order


def expensive_numbers(orders, limit):
    """Генератор номеров заказов дороже limit."""
    for order in orders:
        if order.cost > limit:
            yield order.number


class OrderIterator:
    """Собственный итератор по коллекции заказов."""

    def __init__(self, orders):
        self.orders = orders
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.orders):
            raise StopIteration
        order = self.orders[self.index]
        self.index += 1
        return order