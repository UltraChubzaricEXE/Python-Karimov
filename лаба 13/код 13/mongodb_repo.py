"""Документный репозиторий клиентов фитнес-центра в MongoDB (ЛР13, вариант 8).

Документ client содержит простые поля, вложенный объект (membership),
массив (training_day), статус/тип, цели и тренера.
"""
from pymongo.collection import Collection


class MongoRepository:
    """CRUD-операции над коллекцией client в MongoDB."""

    COLLECTION = "client"

    def __init__(self, client, db_name: str = "fitness_center") -> None:
        self.db = client[db_name]
        self.collection: Collection = self.db[self.COLLECTION]

    def ensure_indexes(self) -> None:
        """Индексы под частые запросы."""
        self.collection.create_index("full_name")
        self.collection.create_index("status")

    # ---------- Create ----------
    def insert(self, document: dict) -> str:
        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    # ---------- Read ----------
    def find_by_id(self, doc_id) -> dict | None:
        from bson import ObjectId
        try:
            key = ObjectId(doc_id) if isinstance(doc_id, str) else doc_id
        except Exception:
            key = doc_id
        return self.collection.find_one({"_id": key})

    def find_all(self) -> list:
        return list(self.collection.find())

    def find(self, query: dict) -> list:
        return list(self.collection.find(query))

    # ---------- Update ----------
    def update(self, doc_id, fields: dict) -> bool:
        from bson import ObjectId
        try:
            key = ObjectId(doc_id) if isinstance(doc_id, str) else doc_id
        except Exception:
            key = doc_id
        result = self.collection.update_one({"_id": key}, {"$set": fields})
        return result.modified_count > 0

    # ---------- Delete ----------
    def delete(self, doc_id) -> bool:
        from bson import ObjectId
        try:
            key = ObjectId(doc_id) if isinstance(doc_id, str) else doc_id
        except Exception:
            key = doc_id
        result = self.collection.delete_one({"_id": key})
        return result.deleted_count > 0

    # ---------- Специализированные запросы ----------
    def find_by_status(self, status: str) -> list:
        return list(self.collection.find({"status": status}))

    def find_by_trainer(self, trainer: str) -> list:
        return list(self.collection.find({"trainer": trainer}))

    def find_by_goal(self, goal: str) -> list:
        return list(self.collection.find({"goals": goal}))

    def find_in_city(self, city: str) -> list:
        # поиск по вложенному полю address.city
        return list(self.collection.find({"address.city": city}))

    def find_active_after_date(self, date_str: str) -> list:
        # поиск с фильтрацией по дате регистрации и статусу
        return list(self.collection.find({"status": "активен", "registered_at": {"$gte": date_str}}))

    def aggregate_by_status(self) -> list:
        """Агрегация $group по статусу (COUNT)."""
        return list(self.collection.aggregate([
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]))

    def aggregate_avg_age(self) -> float:
        result = list(self.collection.aggregate([
            {"$group": {"_id": None, "avg_age": {"$avg": "$age"}}},
        ]))
        return result[0]["avg_age"] if result else 0.0