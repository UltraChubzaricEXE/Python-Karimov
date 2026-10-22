"""Пользовательские исключения приложения «Кинотеатр»."""


class CinemaError(Exception):
    """Базовое исключение приложения."""


class MovieNotFoundError(CinemaError):
    """Фильм с указанным номером не найден."""


class ValidationError(CinemaError):
    """Некорректные данные запроса."""


class ProtocolError(CinemaError):
    """Ошибка протокола обмена (формат сообщения)."""