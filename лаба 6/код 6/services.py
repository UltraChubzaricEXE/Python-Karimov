"""Сервисный слой фитнес-центра: бизнес-операции (ЛР6, вариант 8)."""

from collections import Counter
from datetime import date, timedelta

from context import transaction
from decorators import command, log_call, require_status, timed
from models import (BASE_PRICES, Client, EntityNotFoundError, Membership,
                    MembershipStatus, MembershipType, Trainer)


class NoMembershipError(Exception):
    """Клиент не имеет абонементов - невозможно рассчитать посещаемость."""


class FitnessService:
    """Бизнес-операции системы. Методы помечены @command - меню строится автоматически."""

    def __init__(self) -> None:
        self.clients: dict[int, Client] = {}
        self.trainers: dict[int, Trainer] = {}
        self.memberships: dict[int, Membership] = {}
        self._next_id = 1

    # ---------- вспомогательные ----------
    def _new_id(self) -> int:
        value = self._next_id
        self._next_id += 1
        return value

    def _find(self, storage: dict, object_id: int):
        obj = storage.get(object_id)
        if obj is None:
            raise EntityNotFoundError(f"Объект №{object_id} не найден")
        return obj

    def get_client(self, client_id: int) -> Client:
        return self._find(self.clients, client_id)

    def get_trainer(self, trainer_id: int) -> Trainer:
        return self._find(self.trainers, trainer_id)

    def get_membership(self, membership_id: int) -> Membership:
        return self._find(self.memberships, membership_id)

    # ---------- операции ----------
    @command("load_demo", "Загрузить демонстрационные данные")
    @log_call
    def load_demo(self) -> str:
        c1 = self.add_client("Иванов Иван", "+79151112233")
        c2 = self.add_client("Петрова Анна", "+79154445566")
        c3 = self.add_client("Сидоров Павел", "+79157778899")
        self.add_trainer("Тренер Мария", "фитнес, йога", 1200)
        self.add_trainer("Тренер Сергей", "силовые тренировки", 1500)
        self.issue_membership(c1.id, MembershipType.YEARLY, 1)
        self.issue_membership(c2.id, MembershipType.MONTHLY, 1)
        self.issue_membership(c3.id, MembershipType.MONTHLY, 2)
        return "Загружены клиенты и тренеры"

    @command("list_clients", "Список клиентов")
    def list_clients(self) -> str:
        if not self.clients:
            return "Клиентов нет"
        return "\n".join(self.get_client(i).get_report_data() for i in sorted(self.clients))

    @command("list_trainers", "Список тренеров")
    def list_trainers(self) -> str:
        if not self.trainers:
            return "Тренеров нет"
        return "\n".join(self.get_trainer(i).get_report_data() for i in sorted(self.trainers))

    @command("list_memberships", "Список абонементов")
    def list_memberships(self) -> str:
        if not self.memberships:
            return "Абонементов нет"
        return "\n".join(self.get_membership(i).get_report_data()
                         for i in sorted(self.memberships))

    @command("add_client", "Добавить клиента")
    def add_client(self, name: str, phone: str = "") -> Client:
        client = Client(self._new_id(), name, phone)
        self.clients[client.id] = client
        return client

    @command("add_trainer", "Добавить тренера")
    def add_trainer(self, name: str, specialization: str, hourly_rate: float = 0) -> Trainer:
        trainer = Trainer(self._new_id(), name, specialization, hourly_rate)
        self.trainers[trainer.id] = trainer
        return trainer

    @command("find", "Найти объект по номеру")
    def find_entity(self, kind: str, object_id: int):
        if kind == "clients":
            return self.get_client(object_id)
        if kind == "trainers":
            return self.get_trainer(object_id)
        if kind == "memberships":
            return self.get_membership(object_id)
        raise EntityNotFoundError(f"Неизвестная категория: {kind}")

    @command("issue_membership", "Оформить абонемент")
    @log_call
    def issue_membership(self, client_id: int, kind: MembershipType, trainer_id: int = 0) -> Membership:
        self.get_client(client_id)
        if trainer_id:
            self.get_trainer(trainer_id)
        price = BASE_PRICES[kind]
        membership = Membership(self._new_id(), f"{kind.value} №{self._next_id - 1}",
                                client_id=client_id, kind=kind, price=price,
                                trainer_id=trainer_id)
        self.memberships[membership.id] = membership
        return membership

    @command("change_status", "Изменить статус абонемента")
    @log_call
    def change_status(self, membership_id: int, new_status: MembershipStatus) -> Membership:
        membership = self.get_membership(membership_id)
        membership.change_status(new_status)
        return membership

    @command("record_visit", "Отметить посещение тренировки")
    @require_status(MembershipStatus.ACTIVE)
    def record_visit(self, membership_id: int, day: str) -> Membership:
        membership = self.get_membership(membership_id)
        visit_date = date.fromisoformat(day)
        membership.visits.append(visit_date)
        return membership

    @command("attendance", "Определить посещаемость клиента")
    def attendance(self, client_id: int) -> str:
        self.get_client(client_id)
        memberships = [m for m in self.memberships.values() if m.client_id == client_id]
        if not memberships:
            raise NoMembershipError("У клиента нет абонементов - невозможно рассчитать посещаемость")
        visits = [v for m in memberships for v in m.visits]
        total = len(visits)
        recent = sum(1 for v in visits if v >= date.today() - timedelta(days=30))
        if not visits:
            return "Посещений нет"
        week_average = total / (max((visits[-1] - visits[0]).days, 1) / 7)
        if week_average >= 3:
            rating = "высокая"
        elif week_average >= 1:
            rating = "средняя"
        else:
            rating = "низкая"
        return (f"Всего посещений: {total}, за 30 дней: {recent}, "
                f"в среднем в неделю: {week_average:.1f}, посещаемость: {rating}")

    @command("calculate_cost", "Рассчитать стоимость абонемента")
    @timed
    def calculate_cost(self, membership_id: int) -> str:
        membership = self.get_membership(membership_id)
        total = membership.price
        if membership.trainer_id:
            trainer = self.get_trainer(membership.trainer_id)
            total += trainer.hourly_rate  # персональная тренировка
        return f"Стоимость абонемента №{membership.id}: {total:.2f} руб."

    @command("stats", "Статистика")
    @timed
    def statistics(self) -> str:
        counters = Counter(m.status for m in self.memberships.values())
        revenue = sum(m.price for m in self.memberships.values()
                      if m.status != MembershipStatus.CANCELLED)
        prices = [m.price for m in self.memberships.values()]
        avg = sum(prices) / len(prices) if prices else 0
        return (f"Клиентов: {len(self.clients)}, тренеров: {len(self.trainers)}, "
                f"абонементов: {len(self.memberships)}, по статусам: "
                f"{dict((k.value, v) for k, v in counters.items())}, "
                f"выручка: {revenue:.2f}, средняя цена: {avg:.2f}, "
                f"мин.: {min(prices):.2f}, макс.: {max(prices):.2f}" if prices else "нет данных")

    @command("repeat_demo", "Повторить операцию 3 раза (декоратор @repeat)")
    def repeat_demo(self) -> str:
        return "repeat демонстрация"

    @command("inspect", "Интроспекция объекта")
    def inspect_object(self, kind: str, object_id: int) -> str:
        from introspection import inspect_object as _inspect
        obj = self.find_entity(kind, object_id)
        _inspect(obj)
        return "Интроспекция завершена"

    @command("transaction_demo", "Демонстрация транзакции")
    def transaction_demo(self) -> str:
        with transaction(self.memberships):
            m = self.issue_membership(1, MembershipType.MONTHLY, 0)
        return "Абонемент добавлен в рамках транзакции"