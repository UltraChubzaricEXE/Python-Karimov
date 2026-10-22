"""ЛР8, вариант 8. Паттерны: интерфейсы и абстракции.

Наивысшеуровневые абстракции системы на Protocol.
"""
from typing import Protocol

from models import Membership, MembershipType


class Repository(Protocol):
    """Паттерн Repository: изоляция хранения от бизнес-логики."""

    def add_client(self, client) -> ...: ...
    def add_membership(self, membership: Membership) -> Membership: ...
    def get_membership(self, membership_id: int) -> Membership | None: ...
    def all_memberships(self) -> list[Membership]: ...


class PricingStrategy(Protocol):
    """Паттерн Strategy: алгоритм расчёта цены."""

    def calculate(self, base_price: float) -> float: ...


class Observer(Protocol):
    """Паттерн Observer: получатель уведомлений об изменениях."""

    def update(self, event: str, payload: dict) -> None: ...