"""Модели предметной области: фитнес-центр (ЛР6, вариант 8)."""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class EntityNotFoundError(Exception):
    """Объект с указанным номером не найден."""


class InvalidStatusChangeError(Exception):
    """Недопустимое изменение состояния абонемента."""


class MembershipStatus(Enum):
    ACTIVE = "активен"
    EXPIRED = "истёк"
    FROZEN = "заморожен"
    CANCELLED = "отменён"


class MembershipType(Enum):
    SINGLE = "разовый"
    MONTHLY = "месячный"
    YEARLY = "годовой"


# Базовые цены абонементов (руб.)
BASE_PRICES: dict[MembershipType, float] = {
    MembershipType.SINGLE: 600.0,
    MembershipType.MONTHLY: 3500.0,
    MembershipType.YEARLY: 32000.0,
}

# Допустимые переходы между статусами абонемента
ALLOWED_TRANSITIONS: dict[MembershipStatus, tuple[MembershipStatus, ...]] = {
    MembershipStatus.ACTIVE: (MembershipStatus.FROZEN, MembershipStatus.EXPIRED,
                              MembershipStatus.CANCELLED),
    MembershipStatus.FROZEN: (MembershipStatus.ACTIVE, MembershipStatus.CANCELLED),
    MembershipStatus.EXPIRED: (),
    MembershipStatus.CANCELLED: (),
}


@dataclass
class Entity:
    """Базовый класс предметной области."""

    id: int
    name: str


@dataclass
class Client(Entity):
    phone: str = ""

    def get_report_data(self) -> str:
        return f"Клиент №{self.id}: {self.name}, тел. {self.phone or 'не указан'}"


@dataclass
class Trainer(Entity):
    specialization: str = ""
    hourly_rate: float = 0.0

    def get_report_data(self) -> str:
        return (f"Тренер №{self.id}: {self.name}, {self.specialization}, "
                f"{self.hourly_rate:.0f} руб./час")


@dataclass
class Membership(Entity):
    """Абонемент. Поле name содержит название вида «месячный №3»."""

    client_id: int = 0
    kind: MembershipType = MembershipType.MONTHLY
    price: float = 0.0
    trainer_id: int = 0
    status: MembershipStatus = MembershipStatus.ACTIVE
    visits: list[date] = field(default_factory=list)

    def change_status(self, new_status: MembershipStatus) -> None:
        if new_status not in ALLOWED_TRANSITIONS[self.status]:
            raise InvalidStatusChangeError(
                f"Нельзя изменить статус «{self.status.value}» на «{new_status.value}»")
        self.status = new_status

    def get_report_data(self) -> str:
        return (f"Абонемент №{self.id}: {self.kind.value}, клиент №{self.client_id}, "
                f"{self.price:.2f} руб., {self.status.value}, посещений: {len(self.visits)}")