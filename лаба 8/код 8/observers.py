"""ЛР8, вариант 8. Паттерн Observer: наблюдатели событий фитнес-центра.

Минимум три независимых наблюдателя: Logger, Notification, Statistics.
"""
from interfaces import Observer


class EventLogObserver(Observer):
    """Наблюдатель-журнал: пишет события в список."""

    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def update(self, event: str, payload: dict) -> None:
        self.events.append((event, payload))


class NotificationObserver(Observer):
    """Наблюдатель-уведомление: формирует текстовые сообщения для клиента."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def update(self, event: str, payload: dict) -> None:
        text = f"[уведомление] {event}: {payload}"
        self.messages.append(text)


class StatisticsObserver(Observer):
    """Наблюдатель-статистика: ведёт счётчики по типам событий."""

    def __init__(self) -> None:
        self.counts: dict[str, int] = {}

    def update(self, event: str, payload: dict) -> None:
        self.counts[event] = self.counts.get(event, 0) + 1