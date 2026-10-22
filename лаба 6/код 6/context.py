"""Контекстные менеджеры (ЛР6, вариант 8)."""

import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import Any, Iterator

LOG_PATH = Path(__file__).parent / "operations.log"


class OperationLogger:
    """Записывает в файл дату, операцию, параметры, длительность и результат."""

    def __init__(self, operation: str, params: str = "", path: Path = LOG_PATH) -> None:
        self.operation = operation
        self.params = params
        self.path = path
        self._start = 0.0

    def __enter__(self) -> "OperationLogger":
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None, tb: TracebackType | None) -> bool:
        duration = time.perf_counter() - self._start
        lines = [f"[{datetime.now():%Y-%m-%d %H:%M:%S}]",
                 f"Operation: {self.operation}",
                 f"Params: {self.params or '-'}",
                 f"Duration: {duration:.4f} sec"]
        if exc_type is None:
            lines.append("Result: SUCCESS")
        else:
            lines.append("Result: ERROR")
            lines.append(f"Exception: {exc_type.__name__}: {exc}")
        with open(self.path, "a", encoding="utf-8") as file:
            file.write("\n".join(lines) + "\n\n")
        return False  # исключение не подавляется


@contextmanager
def transaction(storage: dict[int, Any]) -> Iterator[dict[int, Any]]:
    """Транзакционный режим: при ошибке содержимое хранилища восстанавливается."""
    backup = dict(storage)
    try:
        yield storage
    except Exception:
        storage.clear()
        storage.update(backup)
        print("[TRANSACTION] ошибка - изменения отменены")
        raise
    else:
        print("[TRANSACTION] изменения подтверждены")