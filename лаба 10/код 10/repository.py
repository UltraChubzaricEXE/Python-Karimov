"""Хранилище клиентов фитнес-центра (в памяти).
ЛР10, вариант 8."""
from models import Client


class ClientRepository:
    """Репозиторий клиентов с CRUD-операциями."""

    def __init__(self) -> None:
        self._items: dict[int, Client] = {}
        self._next_id: int = 1

    def get_all(self) -> list[Client]:
        return list(self._items.values())

    def get_by_id(self, client_id: int) -> Client | None:
        return self._items.get(client_id)

    def create(self, client: Client) -> Client:
        client.id = self._next_id
        self._next_id += 1
        self._items[client.id] = client
        return client

    def update(self, client: Client) -> Client:
        if client.id not in self._items:
            raise KeyError(client.id)
        self._items[client.id] = client
        return client

    def delete(self, client_id: int) -> bool:
        if client_id in self._items:
            del self._items[client_id]
            return True
        return False

    def find_active_memberships(self) -> list[Client]:
        """Специализированная операция: активные абонементы."""
        return [c for c in self._items.values() if c.membership_status == "активен"]