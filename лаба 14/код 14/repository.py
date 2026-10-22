"""Хранилище клиентов фитнес-центра в памяти (ЛР14, вариант 8).

REST API на FastAPI, ресурс /clients. Данные в памяти; для простоты
используем SQLite-совместимую модель через репозиторий.
"""
from dataclasses import dataclass, field


@dataclass
class Client:
    """Клиент фитнес-центра: id и 7 полей."""
    id: int
    name: str
    age: int
    membership: str          # разовый/месячный/годовой
    membership_status: str   # активен/истёк/заморожен/отменён
    goals: list = field(default_factory=list)
    trainer: str = ""
    registered_at: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "membership": self.membership,
            "membership_status": self.membership_status,
            "goals": self.goals,
            "trainer": self.trainer,
            "registered_at": self.registered_at,
        }


class ClientRepository:
    """Репозиторий клиентов (в памяти)."""

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

    def active_memberships(self) -> list[Client]:
        return [c for c in self._items.values() if c.membership_status == "активен"]