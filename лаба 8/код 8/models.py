"""ЛР8, вариант 8. Фитнес-центр: паттерны проектирования.

Сущности и перечисления.
"""
from dataclasses import dataclass
from enum import Enum


class MembershipType(Enum):
    SINGLE = "разовый"
    MONTHLY = "месячный"
    YEARLY = "годовой"


class MembershipStatus(Enum):
    ACTIVE = "активен"
    FROZEN = "заморожен"
    EXPIRED = "истёк"
    CANCELLED = "отменён"


@dataclass
class Client:
    id: int
    name: str
    phone: str = ""


@dataclass
class Membership:
    id: int
    client_id: int
    mtype: MembershipType
    price: float
    status: MembershipStatus = MembershipStatus.ACTIVE