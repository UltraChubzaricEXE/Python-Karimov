"""Репозиторий фильмов: хранение объектов в памяти.

Минимальный набор операций: add, get, get_all, update, delete.
"""
from models import Movie


class MovieRepository:
    """Хранилище фильмов (в памяти процесса)."""

    def __init__(self) -> None:
        self._items: dict[int, Movie] = {}
        self._next_id: int = 1

    def _issue_id(self) -> int:
        new_id = self._next_id
        self._next_id += 1
        return new_id

    def add(self, movie: Movie) -> Movie:
        """Добавляет фильм, присваивает ему идентификатор."""
        movie.id = self._issue_id()
        self._items[movie.id] = movie
        return movie

    def get(self, movie_id: int) -> Movie | None:
        """Возвращает фильм по идентификатору или None."""
        return self._items.get(movie_id)

    def get_all(self) -> list[Movie]:
        """Возвращает список всех фильмов."""
        return list(self._items.values())

    def update(self, movie: Movie) -> Movie:
        """Заменяет фильм с тем же идентификатором."""
        if movie.id not in self._items:
            raise KeyError(f"Фильм с id {movie.id} не найден")
        self._items[movie.id] = movie
        return movie

    def delete(self, movie_id: int) -> bool:
        """Удаляет фильм. Возвращает True, если фильм был удалён."""
        if movie_id in self._items:
            del self._items[movie_id]
            return True
        return False

    def find_by_genre(self, genre: str) -> list[Movie]:
        """Специализированная операция: поиск фильмов по жанру."""
        genre_lower = genre.lower()
        return [m for m in self._items.values() if m.genre.lower() == genre_lower]