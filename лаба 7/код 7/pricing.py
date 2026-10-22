"""Ценообразование абонементов (ЛР7, вариант 8).

OCP: цена вычисляется выделенной стратегией PricingStrategy. Добавление
нового типа абонемента не требует изменения сервиса - достаточно новой
стратегии. Тонкая абстракция соответствует ISP.
"""
from abc import ABC, abstractmethod

from entities import MembershipType


class PricingStrategy(ABC):
    """Базовый интерфейс стратегии ценообразования (ISP: минимальный)."""

    @abstractmethod
    def calculate(self, base_price: float, *args) -> float:
        ...


class StandardPricing(PricingStrategy):
    """Обычная цена без скидок."""

    def calculate(self, base_price: float, *args) -> float:
        return base_price


class DiscountPricing(PricingStrategy):
    """Цена со скидкой на один процент."""

    def __init__(self, discount_percent: float = 10.0) -> None:
        self.discount = discount_percent

    def calculate(self, base_price: float, *args) -> float:
        return round(base_price * (1 - self.discount / 100), 2)


class FamilyPricing(PricingStrategy):
    """Семейный тариф: фиксированная скидка."""

    def calculate(self, base_price: float, *args) -> float:
        return round(base_price - 300, 2)


# Базовые цены по типам абонементов.
BASE_PRICES: dict[MembershipType, float] = {
    MembershipType.SINGLE: 600.0,
    MembershipType.MONTHLY: 3500.0,
    MembershipType.YEARLY: 32000.0,
}


def price_for(mtype: MembershipType, strategy: PricingStrategy) -> float:
    """Возвращает цену абонемента по его типу и стратегии."""
    base = BASE_PRICES[mtype]
    return strategy.calculate(base)