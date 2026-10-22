"""Лабораторная работа №14. Вариант 8. Фитнес-центр (FastAPI).

Запуск: uvicorn main:app --reload
Swagger: http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from routers import _service as service, router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Загружаем демонстрационные данные при старте.
    demo = [
        {"name": "Иванов Иван", "age": 27, "membership": "годовой",
         "membership_status": "активен", "goals": ["похудение"], "trainer": "Мария"},
        {"name": "Петрова Анна", "age": 31, "membership": "месячный",
         "membership_status": "активен", "goals": ["тонус"], "trainer": "Мария"},
        {"name": "Сидоров Павел", "age": 25, "membership": "разовый",
         "membership_status": "истёк", "goals": [], "trainer": "Сергей"},
        {"name": "Козлов Артём", "age": 40, "membership": "годовой",
         "membership_status": "заморожен", "goals": [], "trainer": "Сергей"},
        {"name": "Смоленская Ольга", "age": 22, "membership": "месячный",
         "membership_status": "активен", "goals": ["кардио"], "trainer": "Мария"},
    ]
    if not service.list_clients():
        for item in demo:
            service.create_client(item)
    yield


app = FastAPI(title="Фитнес-центр API", version="1.0.0", lifespan=lifespan)
app.include_router(router)


# Асинхронный endpoint в дополнение к синхронным.
@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok"}