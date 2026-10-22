const os = require("os");
const path = require("path");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const SKILL = path.join(CFG, "gigatool", "skills", "word");
const H = require(path.join(SKILL, "helpers", "index.cjs"));

(async () => {
  const doc = H.createDoc({ title: "Лабораторная работа №10" });

  doc.heading("Лабораторная работа №10", 1);
  doc.heading("HTTP и REST API в Python: разработка клиент-серверного веб-приложения", 2);
  doc.paragraph("Вариант 8. Фитнес-центр — клиенты (/clients). Разработано REST API на Flask для управления "
    + "клиентами фитнес-центра и отдельная программа-клиент на библиотеке requests. Реализован полный CRUD, "
    + "фильтрация, сортировка и специализированный endpoint «активные абонементы».");

  doc.heading("1. Цель работы", 2);
  doc.paragraph("Изучить принципы работы протокола HTTP и получить практические навыки разработки и использования "
    + "REST API на Python: разобраться с методами GET, POST, PUT, PATCH, DELETE, HTTP-заголовками и кодами состояния, "
    + "изучить принципы REST, разработать собственный HTTP API на Flask, реализовать клиента на requests, обрабатывать "
    + "ошибки, валидировать данные и тестировать API.");

  doc.heading("2. Постановка индивидуального задания", 2);
  doc.paragraph("Вариант 8. Фитнес-центр. Основной ресурс — Client (клиент): id, имя, возраст, абонемент, статус "
    + "абонемента, цели, тренер. Специализированная операция — список клиентов с активными абонементами.");
  doc.bullets([
    "полный CRUD: GET /clients, GET /clients/{id}, POST, PUT, PATCH, DELETE;",
    "фильтрация по status и membership, сортировка по age/name (asc/desc);",
    "специализированный endpoint GET /clients/who-active;",
    "валидация входных данных (Pydantic-подход через сервис), единый формат ошибок;",
    "корректные HTTP-коды (200, 201, 204, 400, 404);",
    "отдельная программа-клиент client.py с консольным меню на requests;",
    "минимум 10 автоматических тестов (pytest).",
  ]);

  doc.heading("3. Краткие теоретические сведения", 2);
  doc.paragraph("HTTP — протокол прикладного уровня для обмена данными между клиентом и сервером. Запрос состоит из "
    + "строки запроса (метод + URI), заголовков и тела. В REST API URL описывает ресурс, а HTTP-метод — действие: "
    + "GET — чтение, POST — создание, PUT — полное изменение, PATCH — частичное, DELETE — удаление.");
  doc.bullets([
    "коды состояния: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 404 Not Found, 500 Internal Server Error;",
    "path-параметры передают идентификатор ресурса (/clients/15), query-параметры — фильтры и сортировку;",
    "JSON используется для передачи данных; Content-Type: application/json;",
    "бизнес-логика размещается в Service, а не в HTTP-маршрутах; хранение — в Repository;",
    "REST стремится к stateless-взаимодействию: каждый запрос содержит всю нужную информацию.",
  ]);

  doc.heading("4. Архитектура приложения", 2);
  doc.paragraph("Схема: Client → HTTP → REST API (Flask) → Service → Repository (в памяти).");
  doc.bullets([
    "models.py — датакласс Client с to_dict()/from_dict();",
    "repository.py — хранение клиентов в памяти;",
    "service.py — бизнес-логика, валидация, пользовательские исключения;",
    "app.py — Flask-приложение, маршруты, обработчики ошибок;",
    "client.py — HTTP-клиент на requests с консольным меню;",
    "tests/ — автоматические тесты.",
  ]);

  doc.heading("5. Таблица API", 2);
  doc.table([
    ["Метод", "Endpoint", "Назначение", "Код"],
    ["GET", "/clients", "список (с фильтрацией/сортировкой)", "200"],
    ["GET", "/clients/{id}", "клиент по номеру", "200/404"],
    ["POST", "/clients", "создание клиента", "201"],
    ["PUT", "/clients/{id}", "полное изменение", "200"],
    ["PATCH", "/clients/{id}", "частичное изменение", "200"],
    ["DELETE", "/clients/{id}", "удаление", "204"],
    ["GET", "/clients/who-active", "активные абонементы", "200"],
  ], { widths: [0.14, 0.26, 0.42, 0.18] });

  doc.heading("6. Исходный код", 2);
  doc.paragraph("Полный исходный код проекта (модули models, repository, service, app, client и тесты) размещён "
    + "в репозитории GitHub в папке 10_fitness/src и 10_fitness/tests:");
  doc.paragraph("https://github.com/ВАШ_ЛОГИН/python_labs/tree/main/10_fitness");
  doc.paragraph("Автоматические тесты (pytest): 18 passed — репозиторий (2), сервис (5), REST API (11). "
    + "HTTP-клиент client.py выполняет запросы GET/POST/PUT/PATCH/DELETE через библиотеку requests.");

  doc.heading("7. Вывод", 2);
  doc.paragraph("В ходе работы освоено устройство HTTP и принципы REST. Разработано REST API фитнес-центра на Flask "
    + "с полным CRUD для клиентов, фильтрацией, сортировкой и специализированным endpoint «активные абонементы». "
    + "Сетевой слой отделён от бизнес-логики (Service) и хранения (Repository). Реализованы валидация, единый формат "
    + "ошибок и корректные HTTP-коды. Программа-клиент на requests взаимодействует с API через консольное меню. "
    + "Написаны автоматические тесты (18 passed), подтверждающие корректность работы.");

  await doc.save(path.join(__dirname, "Отчет_ЛР10_Python_вариант8.docx"));
  console.log("saved");
})();