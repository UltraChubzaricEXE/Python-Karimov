"""Лабораторная работа №3. Вариант 8. Ресторан.

Объектная модель: MenuItem -> Dish / Drink (-> Dessert), Order (композиция).
"""

from abc import ABC, abstractmethod


class MenuItem(ABC):
    """Базовый (абстрактный) класс позиции меню."""

    created_count = 0  # атрибут класса: сколько позиций создано

    def __init__(self, name, price):
        self.name = name
        self.price = price  # проходит через setter с проверкой
        MenuItem.created_count += 1

    # --- инкапсуляция: цена защищена атрибутом _price и property ---
    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value <= 0:
            raise ValueError("Цена должна быть положительной")
        self._price = value

    @abstractmethod
    def final_cost(self):
        """Итоговая стоимость с учётом особенностей типа позиции."""

    def get_info(self):
        return f"{self.name}: цена {self.price:.2f} руб., итого {self.final_cost():.2f} руб."

    def change_price(self, percent):
        """Изменяет цену на заданный процент (может быть отрицательным)."""
        self.price = self.price * (1 + percent / 100)

    def __lt__(self, other):  # позволяет сортировать позиции по итоговой стоимости
        return self.final_cost() < other.final_cost()

    def __str__(self):
        return self.get_info()


class Dish(MenuItem):
    """Блюдо: к цене добавляется 10 % за обслуживание."""

    SERVICE_FEE = 0.10

    def __init__(self, name, price, calories):
        super().__init__(name, price)
        if calories < 0:
            raise ValueError("Калорийность не может быть отрицательной")
        self.calories = calories

    def final_cost(self):
        return self.price * (1 + self.SERVICE_FEE)

    def get_info(self):
        return super().get_info() + f" [{self.calories} ккал]"


class Dessert(Dish):
    """Десерт - особое блюдо: добавляется фиксированная плата за сервировку."""

    SERVING_FEE = 20

    def __init__(self, name, price, calories, sugar_grams):
        super().__init__(name, price, calories)
        self.sugar_grams = sugar_grams

    def final_cost(self):
        return super().final_cost() + self.SERVING_FEE

    def get_info(self):
        return super().get_info() + f" [сахар {self.sugar_grams} г]"


class Drink(MenuItem):
    """Напиток: цена задана за порцию 250 мл, стоимость зависит от объёма."""

    STANDARD_VOLUME = 250

    def __init__(self, name, price, volume_ml):
        super().__init__(name, price)
        if volume_ml <= 0:
            raise ValueError("Объём должен быть положительным")
        self.volume_ml = volume_ml

    def final_cost(self):
        return self.price * self.volume_ml / self.STANDARD_VOLUME

    def get_info(self):
        return super().get_info() + f" [{self.volume_ml} мл]"


class Order:
    """Заказ. Композиция: заказ содержит позиции меню (отношение HAS-A)."""

    def __init__(self, table_number):
        self.table_number = table_number
        self._lines = []  # список пар [позиция меню, количество]
        self._is_open = True

    @property
    def is_open(self):
        return self._is_open

    def add_item(self, item, quantity=1):
        if not self._is_open:
            raise RuntimeError("Заказ закрыт, добавлять позиции нельзя")
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        self._lines.append([item, quantity])

    def remove_item(self, name):
        """Удаляет все строки с позицией по названию. Возвращает число удалённых."""
        before = len(self._lines)
        self._lines = [line for line in self._lines if line[0].name != name]
        return before - len(self._lines)

    def total_cost(self):
        return sum(item.final_cost() * quantity for item, quantity in self._lines)

    def items_count(self):
        return sum(quantity for _, quantity in self._lines)

    def close(self):
        self._is_open = False

    def receipt(self):
        status = "открыт" if self._is_open else "закрыт"
        lines = [f"Заказ стола №{self.table_number} ({status})"]
        for item, quantity in self._lines:
            cost = item.final_cost() * quantity
            lines.append(f" {item.name:<22} x{quantity} {cost:>9.2f} руб.")
        lines.append(f" ИТОГО: {self.total_cost():.2f} руб.")
        return "\n".join(lines)


def title(text):
    print(f"\n=== {text} ===")


def main():
    # Тест 1. Создание объектов каждого типа
    title("Тест 1. Создание объектов")
    soup = Dish("Борщ", 250, 320)
    steak = Dish("Стейк", 890, 650)
    cake = Dessert("Медовик", 180, 410, 38)
    tea = Drink("Чай чёрный", 120, 250)
    juice = Drink("Сок яблочный", 150, 500)
    print("Создано позиций меню:", MenuItem.created_count)
    print("Типы:", type(soup).__name__, type(cake).__name__, type(tea).__name__)

    # Тест 2. Общие методы
    title("Тест 2. Общие методы (get_info, final_cost)")
    print(soup.get_info())
    print(f"Итоговая стоимость напитка: {tea.final_cost():.2f} руб.")

    # Тест 3. Переопределённые методы
    title("Тест 3. Переопределённый final_cost")
    print(f"Dish (цена 250): {soup.final_cost():.2f} -> цена + 10% обслуживание")
    print(f"Dessert (цена 180): {cake.final_cost():.2f} -> цена + 10% + 20 руб. сервировка")
    print(f"Drink (150, 500мл): {juice.final_cost():.2f} -> цена * объём / 250")

    # Тест 4. Изменение состояния объекта
    title("Тест 4. Изменение состояния")
    print(f"Цена стейка до: {steak.price:.2f}")
    steak.change_price(10)
    print(f"Цена стейка после повышения на 10%: {steak.price:.2f}")
    steak.price = 900
    print(f"Цена стейка после ручной установки: {steak.price:.2f}")

    # Тест 5. Некорректное значение свойства
    title("Тест 5. Некорректные значения")
    for action, attempt in [
        ("price = -50", lambda: setattr(steak, "price", -50)),
        ("Dish(..., calories=-1)", lambda: Dish("Салат", 200, -1)),
        ("Drink(..., volume=0)", lambda: Drink("Вода", 50, 0)),
    ]:
        try:
            attempt()
        except ValueError as error:
            print(f"{action}: ValueError - {error}")
    print("Цена стейка осталась:", steak.price)

    # Тест 6. Полиморфная коллекция
    title("Тест 6. Полиморфная коллекция")
    menu = [soup, steak, cake, tea, juice]
    for item in menu:
        print("-", item.get_info())
    print("\nСортировка по итоговой стоимости (перегруженный __lt__):")
    for item in sorted(menu):
        print(f" {item.final_cost():>8.2f} {item.name}")

    # Тест 7. Композиция: заказ содержит позиции меню
    title("Тест 7. Композиция (Order содержит MenuItem)")
    order = Order(table_number=5)
    order.add_item(soup, 2)
    order.add_item(steak)
    order.add_item(cake, 2)
    order.add_item(tea, 2)
    print(order.receipt())
    print("Всего порций:", order.items_count())
    print("Удалено строк «Чай чёрный»:", order.remove_item("Чай чёрный"))
    order.close()
    print(f"Заказ закрыт, сумма к оплате: {order.total_cost():.2f} руб.")
    try:
        order.add_item(juice)
    except RuntimeError as error:
        print("Попытка добавить в закрытый заказ: RuntimeError -", error)


if __name__ == "__main__":
    main()