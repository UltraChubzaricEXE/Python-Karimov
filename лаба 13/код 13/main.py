"""Лабораторная работа №13. Вариант 8. Фитнес-центр.

Демонстрация: MongoDB (20+ документов клиентов), Redis (кэш Cache-Aside,
Hash, List, Sorted Set, TTL), инвалидация кэша, сравнение скорости.
При отсутствии серверов используется mongomock/fakeredis.
"""
from config import make_mongo_client, make_redis_client
from mongodb_repo import MongoRepository
from redis_cache import RedisCache
from seed import seed_data
from service import FitnessService


def main() -> None:
    print("===== ЛР13. Фитнес-центр (MongoDB + Redis) =====")

    mongo = make_mongo_client()
    redis = make_redis_client()
    try:
        mongo.admin.command("ping")
        print("[MongoDB] реальный сервер.")
    except Exception:
        print("[MongoDB] недоступен - mongomock (в памяти).")

    repo = MongoRepository(mongo)
    repo.ensure_indexes()
    cache = RedisCache(redis)
    service = FitnessService(repo, cache)

    # Заполняем БД 20 документами
    existing = repo.find_all()
    if not existing:
        for doc in seed_data():
            repo.insert(doc)
        print("Вставлено документов:", len(repo.find_all()))

    print("\n--- 1. Список клиентов (первые 5) ---")
    for c in repo.find_all()[:5]:
        print(f"  {c['full_name']}, {c['age']} лет, {c['status']}, "
              f"город {c['address']['city']}")

    print("\n--- 2. Вложенный объект: клиенты города Москва ---")
    for c in service.in_city("Москва")[:3]:
        print(f"  {c['full_name']} ({c['address']['street']})")

    print("\n--- 3. Массив: клиенты с целью 'похудение' ---")
    for c in service.by_goal("похудение")[:3]:
        print(f"  {c['full_name']}: {c['goals']}")

    print("\n--- 4. Статус/тип: активные клиенты ---")
    print("  Активных:", len(service.active_clients()))

    print("\n--- 5. Агрегирующие запросы ---")
    print("  По статусам:", service.stats()["by_status"])
    print(f"  Средний возраст: {service.stats()['avg_age']}")

    print("\n--- 6. Cache-Aside: получение клиента через Redis ---")
    docs = repo.find_all()
    first_id = str(docs[0]["_id"])
    data, hit = service.get_client_cached(first_id)
    print(f"  1-й запрос (клиент {docs[0]['full_name']}): source=", "cache" if hit else "mongo")
    data, hit = service.get_client_cached(first_id)
    print(f"  2-й запрос: source=", "cache" if hit else "mongo")

    print("\n--- 7. Инвалидация кэша ---")
    updated = service.update_client(first_id, {"age": docs[0]["age"] + 1})
    print("  update:", updated, "; после него кэш удалён, следующий запрос - из Mongo")

    print("\n--- 8. Redis Hash: текущая тренировка ---")
    service.set_workout(first_id, {"exercise": "беговая дорожка", "duration": 45})
    print("  ", service.cache.get_current_workout(first_id))

    print("\n--- 9. Redis List: последние посещения ---")
    service.record_visit(first_id, "2024-10-10")
    service.record_visit(first_id, "2024-10-08")
    print("  ", service.cache.last_visits(first_id))

    print("\n--- 10. Redis Sorted Set: рейтинг активности ---")
    service.cache.add_activity(docs[0]["_id"], 1)
    service.cache.add_activity(docs[1]["_id"], 5)
    service.cache.add_activity(docs[2]["_id"], 3)
    print("  Топ-2:", service.cache.top_clients(2))

    print("\n--- 11. TTL ---")
    key = "test:ttl"
    cache.set_json(key, "v", ttl=60)
    print(f"  TTL ключа: {cache.ttl(key)} сек")

    print("\n--- 12. Сравнение скорости: Mongo vs Redis ---")
    def _serializable_all():
        docs = repo.find_all()
        for d in docs:
            d["_id"] = str(d["_id"])
        return docs
    bench = cache.benchmark(_serializable_all, "clients:all", iterations=100)
    print(f"  {bench['iterations']} запросов: Mongo={bench['db_time']}с, Redis={bench['redis_time']}с")


if __name__ == "__main__":
    main()