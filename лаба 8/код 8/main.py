"""ЛР8, вариант 8. Фитнес-центр: паттерны проектирования.

Демонстрация: Repository (две реализации), Factory + Strategy, Observer.
"""
from factories import DiscountPricing, FamilyPricing
from interfaces import Repository
from models import MembershipType
from observers import EventLogObserver, NotificationObserver, StatisticsObserver
from repositories import FileRepository, InMemoryRepository
from service import FitnessService


def demo(repository: Repository) -> FitnessService:
    """Запускает демонстрацию на переданном репозитории."""
    print("\n=== ДЕМО (репозиторий:", type(repository).__name__, ") ===")
    service = FitnessService(repository)

    # Observer: подключаем три наблюдателя
    logger = EventLogObserver()
    notifier = NotificationObserver()
    stats = StatisticsObserver()
    for obs in (logger, notifier, stats):
        service.attach(obs)

    client = service.register_client("Иван Иванов", "+79151112233")

    # Factory + стандартная стратегия
    m1 = service.issue_membership(client.id, MembershipType.YEARLY)
    # Смена стратегии без изменения сервиса (Strategy)
    service.set_pricing(FamilyPricing())
    m2 = service.issue_membership(client.id, MembershipType.MONTHLY)
    service.set_pricing(DiscountPricing(15))
    m3 = service.issue_membership(client.id, MembershipType.SINGLE)
    service.freeze_membership(m2.id)

    print(f"Оформлено абонементов: {m1.id}, {m2.id}, {m3.id}")
    print("Событий в журнале:", len(logger.events))
    print("Сообщений уведомления:", len(notifier.messages))
    print("Статистика событий:", stats.counts)
    return service


def main() -> None:
    print("===== ЛР8. Паттерны проектирования (фитнес-центр) =====")
    # Выбор реализации репозитория (доп. задание: две реализации интерфейса)
    choice = input("Хранилище: 1 - память, 2 - файл: ").strip()
    repo = InMemoryRepository() if choice == "2" else FileRepository("l8.json")
    demo(repo)


if __name__ == "__main__":
    main()