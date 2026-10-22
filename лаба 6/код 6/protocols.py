"""Протоколы (структурная типизация) (ЛР6, вариант 8)."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class Reportable(Protocol):
    def get_report_data(self) -> str:
        ...


def print_report(item: Reportable) -> None:
    """Принимает любой объект, у которого есть get_report_data()."""
    print(item.get_report_data())