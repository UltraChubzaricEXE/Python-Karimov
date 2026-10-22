"""ЛР8, вариант 8. Паттерн Repository: хранение в памяти и в файле.

Для повышенной оценки реализованы два хранилища: InMemoryRepository и
FileRepository, взаимозаменяемые через интерфейс Repository.
"""
import json
import os

from interfaces import Repository
from models import Client, Membership, MembershipStatus, MembershipType


class InMemoryRepository(Repository):
    """Хранилище абонементов и клиентов в памяти."""

    def __init__(self) -> None:
        self._clients: dict[int, Client] = {}
        self._memberships: dict[int, Membership] = {}
        self._next: dict[str, int] = {"c": 1, "m": 1}

    def add_client(self, client: Client) -> Client:
        client.id = self._next["c"]; self._next["c"] += 1
        self._clients[client.id] = client
        return client

    def add_membership(self, membership: Membership) -> Membership:
        membership.id = self._next["m"]; self._next["m"] += 1
        self._memberships[membership.id] = membership
        return membership

    def get_membership(self, membership_id: int) -> Membership | None:
        return self._memberships.get(membership_id)

    def all_memberships(self) -> list[Membership]:
        return list(self._memberships.values())


class FileRepository(Repository):
    """Альтернативное хранилище: JSON-файл (LSP + DIP, вторая реализация)."""

    def __init__(self, filename: str = "memberships.json") -> None:
        self.filename = filename
        self._clients: dict[int, Client] = {}
        self._memberships: dict[int, Membership] = {}
        self._next: dict[str, int] = {"c": 1, "m": 1}
        if os.path.exists(filename):
            self._load()

    def _serialize_membership(self, m: Membership) -> dict:
        return {"id": m.id, "client_id": m.client_id,
                "mtype": m.mtype.name, "price": m.price, "status": m.status.name}

    def add_client(self, client: Client) -> Client:
        client.id = self._next["c"]; self._next["c"] += 1
        self._clients[client.id] = client
        return client

    def add_membership(self, membership: Membership) -> Membership:
        membership.id = self._next["m"]; self._next["m"] += 1
        self._memberships[membership.id] = membership
        self._save()
        return membership

    def get_membership(self, membership_id: int) -> Membership | None:
        return self._memberships.get(membership_id)

    def all_memberships(self) -> list[Membership]:
        return list(self._memberships.values())

    def _save(self) -> None:
        data = [self._serialize_membership(m) for m in self._memberships.values()]
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load(self) -> None:
        with open(self.filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        max_id = 0
        for item in data:
            m = Membership(item["id"], client_id=item["client_id"],
                           mtype=MembershipType[item["mtype"]],
                           price=item["price"],
                           status=MembershipStatus[item["status"]])
            self._memberships[m.id] = m
            max_id = max(max_id, m.id)
        self._next["m"] = max_id + 1