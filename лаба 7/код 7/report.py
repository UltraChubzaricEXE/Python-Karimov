"""Формирование отчётов (ЛР7, вариант 8).

SRP: ReportGenerator отвечает только за подготовку статистики/отчёта,
не за бизнес-логику и не за вывод в консоль.
"""
from infrastructure import Repository


class ReportGenerator:
    """Готовит текстовый отчёт о состоянии фитнес-центра."""

    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def generate(self) -> str:
        memberships = self.repository.all_memberships()
        trainings = self.repository.all_trainings()
        lines = []
        lines.append("===== ОТЧЁТ ФИТНЕС-ЦЕНТРА =====")
        lines.append(f"Всего абонементов: {len(memberships)}")
        by_status = {}
        for m in memberships:
            st = m.status.value
            by_status[st] = by_status.get(st, 0) + 1
        for st, cnt in by_status.items():
            lines.append(f"  {st}: {cnt}")
        total_revenue = sum(m.price for m in memberships
                            if m.status.value in ("активен", "заморожен"))
        lines.append(f"Выручка (активные + замороженные): {total_revenue:.2f} руб.")
        lines.append(f"Записей на тренировки: {len(trainings)}")
        scheduled = sum(1 for t in trainings if t.status.value == "запланирована")
        lines.append(f"  запланировано: {scheduled}")
        return "\n".join(lines)