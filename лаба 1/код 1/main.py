"""Лабораторная работа №1. Вариант 8.

Анализ продолжительности тренировок спортсмена.
"""
import random

LONG_WORKOUT_MINUTES = 60  # тренировка "более часа"
SHORT_WORKOUT_MINUTES = 30  # тренировка "менее 30 минут"
MAX_WORKOUT_MINUTES = 600  # разумный предел для одной тренировки
MAX_WORKOUTS = 365  # не больше года наблюдений


def read_positive_int(prompt, maximum):
    """Запрашивает целое число от 1 до maximum, пока ввод не станет корректным."""
    while True:
        text = input(prompt).strip()
        if text.startswith("-") and text[1:].isdigit():
            print("Ошибка: значение не может быть отрицательным")
        elif not text.isdigit():
            print("Ошибка: нужно ввести целое число")
        elif int(text) == 0:
            print("Ошибка: значение должно быть больше нуля")
        elif int(text) > maximum:
            print(f"Ошибка: значение не может быть больше {maximum}")
        else:
            return int(text)


def read_workouts():
    """Ручной ввод продолжительности каждой тренировки (в минутах)."""
    count = read_positive_int("Введите количество тренировок: ", MAX_WORKOUTS)
    workouts = []
    for i in range(count):
        minutes = read_positive_int(
            f"Продолжительность тренировки {i + 1} (мин): ", MAX_WORKOUT_MINUTES
        )
        workouts.append(minutes)
    return workouts


def generate_workouts():
    """Случайная генерация набора тренировок."""
    count = read_positive_int("Сколько тренировок сгенерировать: ", MAX_WORKOUTS)
    workouts = [random.randint(15, 150) for _ in range(count)]
    print("Сгенерированы значения (мин):", *workouts)
    return workouts


def calculate_total(workouts):
    """Суммарная продолжительность тренировок."""
    total = 0
    for minutes in workouts:
        total += minutes
    return total


def calculate_average(workouts):
    """Средняя продолжительность тренировки."""
    return calculate_total(workouts) / len(workouts)


def find_longest(workouts):
    """Возвращает (продолжительность, номер) самой длинной тренировки."""
    longest = workouts[0]
    number = 1
    for i, minutes in enumerate(workouts, start=1):
        if minutes > longest:
            longest = minutes
            number = i
    return longest, number


def count_longer_than(workouts, limit):
    """Количество тренировок продолжительностью строго больше limit минут."""
    count = 0
    for minutes in workouts:
        if minutes > limit:
            count += 1
    return count


def percent_shorter_than(workouts, limit):
    """Процент тренировок продолжительностью строго меньше limit минут."""
    count = 0
    for minutes in workouts:
        if minutes < limit:
            count += 1
    return count / len(workouts) * 100


def format_duration(minutes):
    """Переводит минуты в вид '2 ч 05 мин'."""
    hours = int(minutes // 60)
    rest = round(minutes % 60)
    return f"{hours} ч {rest:02d} мин"


def describe_load(average):
    """Текстовая характеристика нагрузки по средней продолжительности."""
    if average >= 90:
        return "высокая нагрузка"
    elif average >= 45:
        return "умеренная нагрузка"
    else:
        return "лёгкая нагрузка"


def show_statistics(workouts):
    """Выводит все показатели по набору тренировок."""
    total = calculate_total(workouts)
    average = calculate_average(workouts)
    longest, number = find_longest(workouts)
    long_count = count_longer_than(workouts, LONG_WORKOUT_MINUTES)
    short_percent = percent_shorter_than(workouts, SHORT_WORKOUT_MINUTES)

    print("\n----- Результаты анализа -----")
    print(f"Количество тренировок: {len(workouts)}")
    print(f"Суммарная продолжительность: {total} мин ({format_duration(total)})")
    print(f"Средняя продолжительность: {average:.2f} мин")
    print(f"Самая длинная тренировка: №{number} ({longest} мин)")
    print(f"Тренировок дольше часа: {long_count}")
    print(f"Тренировок короче 30 минут: {short_percent:.1f}%")
    print(f"Характеристика: {describe_load(average)}")


def main():
    workouts = []
    while True:
        print("\n===== Анализ тренировок =====")
        print("1. Ввести данные вручную")
        print("2. Сгенерировать данные случайно")
        print("3. Показать статистику")
        print("4. Выход")
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            workouts = read_workouts()
        elif choice == "2":
            workouts = generate_workouts()
        elif choice == "3":
            if len(workouts) == 0:
                print("Сначала введите данные (пункт 1 или 2)")
            else:
                show_statistics(workouts)
        elif choice == "4":
            print("Работа завершена")
            break
        else:
            print("Ошибка: выберите пункт от 1 до 4")


if __name__ == "__main__":
    main()