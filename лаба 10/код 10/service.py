"""Сервисный слой клиентов фитнес-центра. ЛР10, вариант 8."""
from models import Client


class ClientNotFoundError(Exception):
    pass


class ValidationError(Exception):
    pass


class ClientService:
    """Бизнес-логика: валидация и операции с клиентами."""

    MEMBERSHIPS = ("разовый", "месячный", "годовой")
    STATUSES = ("активен", "истёк", "заморожен", "отменён")

    def __init__(self, repository) -> None:
        self.repository = repository

    def _validate(self, data: dict) -> None:
        if not isinstance(data.get("name"), str) or not data["name"].strip():
            raise ValidationError("Имя клиента не может быть пустым")
        if not isinstance(data.get("age"), int) or not 0 < data["age"] < 130:
            raise ValidationError("Возраст должен быть целым числом от 1 до 129")
        if data.get("membership") not in self.MEMBERSHIPS:
            raise ValidationError(f"Недопустимый тип абонемента: {data.get('membership')}")
        if data.get("membership_status") not in self.STATUSES:
            raise ValidationError(f"Недопустимый статус: {data.get('membership_status')}")

    def list_clients(self):
        return self.repository.get_all()

    def get_client(self, client_id: int) -> Client:
        client = self.repository.get_by_id(client_id)
        if client is None:
            raise ClientNotFoundError("Клиент не найден")
        return client

    def create_client(self, data: dict) -> Client:
        self._validate(data)
        client = Client.from_dict({**data, "id": 0})
        return self.repository.create(client)

    def update_client(self, client_id: int, data: dict) -> Client:
        self.get_client(client_id)
        self._validate(data)
        client = Client.from_dict({**data, "id": client_id})
        return self.repository.update(client)

    def patch_client(self, client_id: int, data: dict) -> Client:
        existing = self.get_client(client_id).to_dict()
        for key, value in data.items():
            if value is not None:
                existing[key] = value
        return self.update_client(client_id, existing)

    def delete_client(self, client_id: int) -> None:
        self.get_client(client_id)
        self.repository.delete(client_id)

    def active_memberships(self) -> list:
        return self.repository.find_active_memberships()

    def filter_and_sort(self, status: str | None = None,
                        membership: str | None = None,
                        sort: str | None = None,
                        order: str = "asc") -> list:
        clients = self.repository.get_all()
        if status:
            clients = [c for c in clients if (c.membership_status or "").lower() == status.lower()]
        if membership:
            clients = [c for c in clients if (c.membership or "").lower() == membership.lower()]
        if sort in ("age", "name"):
            clients = sorted(clients, key=lambda c: getattr(c, sort), reverse=(order == "desc"))
        return clients