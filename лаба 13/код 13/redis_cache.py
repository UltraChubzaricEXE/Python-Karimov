"""Redis-кэш фитнес-центра (ЛР13, вариант 8).

Используется минимум 3 типа данных Redis: String, Hash, List, Sorted Set.
Реализован Cache-Aside с TTL и инвалидацией кэша.
"""
import json


class RedisCache:
    """Кэширование часто запрашиваемых данных о клиентах."""

    TTL_DEFAULT = 60

    def __init__(self, client) -> None:
        self.client = client

    # --- String: кэш объекта (Cache-Aside) ---
    def set_json(self, key: str, value, ttl: int = TTL_DEFAULT) -> None:
        self.client.set(key, json.dumps(value, ensure_ascii=False), ex=ttl)

    def get_json(self, key: str):
        raw = self.client.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    def delete(self, key: str) -> None:
        self.client.delete(key)

    def ttl(self, key: str) -> int:
        return self.client.ttl(key)

    def get_cached(self, key: str, loader, ttl: int = 30):
        """Cache-Aside: кэш -> промах -> БД/сервис -> запись в кэш."""
        cached = self.get_json(key)
        if cached is not None:
            return cached, True
        data = loader()
        self.set_json(key, data, ttl=ttl)
        return data, False

    # --- Hash: текущая тренировка ---
    def set_current_workout(self, client_id, workout: dict, ttl: int = 600) -> None:
        key = f"workout:{client_id}"
        self.client.hset(key, mapping={
            "exercise": workout.get("exercise", ""),
            "duration": str(workout.get("duration", 0)),
        })
        self.client.expire(key, ttl)

    def get_current_workout(self, client_id) -> dict | None:
        data = self.client.hgetall(f"workout:{client_id}")
        if not data:
            return None
        return {"exercise": data.get("exercise", ""), "duration": int(data.get("duration", 0))}

    # --- List: последние посещения ---
    def push_visit(self, client_id, value: str, keep: int = 5) -> None:
        key = f"visits:{client_id}"
        self.client.lpush(key, value)
        self.client.ltrim(key, 0, keep - 1)

    def last_visits(self, client_id) -> list:
        return self.client.lrange(f"visits:{client_id}", 0, -1)

    # --- Sorted Set: рейтинг активности ---
    def add_activity(self, client_id, score: float) -> None:
        self.client.zadd("activity:rating", {str(client_id): score})

    def top_clients(self, count: int = 3) -> list:
        return self.client.zrevrange("activity:rating", 0, count - 1, withscores=True)

    # --- счётчик ---
    def increment(self, key: str, amount: int = 1) -> int:
        return self.client.incr(key, amount)

    # --- бенчмарк: MongoDB vs Redis ---
    def benchmark(self, loader, key: str, iterations: int, ttl: int = 3600) -> dict:
        import time
        self.set_json(key, loader(), ttl=ttl)
        self.delete(key)
        start = time.perf_counter()
        for _ in range(iterations):
            loader()
        db_time = time.perf_counter() - start
        start = time.perf_counter()
        for _ in range(iterations):
            self.get_json(key)
        redis_time = time.perf_counter() - start
        return {
            "iterations": iterations,
            "db_time": round(db_time, 4),
            "redis_time": round(redis_time, 4),
        }