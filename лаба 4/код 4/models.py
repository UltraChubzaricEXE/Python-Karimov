"""Классы предметной области: товар и заказ (ЛР4, вариант 8)."""

STATUS_NEW = "новый"
STATUS_PROCESSING = "в обработке"
STATUS_SHIPPED = "отправлен"
STATUS_DELIVERED = "доставлен"
STATUS_CANCELLED = "отменён"

STATUSES = (STATUS_NEW, STATUS_PROCESSING, STATUS_SHIPPED,
            STATUS_DELIVERED, STATUS_CANCELLED)


class Item:
    """Товар в заказе."""

    def __init__(self, name, price, quantity):
        if not name:
            raise ValueError("Название товара не может быть пустым")
        if price <= 0:
            raise ValueError("Цена должна быть положительной")
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        self.name = name
        self.price = price
        self.quantity = quantity

    def cost(self):
        return self.price * self.quantity

    def to_dict(self):
        return {"name": self.name, "price": self.price, "quantity": self.quantity}

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["price"], data["quantity"])


class Order:
    """Заказ: номер, клиент, список товаров, статус. Стоимость вычисляется."""

    def __init__(self, order_id, customer, items, status=STATUS_NEW):
        if not customer:
            raise ValueError("Имя клиента не может быть пустым")
        if not items:
            raise ValueError("Заказ должен содержать хотя бы один товар")
        if status not in STATUSES:
            raise ValueError(f"Неизвестный статус: {status}")
        self.order_id = order_id
        self.customer = customer
        self.items = items
        self.status = status

    def total_cost(self):
        return sum(item.cost() for item in self.items)

    def to_dict(self):
        return {
            "id": self.order_id,
            "customer": self.customer,
            "items": [item.to_dict() for item in self.items],
            "cost": self.total_cost(),
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data):
        items = [Item.from_dict(item) for item in data["items"]]
        return cls(data["id"], data["customer"], items, data["status"])

    def __str__(self):
        goods = ", ".join(f"{i.name} x{i.quantity}" for i in self.items)
        return (f"№{self.order_id} | {self.customer} | {goods} | "
                f"{self.total_cost():.2f} руб. | {self.status}")