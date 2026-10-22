"""Сервисный слой клиентов фитнес-центра (ЛР14, вариант 8)."""
from repository import Client, ClientRepository


class ClientNotFoundError(Exception):
    pass


class ClientService:
    """Бизнес-логика. Репозиторий передаётся через конструктор (DIP)."""

    def __init__(self, repository: ClientRepository) -> None:
        self.repository = repository

    def list_clients(self, status=None, membership=None, sort=None, order="asc",
                     limit=20, offset=0) -> list[Client]:
        clients = self.repository.get_all()
        if status:
            clients = [c for c in clients if (c.membership_status or "").lower() == status.lower()]
        if membership:
            clients = [c for c in clients if (c.membership or "").lower() == membership.lower()]
        if sort in ("age", "name"):
            clients = sorted(clients, key=lambda c: getattr(c, sort), reverse=(order == "desc"))
        return clients[offset:offset + limit]

    def total(self, status=None, membership=None) -> int:
        clients = self.repository.get_all()
        if status:
            clients = [c for c in clients if (c.membership_status or "").lower() == status.lower()]
        if membership:
            clients = [c for c in clients if (c.membership or "").lower() == membership.lower()]
        return len(clients)

    def get_client(self, client_id: int) -> Client:
        client = self.repository.get_by_id(client_id)
        if client is None:
            raise ClientNotFoundError(f"Клиент с номером {client_id} не найден")
        return client

    def create_client(self, data: dict) -> Client:
        client = Client(id=0, **data)
        return self.repository.create(client)

    def update_client(self, client_id: int, data: dict) -> Client:
        existing = self.get_client(client_id)
        payload = existing.to_dict()
        payload.update({k: v for k, v in data.items() if v is not None})
        payload["id"] = client_id
        return self.repository.update(Client(**payload))

    def delete_client(self, client_id: int) -> None:
        self.get_client(client_id)
        self.repository.delete(client_id)

    def active_memberships(self) -> list[Client]:
        return self.repository.active_memberships()

    def statistics(self) -> dict:
        clients = self.repository.get_all()
        if not clients:
            return {"total": 0, "avg_age": 0, "by_status": {}}
        by_status = {}
        for c in clients:
            by_status[c.membership_status] = by_status.get(c.membership_status, 0) + 1
        return {
            "total": len(clients),
            "avg_age": round(sum(c.age for c in clients) / len(clients), 2),
            "by_status": by_status,
        }

    def search(self, q: str) -> list[Client]:
        ql = q.lower()
        return [c for c in self.repository.get_all() if ql in c.name.lower()]