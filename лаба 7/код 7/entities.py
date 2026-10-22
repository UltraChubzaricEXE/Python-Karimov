"""ЛР7, вариант 8. Фитнес-центр. ВЕРСИЯ 2 - СООТВЕТСТВУЕТ SOLID.

Многослойная архитектура: entities, enums, repository (интерфейс),
pricing (стратегии ценообразования - OCP), notifier (уведомления - DIP),
service (бизнес-логика), report (SRP), console (UI).
"""
from dataclasses import dataclass, field
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


class TrainingStatus(Enum):
    SCHEDULED = "запланирована"
    DONE = "проведена"
    CANCELLED = "отменена"


@dataclass
class Client:
    id: int
    name: str
    phone: str = ""


@dataclass
class Trainer:
    id: int
    name: str
    specialization: str
    hourly_rate: float = 0.0


@dataclass
class Membership:
    id: int
    client_id: int
    mtype: MembershipType
    price: float
    status: MembershipStatus = MembershipStatus.ACTIVE
    trainer_id: int = 0


@dataclass
class Training:
    id: int
    membership_id: int
    trainer_id: int
    date: str
    status: TrainingStatus = TrainingStatus.SCHEDULED