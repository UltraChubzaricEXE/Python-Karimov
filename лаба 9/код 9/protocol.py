"""Протокол клиент-серверного обмена: newline-delimited JSON.

Каждый запрос — JSON {command, data}, заканчивающийся символом \n.
Каждый ответ — JSON {status, data} либо {status, error}.
"""
import json

from exceptions import ProtocolError


def encode_message(payload: dict) -> bytes:
    """Сериализует dict в байты JSON + символ конца строки."""
    try:
        text = json.dumps(payload, ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise ProtocolError(f"Невозможно сериализовать сообщение: {exc}") from exc
    return (text + "\n").encode("utf-8")


def decode_messages(buffer: str) -> list[dict]:
    """Разбирает накопленную строку на список JSON-сообщений (по \n).

    Возвращает пару (полные_сообщения, остаток_буфера).
    """
    messages: list[dict] = []
    lines = buffer.split("\n")
    complete, rest = lines[:-1], lines[-1]
    for line in complete:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ProtocolError(f"Некорректный JSON: {exc}") from exc
        if not isinstance(obj, dict):
            raise ProtocolError("Сообщение должно быть JSON-объектом")
        messages.append(obj)
    return messages, rest


def make_response(status: str, data=None, error=None) -> dict:
    """Формирует стандартизированный ответ."""
    if status == "error":
        return {"status": "error", "error": error or "Неизвестная ошибка"}
    return {"status": "ok", "data": data if data is not None else {}}