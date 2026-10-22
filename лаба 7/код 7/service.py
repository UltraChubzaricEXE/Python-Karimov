"""Бизнес-логика фитнес-центра (ЛР7, вариант 8).

SRP: сервис отвечает только за бизнес-операции (запись, отмена, оформление).
DIP: получает Repository и Notifier через конструктор (Dependency Injection).
OCP: цена берётся из стратегии, а не из if/elif.
"""
from entities import Client, Membership, MembershipStatus, Trainer, Training, TrainingStatus
from infrastructure import Repository, Notifier
from pricing import PricingStrategy, price_for


class DomainError(Exception):
    """Ошибка предметной области."""


class FitnessService:
    def __init__(self, repository: Repository, notifier: Notifier,
                 pricing: PricingStrategy | None = None) -> None:
        self.repository = repository
        self.notifier = notifier
        self._pricing = pricing  # стратегия ценообразования (внедряется)

    def set_pricing(self, pricing: PricingStrategy) -> None:
        """Позволяет сменить стратегию ценообразования без изменения сервиса (OCP)."""
        self._pricing = pricing

    def register_client(self, name: str, phone: str = "") -> Client:
        if not name.strip():
            raise DomainError("Имя клиента обязательно")
        client = self.repository.add_client(Client(0, name.strip(), phone.strip()))
        self.notifier.notify(f"Клиент {client.name} зарегистрирован (id={client.id})")
        return client

    def add_trainer(self, name: str, specialization: str, hourly_rate: float = 0) -> Trainer:
        trainer = self.repository.add_trainer(Trainer(0, name.strip(), specialization.strip(), hourly_rate))
        self.notifier.notify(f"Добавлен тренер {trainer.name}")
        return trainer

    def issue_membership(self, client_id: int, mtype, strategy: PricingStrategy | None = None) -> Membership:
        client = self.repository.get_client(client_id)
        if client is None:
            raise DomainError("Клиент не найден")
        s = strategy or self._pricing
        if s is None:
            from pricing import StandardPricing
            s = StandardPricing()
        price = price_for(mtype, s)
        membership = self.repository.add_membership(
            Membership(0, client_id=client_id, mtype=mtype, price=price))
        self.notifier.notify(
            f"Оформлен абонемент {mtype.value} для клиента {client.name}, цена {price} руб.")
        return membership

    def book_training(self, membership_id: int, trainer_id: int, date: str) -> Training:
        membership = self.repository.get_membership(membership_id)
        if membership is None:
            raise DomainError("Абонемент не найден")
        if membership.status != MembershipStatus.ACTIVE:
            raise DomainError(f"Нельзя записаться: статус абонемента {membership.status.value}")
        if self.repository.get_trainer(trainer_id) is None:
            raise DomainError("Тренер не найден")
        training = self.repository.add_training(Training(0, membership_id, trainer_id, date))
        self.notifier.notify(f"Запись на тренировку #{training.id} создана")
        return training

    def cancel_training(self, training_id: int) -> Training:
        training = next((t for t in self.repository.all_trainings() if t.id == training_id), None)
        if training is None:
            raise DomainError("Запись не найдена")
        if training.status == TrainingStatus.CANCELLED:
            raise DomainError("Запись уже отменена")
        training.status = TrainingStatus.CANCELLED
        self.notifier.notify(f"Запись #{training.id} отменена")
        return training

    def freeze_membership(self, membership_id: int) -> Membership:
        membership = self.repository.get_membership(membership_id)
        if membership is None:
            raise DomainError("Абонемент не найден")
        if membership.status != MembershipStatus.ACTIVE:
            raise DomainError("Заморозить можно только активный абонемент")
        membership.status = MembershipStatus.FROZEN
        self.notifier.notify(f"Абонемент #{membership.id} заморожен")
        return membership