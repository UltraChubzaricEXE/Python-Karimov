"""Интроспекция объектов (ЛР6, вариант 8)."""

import inspect
from enum import Enum
from typing import Any

from models import Entity


def inspect_object(obj: Any) -> None:
    print("=== ИНФОРМАЦИЯ ОБ ОБЪЕКТЕ ===")
    print(f"Тип: {type(obj).__name__}")
    print(f"Наследник Entity: {isinstance(obj, Entity)}")
    print(f"Класс - подкласс Entity: {issubclass(type(obj), Entity)}")
    print(f"Есть метод get_report_data: {hasattr(obj, 'get_report_data')}")

    fields = {n: getattr(obj, n) for n in dir(obj)
              if not n.startswith("_") and not callable(getattr(obj, n))}
    print("Атрибуты:")
    for name, value in fields.items():
        shown = value.value if isinstance(value, Enum) else value
        print(f" {name} = {shown!r}")

    methods = [(n, m) for n, m in inspect.getmembers(obj, inspect.ismethod)
               if not n.startswith("_")]
    print("Методы:")
    if not methods:
        print(" (нет)")
    for name, method in methods:
        print(f" {name}{inspect.signature(method)}")