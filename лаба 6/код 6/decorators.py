"""Собственные декораторы (ЛР6, вариант 8)."""

import itertools
import time
from functools import wraps
from typing import Any, Callable

from models import MembershipStatus

COMMAND_ATTRIBUTE = "_command_info"
_order = itertools.count(1)


def log_call(func: Callable) -> Callable:
    """Декоратор №1: журналирование вызова (параметры и результат)."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        shown = [repr(a) for a in args[1:]] + [f"{k}={v!r}" for k, v in kwargs.items()]
        print(f"[LOG] вызван {func.__name__}({', '.join(shown)})")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} вернул: {result!r}")
        return result

    return wrapper


def timed(func: Callable) -> Callable:
    """Декоратор №2: измерение времени выполнения."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print(f"[PERFORMANCE] {func.__name__}: {time.perf_counter() - start:.4f} sec")

    return wrapper


def require_status(*allowed: MembershipStatus) -> Callable:
    """Декоратор №3 (с параметрами): метод выполняется, только если абонемент
    (первый аргумент после self - его номер) имеет один из допустимых статусов."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self: Any, membership_id: int, *args: Any, **kwargs: Any) -> Any:
            membership = self.get_membership(membership_id)
            if membership.status not in allowed:
                names = ", ".join(s.value for s in allowed)
                raise PermissionError(
                    f"Операция доступна только для абонементов со статусом: {names} "
                    f"(текущий: {membership.status.value})")
            return func(self, membership_id, *args, **kwargs)

        return wrapper

    return decorator


def repeat(times: int) -> Callable:
    """Декоратор с параметром: повторяет вызов функции times раз."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


def command(name: str, title: str) -> Callable:
    """Регистрирует метод как команду меню (автоматическая регистрация операций)."""

    def decorator(func: Callable) -> Callable:
        setattr(func, COMMAND_ATTRIBUTE, (name, title, next(_order)))
        return func

    return decorator