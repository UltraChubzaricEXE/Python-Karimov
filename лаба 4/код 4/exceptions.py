"""Пользовательские исключения приложения «Заказы» (ЛР4, вариант 8)."""


class OrderError(Exception):
    """Базовое исключение приложения."""


class OrderNotFoundError(OrderError):
    """Заказ с указанным номером не найден."""

    def __init__(self, order_id):
        self.order_id = order_id
        super().__init__(f"Заказ №{order_id} не найден")


class InvalidOrderOperationError(OrderError):
    """Недопустимая операция над заказом (например, отмена выполненного заказа)."""


class StorageError(OrderError):
    """Ошибка чтения или записи файла данных."""