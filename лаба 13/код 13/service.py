"""Сервисный слой фитнес-центра на MongoDB + Redis (ЛР13, вариант 8)."""
from mongodb_repo import MongoRepository
from redis_cache import RedisCache


class FitnessService:
    """Бизнес-логика с кэшированием через Redis."""

    STATUSES = ("активен", "истёк", "заморожен", "отменён")

    def __init__(self, repo: MongoRepository, cache: RedisCache) -> None:
        self.repo = repo
        self.cache = cache

    def _validate(self, doc: dict) -> None:
        if not isinstance(doc.get("full_name"), str) or not doc["full_name"].strip():
            raise ValueError("Имя клиента обязательно")
        if not isinstance(doc.get("age"), (int, float)) or not 1 <= doc["age"] <= 129:
            raise ValueError("Некорректный возраст")
        if doc.get("status") not in self.STATUSES:
            raise ValueError(f"Недопустимый статус: {doc.get('status')}")

    def create_client(self, doc: dict) -> str:
        self._validate(doc)
        return self.repo.insert(doc)

    def get_client_cached(self, doc_id: str, ttl: int = 60):
        """Получение клиента через Cache-Aside (Redis)."""
        key = f"client:{doc_id}"
        def _serializable():
            doc = self.repo.find_by_id(doc_id)
            if doc is not None and "_id" in doc:
                doc["_id"] = str(doc["_id"])  # ObjectId не JSON-сериализуем
            return doc
        return self.cache.get_cached(key, _serializable, ttl=ttl)

    def update_client(self, doc_id: str, fields: dict) -> bool:
        ok = self.repo.update(doc_id, fields)
        if ok:
            self.cache.delete(f"client:{doc_id}")  # инвалидация кэша
        return ok

    def delete_client(self, doc_id: str) -> bool:
        ok = self.repo.delete(doc_id)
        if ok:
            self.cache.delete(f"client:{doc_id}")
        return ok

    def list_clients(self) -> list:
        return self.repo.find_all()

    def active_clients(self) -> list:
        return self.repo.find_by_status("активен")

    def by_trainer(self, trainer: str) -> list:
        return self.repo.find_by_trainer(trainer)

    def by_goal(self, goal: str) -> list:
        return self.repo.find_by_goal(goal)

    def in_city(self, city: str) -> list:
        return self.repo.find_in_city(city)

    def active_after(self, date_str: str) -> list:
        return self.repo.find_active_after_date(date_str)

    def stats(self) -> dict:
        return {
            "by_status": self.repo.aggregate_by_status(),
            "avg_age": round(self.repo.aggregate_avg_age(), 2),
            "total": len(self.list_clients()),
        }

    # --- Redis-специфичные операции ---
    def record_visit(self, client_id: str, date: str) -> None:
        self.cache.push_visit(client_id, date)

    def set_workout(self, client_id: str, workout: dict) -> None:
        self.cache.set_current_workout(client_id, workout)