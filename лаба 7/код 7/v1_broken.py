"""ЛР7, вариант 8. Физическое-центр. ВЕРСИЯ 1 - ПРОБЛЕМНАЯ архитектура.

Здесь намеренно нарушены принципы SOLID (см. commented_notes ниже). Эта
версия работает, но плохо расширяется.
"""
from enum import Enum


class MembershipType(Enum):
    SINGLE = "разовый"
    MONTHLY = "месячный"
    YEARLY = "годовой"


# --- Нарушения SOLID ---
# SRP: класс FitnessApp делает всё: хранит данные, печатает, считает, работает с консолью.
# OCP: чтобы добавить тип абонемента, нужно править метод cost() (длинный if/elif).
# DIP: сервис жёстко зависит от SQLite внутри себя (или от консоли).
# LSP/ISP: иерархия проблемная - Membership зависит от всех типов в одном классе.
class FitnessApp:
    def __init__(self):
        self.clients = []
        self.trainers = []
        self.memberships = []

    def register_client(self, name, phone):
        # SRP нарушен: бизнес-логика + хранение
        self.clients.append({"id": len(self.clients) + 1, "name": name, "phone": phone})
        print(f"Клиент {name} зарегистрирован (id={len(self.clients)})")

    def add_trainer(self, name, spec, rate):
        self.trainers.append({"id": len(self.trainers) + 1, "name": name,
                              "spec": spec, "rate": rate})

    def issue_membership(self, client_id, mtype):
        # OCP нарушен: длинный if/elif для расчёта цены по каждому типу
        if mtype == MembershipType.SINGLE:
            price = 600
        elif mtype == MembershipType.MONTHLY:
            price = 3500
        elif mtype == MembershipType.YEARLY:
            price = 32000
        else:
            raise ValueError("Неизвестный тип")
        mid = len(self.memberships) + 1
        self.memberships.append({"id": mid, "client_id": client_id,
                                 "type": mtype, "price": price, "status": "активен"})
        print(f"Оформлен абонемент id={mid}, цена={price}")
        return mid

    def book_training(self, membership_id, trainer_id, date):
        # DIP/сцепление: вся логика на месте, нет разделения на слои
        m = self._find_membership(membership_id)
        if m["status"] != "активен":
            return False, "Абонемент не активен"
        return True, "Запись создана"

    def cancel_training(self, membership_id, training_id):
        return True, "Запись отменена"

    def report(self):
        # SRP нарушен: печать + статистика в приложении
        print("Отчёт:")
        for m in self.memberships:
            print(f"  Абонемент {m['id']}: {m['type'].value}, {m['price']} руб., {m['status']}")

    def _find_membership(self, membership_id):
        return next((m for m in self.memberships if m["id"] == membership_id), None)


def main():
    app = FitnessApp()
    app.add_trainer("Мария", "фитнес", 1200)
    app.register_client("Иван Иванов", "+79151112233")
    mid = app.issue_membership(1, MembershipType.YEARLY)
    ok, msg = app.book_training(mid, 1, "2024-10-10 10:00")
    print(msg)
    app.report()


if __name__ == "__main__":
    main()