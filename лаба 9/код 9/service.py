"""Сервисный слой: бизнес-логика работы с фильмами.

Сервис не знает о существовании сети и консоли — он работает только
с Repository и моделями.
"""
from exceptions import MovieNotFoundError, ValidationError
from models import Movie
from repository import MovieRepository


def _validate(data: dict, for_create: bool) -> None:
    """Базовая проверка полей фильма."""
    for field_name in ("title", "director", "genre", "year", "duration_min", "rating"):
        if field_name not in data:
            raise ValidationError(f"Отсутствует обязательное поле: {field_name}")
    if not data["title"].strip():
        raise ValidationError("Название фильма не может быть пустым")
    if not data["director"].strip():
        raise ValidationError("Имя режиссёра не может быть пустым")
    if not data["genre"].strip():
        raise ValidationError("Жанр не может быть пустым")
    if int(data["year"]) < 1888 or int(data["year"]) > 2100:
        raise ValidationError("Некорректный год выпуска")
    if int(data["duration_min"]) <= 0:
        raise ValidationError("Продолжительность должна быть положительной")
    if not 0 <= float(data["rating"]) <= 10:
        raise ValidationError("Рейтинг должен быть в диапазоне 0..10")


class MovieService:
    """Операции над фильмами, опирающиеся на репозиторий."""

    def __init__(self, repository: MovieRepository) -> None:
        self.repository = repository

    def list_movies(self) -> list[Movie]:
        return self.repository.get_all()

    def get_movie(self, movie_id: int) -> Movie:
        movie = self.repository.get(movie_id)
        if movie is None:
            raise MovieNotFoundError(f"Фильм с номером {movie_id} не найден")
        return movie

    def create_movie(self, data: dict) -> Movie:
        _validate(data, for_create=True)
        movie = Movie.from_dict({**data, "id": 0})
        return self.repository.add(movie)

    def update_movie(self, movie_id: int, data: dict) -> Movie:
        self.get_movie(movie_id)  # проверка существования
        _validate(data, for_create=False)
        movie = Movie.from_dict({**data, "id": movie_id})
        return self.repository.update(movie)

    def delete_movie(self, movie_id: int) -> bool:
        self.get_movie(movie_id)
        return self.repository.delete(movie_id)

    def find_by_genre(self, genre: str) -> list[Movie]:
        return self.repository.find_by_genre(genre)