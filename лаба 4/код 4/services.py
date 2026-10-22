"""Бизнес-логика: операции над заказами (ЛР4, вариант 8)."""

from exceptions import InvalidOrderOperationError, OrderNotFoundError
from models import (Order, STATUS_CANCELLED, STATUS_DELIVERED, STATUS_NEW,
                    STATUS_PROCESSING, STATUS_SHIPPED, STATUSES)

# Допустимые переходы статусов
TRANSITIONS = {
    STATUS_NEW: (STATUS_PROCESSING, STATUS_CANCELLED),
    STATUS_PROCESSING: (STATUS_SHIPPED, STATUS_CANCELLED),
    STATUS_SHIPPED: (STATUS_DELIVERED, STATUS_CANCELLED),
    STATUS_DELIVERED: (),
    STATUS_CANCELLED: (),
}


class OrderService:
    def __init__(self, orders=None):
        self.orders = orders if orders is not None else []

    def next_id(self):
        return max((order.order_id for order in self.orders), default=0) + 1

    def create_order(self, customer, items):
        order = Order(self.next_id(), customer, items)
        self.orders.append(order)
        return order

    def find_order(self, order_id):
        for order in self.orders:
            if order.order_id == order_id:
                return order
        raise OrderNotFoundError(order_id)

    def find_by_customer(self, customer):
        return [o for o in self.orders if customer.lower() in o.customer.lower()]

    def change_status(self, order_id, new_status):
        if new_status not in STATUSES:
            raise InvalidOrderOperationError(f"Неизвестный статус: {new_status}")
        order = self.find_order(order_id)
        if new_status not in TRANSITIONS[order.status]:
            raise InvalidOrderOperationError(
                f"Нельзя изменить статус «{order.status}» на «{new_status}»")
        order.status = new_status
        return order

    def cancel_order(self, order_id):
        order = self.find_order(order_id)
        if STATUS_CANCELLED not in TRANSITIONS[order.status]:
            raise InvalidOrderOperationError(
                f"Заказ №{order_id} нельзя отменить: его статус «{order.status}»")
        order.status = STATUS_CANCELLED
        return order

    def calculate_cost(self, order_id):
        return self.find_order(order_id).total_cost()