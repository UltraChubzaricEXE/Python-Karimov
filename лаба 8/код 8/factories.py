"""ЛР8, вариант 8. Паттерны Strategy и Factory.

Strategy: взаимозаменяемые алгоритмы расчёта цены абонемента.
Factory: создание объектов семейства абонементов по типу.
"""
from models import Membership, MembershipType

# Базовые цены далее — фактически доставка из стратегии
BASE_PRICES = {
    MembershipType.SINGLE: 600.0,
    MembershipType.MONTHLY: 3500.0,
    MembershipType.YEARLY: 32000.0,
}


# ---------- Strategy ----------
class StandardPricing:
    """Стандартная цена."""

    def calculate(self, base_price: float) -> float:
        return base_price


class DiscountPricing:
    """Цена со скидкой."""

    def __init__(self, percent: float = 10.0) -> None:
        self.percent = percent

    def calculate(self, base_price: float) -> float:
        return round(base_price * (1 - self.percent / 100), 2)


class FamilyPricing:
    """Семейный тариф: фиксированная скидка."""

    def calculate(self, base_price: float) -> float:
        return round(base_price - 300, 2)


# ---------- Factory ----------
class MembershipFactory:
    """Паттерн Factory: создаёт абонемент нужного типа с ценой.

    Комбинация Factory + Strategy: фабрика принимает стратегию ценообразования.
    """

    @staticmethod
    def create(mtype: MembershipType, strategy=None) -> "MembershipSpec":
        base = BASE_PRICES[mtype]
        price = (strategy or StandardPricing()).calculate(base)
        return MembershipSpec(mtype, price)


class MembershipSpec:
    """Спецификация абонемента (результат фабрики)."""

    def __init__(self, mtype: MembershipType, price: float) -> None:
        self.mtype = mtype
        self.price = price

    def build(self, client_id: int) -> Membership:
        return Membership(0, client_id=client_id, mtype=self.mtype, price=self.price)