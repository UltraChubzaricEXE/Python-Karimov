"""Модели предметной области: кинотеатр.

Вариант 8. Основная сущность — фильм (Movie).
"""
from dataclasses import dataclass, field


@dataclass
class Movie:
    """Фильм: идентификатор и минимум четыре дополнительных поля."""
    id: int
    title: str
    director: str
    genre: str
    year: int
    duration_min: int
    rating: float

    def to_dict(self) -> dict:
        """Преобразование объекта в словарь для JSON."""
        return {
            "id": self.id,
            "title": self.title,
            "director": self.director,
            "genre": self.genre,
            "year": self.year,
            "duration_min": self.duration_min,
            "rating": self.rating,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Movie":
        """Восстановление объекта из словаря."""
        return cls(
            id=data["id"],
            title=data["title"],
            director=data["director"],
            genre=data["genre"],
            year=data["year"],
            duration_min=data["duration_min"],
            rating=data["rating"],
        )

    def __str__(self) -> str:
        return (f"#{self.id} {self.title} ({self.year}) — {self.director}, "
                f"{self.genre}, {self.duration_min} мин, рейтинг {self.rating}")