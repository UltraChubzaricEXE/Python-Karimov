"""Классы предметной области: заказы (ЛР5, вариант 8)."""

STATUS_ACTIVE = "активен"
STATUS_DONE = "выполнен"
STATUS_CANCELLED = "отменён"

STATUSES = (STATUS_ACTIVE, STATUS_DONE, STATUS_CANCELLED)


class Order:
    """Базовый класс заказа: номер, клиент, стоимость, статус."""

    def __init__(self, number, customer, cost, status=STATUS_ACTIVE):
        if cost < 0:
            raise ValueError("Стоимость заказа не может быть отрицательной")
        if status not in STATUSES:
            raise ValueError(f"Неизвестный статус заказа: {status}")
        self.number = number
        self.customer = customer
        self.cost = cost
        self.status = status

    @property
    def is_active(self):
        return self.status == STATUS_ACTIVE

    def describe(self):
        return f"№{self.number} {self.customer}, {self.cost:.2f} руб., {self.status}"

    def __str__(self):
        return self.describe()


class DeliveryOrder(Order):
    """Заказ с доставкой по адресу."""

    def __init__(self, number, customer, cost, address, status=STATUS_ACTIVE):
        super().__init__(number, customer, cost, status)
        self.address = address

    def describe(self):
        return super().describe() + f", доставка: {self.address}"


class PickupOrder(Order):
    """Заказ с самовывозом из пункта выдачи."""

    def __init__(self, number, customer, cost, point, status=STATUS_ACTIVE):
        super().__init__(number, customer, cost, status)
        self.point = point

    def describe(self):
        return super().describe() + f", самовывоз: {self.point}"