"""ЛР8, вариант 8. Сервис фитнес-центра с паттерном Observer (Subject).

Subject (сервис) хранит список наблюдателей и уведомляет их обо всех
изменениях. Сервис также использует Repository (хранение) и Factory +
Strategy (создание абонементов).
"""
from interfaces import Observer, Repository
from factories import MembershipFactory, StandardPricing
from models import Client, Membership, MembershipStatus
from observers import StatisticsObserver


class DomainError(Exception):
    pass


class FitnessService:
    """Бизнес-логика + Source-событий (паттерн Observer)."""

    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self._observers: list[Observer] = []
        self._pricing = StandardPricing()

    # --- паттерн Observer ---
    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def _notify(self, event: str, payload: dict) -> None:
        for observer in self._observers:
            observer.update(event, payload)

    def set_pricing(self, strategy) -> None:
        self._pricing = strategy

    # --- операции ---
    def register_client(self, name: str, phone: str = "") -> Client:
        if not name.strip():
            raise DomainError("Имя клиента обязательно")
        client = self.repository.add_client(Client(0, name.strip(), phone.strip()))
        self._notify("client_created", {"id": client.id, "name": client.name})
        return client

    def issue_membership(self, client_id: int, mtype) -> Membership:
        spec = MembershipFactory.create(mtype, self._pricing)
        membership = self.repository.add_membership(spec.build(client_id))
        self._notify("membership_created", {"id": membership.id,
                                            "type": mtype.value,
                                            "price": membership.price})
        return membership

    def freeze_membership(self, membership_id: int) -> Membership:
        m = self.repository.get_membership(membership_id)
        if m is None:
            raise DomainError("Абонемент не найден")
        if m.status != MembershipStatus.ACTIVE:
            raise DomainError("Заморозить можно только активный абонемент")
        m.status = MembershipStatus.FROZEN
        self._notify("membership_frozen", {"id": membership_id})
        return m