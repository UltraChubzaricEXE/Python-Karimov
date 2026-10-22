"""ЛР7, вариант 8. Фитнес-центр. Точка входа.

Демонстрирует обе версии: проблемную (v1) и отрефакторенную (v2).
Для v2 строится граф зависимостей через Dependency Injection:
ConsoleUI -> FitnessService(repository, notifier, pricing) -> Repository.
"""
from console import ConsoleUI
from entities import MembershipStatus, MembershipType
from infrastructure import ConsoleNotifier, InMemoryRepository
from pricing import FamilyPricing, StandardPricing
from report import ReportGenerator
from service import FitnessService


def demo_refactored() -> None:
    """Отрефакторенная версия с Dependency Injection."""
    print("\n--- V2 (SOLID): сборка графа зависимостей (DI) ---")
    repository = InMemoryRepository()
    notifier = ConsoleNotifier()
    service = FitnessService(repository, notifier, pricing=StandardPricing())

    masha = service.add_trainer("Мария", "фитнес", 1200)
    ivan = service.register_client("Иван Иванов", "+79151112233")

    # Стандартная цена
    m1 = service.issue_membership(ivan.id, MembershipType.YEARLY)
    # Семейная стратегия (OCP: смена стратегии без изменения сервиса)
    service.set_pricing(FamilyPricing())
    m2 = service.issue_membership(ivan.id, MembershipType.MONTHLY)

    t1 = service.book_training(m1.id, masha.id, "2024-10-10 10:00")
    service.cancel_training(t1.id)
    service.freeze_membership(m2.id)

    print()
    print(ReportGenerator(repository).generate())


def demo_broken() -> None:
    """Проблемная версия v1 (для сравнения с v2 на защите)."""
    print("\n--- V1 (проблемная): наглядное нарушение SOLID ---")
    import v1_broken
    v1_broken.main()


def main() -> None:
    demo_broken()       # сначала проблемная версия
    demo_refactored()   # затем отрефакторенная


if __name__ == "__main__":
    main()