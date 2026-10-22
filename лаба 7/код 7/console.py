"""Пользовательский интерфейс фитнес-центра (ЛР7, вариант 8).

SRP: ConsoleUI отвечает только за взаимодействие с пользователем
(ввод/вывод). Бизнес-логика не содержит input()/print().
"""
from entities import MembershipType
from infrastructure import Repository
from report import ReportGenerator
from service import FitnessService


class ConsoleUI:
    """Консольный интерфейс приложения."""

    def __init__(self, service: FitnessService, repository: Repository) -> None:
        self.service = service
        self.repository = repository

    def run(self) -> None:
        while True:
            print("\n===== ФИТНЕС-ЦЕНТР (SOLID) =====")
            print("1. Зарегистрировать клиента")
            print("2. Добавить тренера")
            print("3. Оформить абонемент")
            print("4. Записаться на тренировку")
            print("5. Отменить запись")
            print("6. Заморозить абонемент")
            print("7. Показать отчёт")
            print("0. Выход")
            choice = input("Выберите пункт: ").strip()
            try:
                if choice == "1":
                    name = self._read_nonempty("Имя клиента: ")
                    phone = input("Телефон: ").strip()
                    self.service.register_client(name, phone)
                elif choice == "2":
                    name = self._read_nonempty("Имя тренера: ")
                    spec = input("Специализация: ").strip()
                    rate = self._read_float("Ставка (руб/час): ")
                    self.service.add_trainer(name, spec, rate)
                elif choice == "3":
                    cid = self._read_int("Номер клиента: ")
                    mtype = self._read_membership_type()
                    self.service.issue_membership(cid, mtype)
                elif choice == "4":
                    mid = self._read_int("Номер абонемента: ")
                    tid = self._read_int("Номер тренера: ")
                    date = input("Дата (ГГГГ-ММ-ДД ЧЧ:ММ): ").strip()
                    self.service.book_training(mid, tid, date)
                elif choice == "5":
                    trid = self._read_int("Номер записи: ")
                    self.service.cancel_training(trid)
                elif choice == "6":
                    mid = self._read_int("Номер абонемента: ")
                    self.service.freeze_membership(mid)
                elif choice == "7":
                    print(ReportGenerator(self.repository).generate())
                elif choice == "0":
                    print("Работа завершена")
                    break
                else:
                    print("Ошибка: нет такого пункта")
            except Exception as exc:
                print("Ошибка:", exc)

    # --- вспомогательный ввод ---
    @staticmethod
    def _read_nonempty(prompt: str) -> str:
        while True:
            v = input(prompt).strip()
            if v:
                return v
            print("Ошибка: пустое значение")

    @staticmethod
    def _read_int(prompt: str) -> int:
        while True:
            v = input(prompt).strip()
            if v.isdigit() and int(v) > 0:
                return int(v)
            print("Ошибка: целое положительное число")

    @staticmethod
    def _read_float(prompt: str) -> float:
        while True:
            v = input(prompt).strip().replace(",", ".")
            try:
                return float(v)
            except ValueError:
                print("Ошибка: число")

    @staticmethod
    def _read_membership_type() -> MembershipType:
        mapping = {"1": MembershipType.SINGLE, "2": MembershipType.MONTHLY,
                   "3": MembershipType.YEARLY}
        while True:
            print("Тип абонемента: 1 - разовый, 2 - месячный, 3 - годовой")
            v = input("Выберите: ").strip()
            if v in mapping:
                return mapping[v]
            print("Ошибка: 1, 2 или 3")