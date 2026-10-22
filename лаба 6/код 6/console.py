"""Консольный интерфейс: меню формируется автоматически из команд с @command (ЛР6)."""

import inspect
from typing import Any, Callable

from context import OperationLogger
from decorators import COMMAND_ATTRIBUTE
from models import EntityNotFoundError, InvalidStatusChangeError


def discover_commands(service: object) -> list[tuple[str, str, Callable]]:
    """Находит методы, помеченные @command, с помощью inspect.getmembers."""
    found = []
    for _, method in inspect.getmembers(service, inspect.ismethod):
        if hasattr(method, COMMAND_ATTRIBUTE):
            name, title, order = getattr(method, COMMAND_ATTRIBUTE)
            found.append((order, name, title, method))
    found.sort(key=lambda item: item[0])
    return [(name, title, method) for _, name, title, method in found]


def ask(param: inspect.Parameter) -> Any:
    """Запрашивает значение параметра и преобразует его по аннотации типа."""
    has_default = param.default is not inspect.Parameter.empty
    suffix = f" [{param.default}]" if has_default else ""
    while True:
        raw = input(f" {param.name}{suffix}: ").strip()
        if raw == "" and has_default:
            return param.default
        if raw == "":
            print(" Ошибка: значение не может быть пустым")
            continue
        # для Enum-аннотаций предлагаем выбирать вариант
        annotation = param.annotation
        if isinstance(annotation, type) and hasattr(annotation, "__members__"):
            names = list(annotation.__members__)
            print(f"  варианты: {', '.join(names)}")
            raw = input("  выберите вариант: ").strip().upper()
            try:
                return annotation[raw]
            except KeyError:
                print(" Ошибка: нет такого варианта")
                continue
        try:
            return annotation(raw)
        except ValueError:
            print(f" Ошибка: ожидается значение типа {getattr(annotation, '__name__', annotation)}")


def run(service: object) -> None:
    commands = discover_commands(service)
    while True:
        print("\n===== ФИТНЕС-ЦЕНТР =====")
        for number, (_, title, _) in enumerate(commands, start=1):
            print(f"{number}. {title}")
        print("0. Выход")
        choice = input("Выберите пункт: ").strip()
        if choice == "0":
            print("Работа завершена")
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(commands):
            print("Ошибка: нет такого пункта меню")
            continue
        name, _, method = commands[int(choice) - 1]
        signature = inspect.signature(method)
        arguments = [ask(param) for param in signature.parameters.values()]
        try:
            with OperationLogger(name, ", ".join(map(repr, arguments))):
                result = method(*arguments)
                if result:
                    print(result)
        except (EntityNotFoundError, InvalidStatusChangeError,
                PermissionError, ValueError) as error:
            print(f"Ошибка: {error}")