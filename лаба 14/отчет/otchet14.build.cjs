const os = require("os");
const path = require("path");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const SKILL = path.join(CFG, "gigatool", "skills", "word");
const H = require(path.join(SKILL, "helpers", "index.cjs"));

(async () => {
  const doc = H.createDoc({ title: "Лабораторная работа №14" });

  doc.heading("Лабораторная работа №14", 1);
  doc.heading("Разработка REST API на Python с использованием FastAPI", 2);
  doc.paragraph("Вариант 8. Фитнес-центр — клиенты (/clients). Разработан современный REST API на FastAPI с "
    + "автоматической документацией OpenAPI (Swagger UI). Реализованы полный CRUD, поиск, фильтрация, сортировка, "
    + "пагинация и статистика. Данные хранятся в памяти через репозиторий; бизнес-логика вынесена в сервис; "
    + "используются Pydantic-схемы и Dependency Injection.");

  doc.heading("1. Цель работы", 2);
  doc.paragraph("Получить практические навыки разработки современных REST API на Python с использованием FastAPI: "
    + "создавать HTTP-эндпоинты, использовать GET/POST/PUT/PATCH/DELETE, path- и query-параметры, Pydantic для "
    + "валидации, HTTP-коды состояния, автоматическую документацию OpenAPI, Dependency Injection, разделять API "
    + "на слои, реализовать пагинацию и фильтрацию, писать автоматические тесты и понимать синхронность/асинхронность.");

  doc.heading("2. Постановка индивидуального задания", 2);
  doc.paragraph("Вариант 8. Фитнес-центр. Основная сущность — Client: ФИО, возраст, абонемент, цели, тренер, "
    + "дата регистрации, статус. API /clients.");
  doc.bullets([
    "полный CRUD: GET /clients, GET /clients/{id}, POST, PUT, PATCH, DELETE;",
    "GET /clients/search?q=... — поиск по имени;",
    "GET /clients/statistics — три статистических показателя;",
    "GET /clients/active — специализированный endpoint «активные абонементы»;",
    "query-параметры: status, membership (фильтры), sort, order (сортировка), limit, offset (пагинация);",
    "Pydantic-схемы ClientCreate, ClientUpdate, ClientResponse и валидация (422 при ошибке);",
    "корректные HTTP-коды: 200, 201, 204, 404, 422;",
    "разделение слоёв Router → Service → Repository;",
    "минимум один async-эндпоинт (/health), Dependency Injection через Depends;",
    "минимум 15 автоматических тестов.",
  ]);

  doc.heading("3. Краткие теоретические сведения", 2);
  doc.bullets([
    "FastAPI — современный Python-фреймворк для API: автоматическая OpenAPI-документация, автовалидация через Pydantic, синхронные и асинхронные обработчики.",
    "Endpoint — комбинация HTTP-метода и URL; путь к ресурсу (/clients/15) — path-параметр, фильтры (?sort=age&order=desc) — query-параметры.",
    "HTTP-коды: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 404 Not Found, 422 Validation Error, 500 Internal Server Error.",
    "Pydantic гарантирует валидацию входных данных и описание схемы API; Field(min_length=..., gt=...) задаёт ограничения.",
    "Dependency Injection (Depends) отделяет HTTP-слой от зависимости: слот получает сервис, а не создаёт его сам.",
    "Swagger UI доступен по /docs — автоматическое описание эндпоинтов, параметров и моделей.",
    "async def полезно для I/O-операций (БД, сеть), но не ускоряет CPU-bound вычисления.",
  ]);

  doc.heading("4. Архитектура приложения", 2);
  doc.paragraph("Схема: Client → HTTP → FastAPI App → Router → Service → Repository (в памяти).");
  doc.table([
    ["Модуль", "Назначение"],
    ["main.py", "приложение FastAPI, lifespan, загрузка демо-данных, async /health"],
    ["routers.py", "HTTP-эндпоинты /clients, Dependency Injection"],
    ["schemas.py", "Pydantic-схемы ClientCreate/Update/Response/ListParams"],
    ["service.py", "бизнес-логика: фильтрация, сортировка, пагинация, статистика"],
    ["repository.py", "хранение клиентов в памяти, CRUD"],
  ], { widths: [0.24, 0.76] });

  doc.heading("5. Таблица API", 2);
  doc.table([
    ["Метод", "Endpoint", "Назначение", "Код"],
    ["GET", "/clients", "список (фильтры, сортировка, пагинация)", "200"],
    ["GET", "/clients/{id}", "клиент по номеру", "200/404"],
    ["POST", "/clients", "создание клиента", "201"],
    ["PUT", "/clients/{id}", "полное изменение", "200"],
    ["PATCH", "/clients/{id}", "частичное изменение", "200"],
    ["DELETE", "/clients/{id}", "удаление", "204"],
    ["GET", "/clients/search", "поиск по имени", "200"],
    ["GET", "/clients/statistics", "статистика", "200"],
    ["GET", "/clients/active", "активные абонементы", "200"],
  ], { widths: [0.14, 0.26, 0.44, 0.16] });

  doc.heading("6. Исходный код", 2);
  doc.paragraph("Полный исходный код проекта (модули main, routers, schemas, service, repository и тесты) размещён "
    + "в репозитории GitHub в папке 14_fitness/src и 14_fitness/tests:");
  doc.paragraph("https://github.com/ВАШ_ЛОГИН/python_labs/tree/main/14_fitness");
  doc.paragraph("Данные валидируются Pydantic-схемами (ClientCreate/ClientUpdate/ClientResponse), применяется "
    + "Dependency Injection через Depends, реализованы поиск, фильтрация, сортировка, пагинация, статистика и "
    + "асинхронный endpoint /health.");

  doc.heading("7. Вывод", 2);
  doc.paragraph("В ходе работы освоены принципы разработки REST API на FastAPI. Создано приложение управления "
    + "клиентами фитнес-центра: полный CRUD, поиск, фильтрация, сортировка, пагинация и статистика. Данные "
    + "валидируются Pydantic-схемами, возвращаются корректные HTTP-коды, реализована автоматическая документация "
    + "OpenAPI (Swagger). HTTP-слой отделён от бизнес-логики (Service) и хранения (Repository), использована "
    + "Dependency Injection. Написаны 23 автоматических теста. Показан асинхронный эндпоинт /health.");

  await doc.save(path.join(__dirname, "Отчет_ЛР14_Python_вариант8.docx"));
  console.log("saved");
})();