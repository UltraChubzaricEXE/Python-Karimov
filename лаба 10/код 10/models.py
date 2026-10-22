"""Модель клиента фитнес-центра для REST API (ЛР10, вариант 8)."""
from dataclasses import dataclass, field


@dataclass
class Client:
    """Клиент фитнес-центра: минимум 5 полей + id."""
    id: int
    name: str
    age: int
    membership: str            # тип абонемента: разовый/месячный/годовой
    membership_status: str     # активен/истёк/заморожен/отменён
    goals: list = field(default_factory=list)
    trainer: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "membership": self.membership,
            "membership_status": self.membership_status,
            "goals": self.goals,
            "trainer": self.trainer,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Client":
        return cls(
            id=data.get("id", 0),
            name=data["name"],
            age=data.get("age", 0),
            membership=data.get("membership", "месячный"),
            membership_status=data.get("membership_status", "активен"),
            goals=list(data.get("goals", [])),
            trainer=data.get("trainer", ""),
        )