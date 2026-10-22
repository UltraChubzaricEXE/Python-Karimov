"""Лабораторная работа №4. Вариант 8. Система управления заказами."""

from pathlib import Path

from exceptions import OrderError, OrderNotFoundError
from models import Item, STATUSES
from services import OrderService
from storage import JsonRepository, export_csv

DATA_DIR = Path(__file__).parent / "data"
JSON_PATH = DATA_DIR / "orders.json"
CSV_PATH = DATA_DIR / "orders.csv"


def read_int(prompt):
    """Целое положительное число; при ошибке запрос повторяется."""
    while True:
        text = input(prompt).strip()
        try:
            value = int(text)
        except ValueError:
            print("Ошибка: необходимо ввести целое число")
            continue
        if value <= 0:
            print("Ошибка: число должно быть больше нуля")
        else:
            return value


def read_price(prompt):
    while True:
        text = input(prompt).strip().replace(",", ".")
        try:
            value = float(text)
        except ValueError:
            print("Ошибка: необходимо ввести число")
            continue
        if value <= 0:
            print("Ошибка: цена должна быть больше нуля")
        else:
            return value


def read_nonempty(prompt):
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("Ошибка: строка не может быть пустой")


def create_order(service):
    customer = read_nonempty("Клиент: ")
    items = []
    while True:
        name = read_nonempty(" Название товара: ")
        price = read_price(" Цена: ")
        quantity = read_int(" Количество: ")
        items.append(Item(name, price, quantity))
        if input(" Добавить ещё товар? (д/н): ").strip().lower() != "д":
            break
    order = service.create_order(customer, items)
    print(f"Создан заказ №{order.order_id}, стоимость {order.total_cost():.2f} руб.")


def show_orders(orders):
    if not orders:
        print("Заказов нет")
    for order in orders:
        print(order)


def change_status(service):
    order_id = read_int("Номер заказа: ")
    print("Статусы:", ", ".join(STATUSES))
    new_status = read_nonempty("Новый статус: ").lower()
    order = service.change_status(order_id, new_status)
    print(f"Статус заказа №{order.order_id} изменён: {order.status}")


def print_menu():
    print("\n===== УПРАВЛЕНИЕ ЗАКАЗАМИ =====")
    print("1. Создать заказ")
    print("2. Показать все заказы")
    print("3. Найти заказ по номеру")
    print("4. Найти заказы клиента")
    print("5. Изменить статус заказа")
    print("6. Отменить заказ")
    print("7. Рассчитать стоимость заказа")
    print("8. Сохранить в JSON")
    print("9. Экспортировать в CSV")
    print("10. Загрузить из JSON")
    print("0. Выход")


def main():
    repository = JsonRepository(JSON_PATH)
    try:
        service = OrderService(repository.load())
        print(f"Загружено заказов: {len(service.orders)}")
    except OrderError as error:
        print(f"Ошибка загрузки: {error}. Начинаем с пустого списка.")
        service = OrderService()

    while True:
        print_menu()
        choice = input("Выберите пункт: ").strip()
        try:
            if choice == "1":
                create_order(service)
            elif choice == "2":
                show_orders(service.orders)
            elif choice == "3":
                print(service.find_order(read_int("Номер заказа: ")))
            elif choice == "4":
                show_orders(service.find_by_customer(read_nonempty("Клиент: ")))
            elif choice == "5":
                change_status(service)
            elif choice == "6":
                order = service.cancel_order(read_int("Номер заказа: "))
                print(f"Заказ №{order.order_id} отменён")
            elif choice == "7":
                cost = service.calculate_cost(read_int("Номер заказа: "))
                print(f"Стоимость заказа: {cost:.2f} руб.")
            elif choice == "8":
                repository.save(service.orders)
                print(f"Данные сохранены: {JSON_PATH.name}")
            elif choice == "9":
                export_csv(service.orders, CSV_PATH)
                print(f"Данные экспортированы: {CSV_PATH.name}")
            elif choice == "10":
                service = OrderService(repository.load())
                print(f"Загружено заказов: {len(service.orders)}")
            elif choice == "0":
                repository.save(service.orders)
                print("Данные сохранены. Работа завершена")
                break
            else:
                print("Ошибка: нет такого пункта меню")
        except OrderNotFoundError as error:
            print(f"Ошибка: {error}")
        except OrderError as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()