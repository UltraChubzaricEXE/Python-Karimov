"""Интерфейсы хранилища и уведомлений (ЛР7, вариант 8).

DIP: сервис зависит от абстракций Repository и Notifier, а не от
конкретных реализаций. ISP: интерфейсы минимальны и специализированы.
"""
from typing import Protocol

from entities import Client, Membership, Trainer, Training


class Repository(Protocol):
    """Абстракция хранилища (DIP)."""

    def add_client(self, client: Client) -> Client: ...
    def add_trainer(self, trainer: Trainer) -> Trainer: ...
    def add_membership(self, membership: Membership) -> Membership: ...
    def add_training(self, training: Training) -> Training: ...
    def get_client(self, client_id: int) -> Client | None: ...
    def get_membership(self, membership_id: int) -> Membership | None: ...
    def get_trainer(self, trainer_id: int) -> Trainer | None: ...
    def all_memberships(self) -> list[Membership]: ...
    def all_trainings(self) -> list[Training]: ...


class Notifier(Protocol):
    """Абстракция уведомлений (DIP). Клиент не зависит от конкретного способа."""

    def notify(self, message: str) -> None: ...


class InMemoryRepository(Repository):
    """Реализация хранилища в памяти (LSP: заменяет Repository)."""

    def __init__(self) -> None:
        self._clients: dict[int, Client] = {}
        self._trainers: dict[int, Trainer] = {}
        self._memberships: dict[int, Membership] = {}
        self._trainings: dict[int, Training] = {}
        self._next: dict[str, int] = {"c": 1, "t": 1, "m": 1, "tr": 1}

    def add_client(self, client: Client) -> Client:
        client.id = self._next["c"]; self._next["c"] += 1
        self._clients[client.id] = client
        return client

    def add_trainer(self, trainer: Trainer) -> Trainer:
        trainer.id = self._next["t"]; self._next["t"] += 1
        self._trainers[trainer.id] = trainer
        return trainer

    def add_membership(self, membership: Membership) -> Membership:
        membership.id = self._next["m"]; self._next["m"] += 1
        self._memberships[membership.id] = membership
        return membership

    def add_training(self, training: Training) -> Training:
        training.id = self._next["tr"]; self._next["tr"] += 1
        self._trainings[training.id] = training
        return training

    def get_client(self, client_id: int) -> Client | None:
        return self._clients.get(client_id)

    def get_membership(self, membership_id: int) -> Membership | None:
        return self._memberships.get(membership_id)

    def get_trainer(self, trainer_id: int) -> Trainer | None:
        return self._trainers.get(trainer_id)

    def all_memberships(self) -> list[Membership]:
        return list(self._memberships.values())

    def all_trainings(self) -> list[Training]:
        return list(self._trainings.values())


class ConsoleNotifier(Notifier):
    """Уведомление в консоль (реализация Notifier)."""

    def notify(self, message: str) -> None:
        print("[Уведомление]", message)


class FileNotifier(Notifier):
    """Альтернативная реализация Notifier - запись в файл (LSP/DIP)."""

    def __init__(self, filename: str = "notifications.log") -> None:
        self.filename = filename

    def notify(self, message: str) -> None:
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(message + "\n")