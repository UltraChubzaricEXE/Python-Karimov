"""Лабораторная работа №5. Вариант 8. Заказы: функциональные возможности Python."""

import sys

from generators import OrderIterator, expensive_numbers, orders_of_customer
from models import (STATUS_CANCELLED, STATUS_DONE, DeliveryOrder, Order,
                    PickupOrder)
from operations import (all_costs_positive, calculate_total, filter_objects,
                        has_cancelled, make_cost_filter, sort_objects,
                        transform_objects)


def title(text):
    print(f"\n=== {text} ===")


def main():
    orders = [
        DeliveryOrder(101, "Иванов", 3500, "ул. Ленина, 5"),
        PickupOrder(102, "Петров", 1200, "ПВЗ №3"),
        DeliveryOrder(103, "Иванов", 8900, "пр. Мира, 12", STATUS_DONE),
        PickupOrder(104, "Сидорова", 450, "ПВЗ №1", STATUS_CANCELLED),
        DeliveryOrder(105, "Петров", 15200, "ул. Гагарина, 8"),
        PickupOrder(106, "Иванов", 2300, "ПВЗ №2"),
    ]

    title("1. Исходные данные (полиморфный вызов describe)")
    for order in orders:
        print(order.describe())

    title("2. filter(): активные заказы")
    active = list(filter_objects(orders, lambda order: order.is_active))
    print([order.number for order in active])

    title("3. map(): номера заказов")
    numbers = list(transform_objects(orders, lambda order: order.number))
    print("Через map: ", numbers)
    print("Через comprehension:", [order.number for order in orders])

    title("4. sorted(key=...): сортировка по стоимости")
    for order in sort_objects(orders, lambda order: order.cost, reverse=True):
        print(f"{order.cost:>9.2f} заказ №{order.number}")

    title("5. reduce(): общая стоимость")
    print(f"Все заказы: {calculate_total(orders):.2f} руб.")
    print(f"Только активные: {calculate_total(active):.2f} руб.")

    title("6. Функция высшего порядка, возвращающая функцию")
    big_order = make_cost_filter(3000)
    print("Заказы от 3000 руб.:",
          [order.number for order in filter_objects(orders, big_order)])

    title("7. any() / all()")
    print("Есть отменённые заказы:", has_cancelled(orders))
    print("Есть отменённые среди активных:", has_cancelled(active))
    print("У всех заказов стоимость > 0:", all_costs_positive(orders))

    title("8. Генератор: заказы клиента «Иванов»")
    for order in orders_of_customer(orders, "Иванов"):
        print(order.describe())
    print("Номера заказов дороже 3000 (генератор):", list(expensive_numbers(orders, 3000)))

    title("9. next() и завершение итерации")
    generator = orders_of_customer(orders, "Петров")
    print("Первый:", next(generator).number)
    print("Второй:", next(generator).number)
    try:
        next(generator)
    except StopIteration:
        print("Больше заказов нет: возникло StopIteration")

    title("10. Собственный итератор OrderIterator")
    iterator = OrderIterator(orders)
    for order in iterator:
        print(order.number, end=" ")
    print()
    try:
        next(iterator)
    except StopIteration:
        print("Итератор исчерпан: StopIteration")

    title("11. Ленивые вычисления: список и генератор")
    squares_list = [x * x for x in range(1_000_000)]
    squares_gen = (x * x for x in range(1_000_000))
    print("Размер списка в памяти: ", sys.getsizeof(squares_list), "байт")
    print("Размер генератора в памяти: ", sys.getsizeof(squares_gen), "байт")
    print("Первые 3 значения генератора:", next(squares_gen), next(squares_gen), next(squares_gen))

    title("12. Конвейер: filter -> map -> sorted")
    pipeline = sort_objects(
        transform_objects(
            filter_objects(orders, lambda o: o.is_active and o.cost > 1000),
            lambda o: (o.number, o.cost * 0.9),  # скидка 10 %
        ),
        lambda pair: pair[1],
    )
    for number, price in pipeline:
        print(f"Заказ №{number}: {price:.2f} руб. со скидкой 10%")

    title("13. Обработка некорректных данных")
    bad_data = [(401, "Орлов", -100), (402, "Орлов", 500, "неизвестный")]
    for data in bad_data:
        try:
            if len(data) == 3:
                Order(*data)
            else:
                Order(data[0], data[1], data[2], data[3])
        except ValueError as error:
            print(f"Заказ №{data[0]} не создан: {error}")


if __name__ == "__main__":
    main()