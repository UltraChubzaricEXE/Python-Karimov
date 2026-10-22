"""Лабораторная работа №2. Вариант 8.

Банковские счета: обработка набора данных с помощью коллекций Python.
Каждый счёт - словарь с ключами: number, owner, type, balance.
"""

# Допустимые типы счетов (кортеж - неизменяемая коллекция)
ACCOUNT_TYPES = ("текущий", "сберегательный", "депозитный", "кредитный")

DEMO_ACCOUNTS = [
    ("40817001", "Иванов Иван", "текущий", 15000.0),
    ("40817002", "Петрова Анна", "сберегательный", 250000.0),
    ("40817003", "Иванов Иван", "депозитный", 500000.0),
    ("40817004", "Сидоров Павел", "текущий", 3200.5),
    ("40817005", "Петрова Анна", "текущий", 78000.0),
    ("40817006", "Козлов Артём", "сберегательный", 120000.0),
]


# ---------- Операции над коллекцией ----------
def create_account(number, owner, account_type, balance):
    """Создаёт словарь-счёт."""
    return {"number": number, "owner": owner, "type": account_type, "balance": balance}


def number_exists(accounts, number):
    """Проверяет, есть ли уже счёт с таким номером (set из номеров)."""
    numbers = {account["number"] for account in accounts}
    return number in numbers


def add_account(accounts, number, owner, account_type, balance):
    """Добавляет счёт. Возвращает True, если добавлен, и False, если номер занят."""
    if number_exists(accounts, number):
        return False
    accounts.append(create_account(number, owner, account_type, balance))
    return True


def remove_account(accounts, number):
    """Удаляет счёт по номеру. Возвращает True, если счёт был найден."""
    for index, account in enumerate(accounts):
        if account["number"] == number:
            accounts.pop(index)
            return True
    return False


def find_by_owner(accounts, owner):
    """Поиск счетов владельца (по части фамилии/имени, без учёта регистра)."""
    return [
        account
        for account in accounts
        if owner.lower() in account["owner"].lower()
    ]


def filter_by_type(accounts, account_type):
    """Фильтрация счетов по типу."""
    return [account for account in accounts if account["type"] == account_type]


def calculate_total_balance(accounts):
    """Общий баланс всех счетов (через цикл)."""
    total = 0
    for account in accounts:
        total += account["balance"]
    return total


def find_max_balance(accounts):
    """Счета с максимальным балансом (их может быть несколько)."""
    maximum = max(account["balance"] for account in accounts)
    return [account for account in accounts if account["balance"] == maximum]


def find_min_balance(accounts):
    """Счета с минимальным балансом."""
    minimum = min(account["balance"] for account in accounts)
    return [account for account in accounts if account["balance"] == minimum]


def get_account_types(accounts):
    """Множество уникальных типов счетов."""
    return {account["type"] for account in accounts}


def sort_by_balance(accounts, descending=False):
    """Сортировка счетов по балансу (исходный список не меняется)."""
    return sorted(accounts, key=lambda account: account["balance"], reverse=descending)


def group_by_type(accounts):
    """Группировка: словарь {тип: [счета]}."""
    groups = {}
    for account in accounts:
        groups.setdefault(account["type"], []).append(account)
    return groups


# ---------- Ввод и вывод ----------
def read_nonempty(prompt):
    """Запрашивает непустую строку."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("Ошибка: строка не может быть пустой")


def read_account_number(accounts):
    """Номер счёта: 6-20 цифр, уникальный."""
    while True:
        number = input("Номер счёта (6-20 цифр): ").strip()
        if not number.isdigit() or not 6 <= len(number) <= 20:
            print("Ошибка: номер должен состоять из 6-20 цифр")
        elif number_exists(accounts, number):
            print("Ошибка: счёт с таким номером уже существует")
        else:
            return number


def read_account_type():
    """Тип счёта из допустимого набора."""
    while True:
        text = input(f"Тип счёта ({', '.join(ACCOUNT_TYPES)}): ").strip().lower()
        if text in ACCOUNT_TYPES:
            return text
        print("Ошибка: недопустимый тип счёта")


def read_balance():
    """Баланс - неотрицательное число."""
    while True:
        text = input("Баланс (руб.): ").strip().replace(",", ".")
        try:
            value = float(text)
        except ValueError:
            print("Ошибка: нужно ввести число")
            continue
        if value < 0:
            print("Ошибка: баланс не может быть отрицательным")
        else:
            return value


def print_accounts(accounts):
    """Выводит таблицу счетов."""
    if not accounts:
        print(" (нет подходящих счетов)")
        return
    print(f" {'Номер':<22}{'Владелец':<16}{'Тип':<16}{'Баланс':>14}")
    for account in accounts:
        print(
            f" {account['number']:<22}{account['owner']:<16}"
            f"{account['type']:<16}{account['balance']:>14,.2f}"
        )


# ---------- Пункты меню ----------
def menu_add(accounts):
    number = read_account_number(accounts)
    owner = read_nonempty("Владелец: ")
    account_type = read_account_type()
    balance = read_balance()
    add_account(accounts, number, owner, account_type, balance)
    print("Счёт добавлен")


def menu_search(accounts):
    owner = read_nonempty("Введите владельца (или часть имени): ")
    found = find_by_owner(accounts, owner)
    print(f"Найдено счетов: {len(found)}")
    print_accounts(found)


def menu_filter(accounts):
    account_type = read_account_type()
    found = filter_by_type(accounts, account_type)
    print(f"Счетов типа «{account_type}»: {len(found)}")
    print_accounts(found)


def menu_sort(accounts):
    choice = input("Порядок (1 - по возрастанию, 2 - по убыванию): ").strip()
    result = sort_by_balance(accounts, descending=(choice == "2"))
    print_accounts(result)


def menu_statistics(accounts):
    total = calculate_total_balance(accounts)
    print(f"Количество счетов: {len(accounts)}")
    print(f"Общий баланс: {total:,.2f} руб.")
    print(f"Средний баланс: {total / len(accounts):,.2f} руб.")
    print("Счёт с максимальным балансом:")
    print_accounts(find_max_balance(accounts))
    print("Счёт с минимальным балансом:")
    print_accounts(find_min_balance(accounts))


def menu_unique_types(accounts):
    types = get_account_types(accounts)
    print(f"Используемые типы счетов ({len(types)}): {', '.join(sorted(types))}")


def menu_remove(accounts):
    number = read_nonempty("Номер удаляемого счёта: ")
    if remove_account(accounts, number):
        print("Счёт удалён")
    else:
        print("Счёт с таким номером не найден")


def menu_group(accounts):
    for account_type, group in group_by_type(accounts).items():
        subtotal = calculate_total_balance(group)
        print(f"{account_type}: счетов {len(group)}, сумма {subtotal:,.2f} руб.")


def menu_load_demo(accounts):
    added = 0
    for number, owner, account_type, balance in DEMO_ACCOUNTS:
        if add_account(accounts, number, owner, account_type, balance):
            added += 1
    print(f"Загружено демонстрационных счетов: {added}")


def main():
    accounts = []
    # Пункты, которым нужен непустой список счетов
    needs_data = {"2", "3", "4", "5", "6", "7", "8", "9"}
    actions = {
        "1": menu_add, "2": lambda a: print_accounts(a), "3": menu_search,
        "4": menu_filter, "5": menu_sort, "6": menu_statistics,
        "7": menu_unique_types, "8": menu_remove, "9": menu_group,
        "10": menu_load_demo,
    }
    while True:
        print("\n===== БАНКОВСКИЕ СЧЕТА =====")
        print("1. Добавить счёт")
        print("2. Показать все счета")
        print("3. Найти счета владельца")
        print("4. Фильтрация по типу счёта")
        print("5. Сортировка по балансу")
        print("6. Статистика")
        print("7. Уникальные типы счетов")
        print("8. Удалить счёт")
        print("9. Группировка по типам")
        print("10. Загрузить демонстрационные данные")
        print("0. Выход")
        choice = input("Выберите пункт: ").strip()
        if choice == "0":
            print("Работа завершена")
            break
        if choice not in actions:
            print("Ошибка: нет такого пункта меню")
        elif choice in needs_data and not accounts:
            print("Список счетов пуст. Добавьте данные (пункт 1 или 10)")
        else:
            actions[choice](accounts)


if __name__ == "__main__":
    main()