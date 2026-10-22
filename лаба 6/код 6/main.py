"""Лабораторная работа №6. Вариант 8. Фитнес-центр. Точка входа."""

from console import run
from services import FitnessService


def main() -> None:
    service = FitnessService()
    run(service)


if __name__ == "__main__":
    main()