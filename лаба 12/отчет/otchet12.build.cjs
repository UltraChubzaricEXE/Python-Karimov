const os = require("os");
const path = require("path");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const SKILL = path.join(CFG, "gigatool", "skills", "word");
const H = require(path.join(SKILL, "helpers", "index.cjs"));

(async () => {
  const doc = H.createDoc({ title: "Лабораторная работа №12" });

  doc.heading("Лабораторная работа №12", 1);
  doc.heading("Работа с реляционными базами данных в Python с использованием SQLAlchemy и ORM", 2);
  doc.paragraph("Вариант 8. Авиабилеты. Разработано консольное приложение с сущностями Passenger (пассажир), "
    + "Flight (рейс) и Ticket (билет). Доступ к базе выполняется через SQLAlchemy 2.x ORM. Реализованы покупка "
    + "и отмена билета как транзакция с изменением количества проданных мест на рейсе.");

  doc.heading("1. Цель работы", 2);
  doc.paragraph("Получить практические навыки разработки Python-приложений, взаимодействующих с реляционной базой "
    + "данных посредством ORM-библиотеки SQLAlchemy: изучить принципы ORM, описывать модели БД в виде Python-классов, "
    + "выполнять CRUD-операции, устанавливать связи, фильтровать, сортировать и искать данные, использовать транзакции, "
    + "разделять модели, доступ к данным и бизнес-логику.");

  doc.heading("2. Постановка индивидуального задания", 2);
  doc.paragraph("Вариант 8. Авиабилеты. Сущности: Passenger (пассажир), Flight (рейс), Ticket (билет). "
    + "Реализовать покупку и отмену билета.");
  doc.bullets([
    "не менее трёх сущностей со связями 1:N (Passenger - Tickets, Flight - Tickets);",
    "создание, получение по ID, список, изменение, удаление, поиск и фильтрация;",
    "минимум два варианта сортировки; получение связанных данных (билеты пассажира, билеты рейса);",
    "транзакционная операция: покупка билета уменьшает счётчик проданных мест, отмена — увеличивает; при ошибке — ROLLBACK;",
    "обработка ошибок: отсутствие объекта, дубликат email, занятое место, полностью занятый рейс;",
    "использование SQLAlchemy 2.x (Mapped, mapped_column, relationship), без ручного SQL для основных операций;",
    "автоматические тесты (pytest).",
  ]);

  doc.heading("3. Краткие теоретические сведения", 2);
  doc.bullets([
    "ORM (Object-Relational Mapping) отображает таблицы БД на Python-классы и уменьшает количество ручного SQL.",
    "SQLAlchemy состоит из Engine (соединение), Session (рабочая сессия), Model (сущность), Query, Relationship (связи), Transaction.",
    "Модель описывается через DeclarativeBase; поля — Mapped[int] + mapped_column; связи — relationship() с back_populates.",
    "CRUD: session.add() + commit() (create), session.get() (read), изменение атрибута + commit() (update), session.delete() (delete).",
    "Фильтрация — where(), сортировка — order_by(); получение связанных объектов — через relationship.",
    "Транзакция: несколько изменений фиксируются одним commit(); при исключении — rollback().",
    "Связь 1:N: foreign key на стороне «многие» и relationship на обеих сторонах; уникальные ограничения и NOT NULL повышают целостность.",
  ]);

  doc.heading("4. Архитектура приложения", 2);
  doc.paragraph("Схема: Service → Repository → SQLAlchemy ORM → SQLite/PostgreSQL. Модели вынесены в отдельный модуль, "
    + "доступ к данным — в Repository, бизнес-логика — в Service, точка входа — main.py.");
  doc.table([
    ["Модуль", "Назначение"],
    ["database.py", "Engine, Session, DeclarativeBase, create_all"],
    ["models.py", "ORM-модели Passenger, Flight, Ticket и их связи"],
    ["repository.py", "CRUD-запросы через сессию SQLAlchemy"],
    ["service.py", "бизнес-логика: регистрация, покупка/отмена билета, транзакции"],
    ["main.py", "консольная демонстрация"],
  ], { widths: [0.26, 0.74] });

  doc.heading("5. Модель данных (ER-схема)", 2);
  doc.paragraph("Passenger (id PK, full_name, passport, email UNIQUE, phone) ──1:N── Ticket (id PK, passenger_id FK, "
    + "flight_id FK, seat, status, booked_at) ──N:1── Flight (id PK, number, origin, destination, departure, price, "
    + "total_seats, sold_seats). Удаление пассажира каскадно удаляет его билеты (cascade='all, delete-orphan').");

  doc.heading("6. Исходный код", 2);
  doc.paragraph("Полный исходный код проекта (модули database, models, repository, service, main и тесты) размещён "
    + "в репозитории GitHub в папке 12_airlines/src и 12_airlines/tests:");
  doc.paragraph("https://github.com/ВАШ_ЛОГИН/python_labs/tree/main/12_airlines");
  doc.paragraph("Модели Passenger, Flight и Ticket описаны классами SQLAlchemy 2.x с relationship; покупка и "
    + "отмена билета выполняются как транзакции с атомарным изменением счётчика проданных мест.");

  doc.heading("7. Результаты работы", 2);
  doc.bullets([
    "зарегистрировано 3 пассажира, создано 4 рейса;",
    "покупка билетов изменяет счётчик проданных мест: 3 → 4;",
    "попытка купить билет на полностью занятый рейс вызывает NoFreeSeatsError;",
    "отмена билета вернула место: 2 → 1;",
    "повторная отмена вызывает InvalidOperationError;",
    "автоматические тесты: 16 passed.",
  ]);

  doc.heading("8. Вывод", 2);
  doc.paragraph("В ходе работы освоены принципы ORM и разработано приложение авиакомпании с сущностями Passenger, "
    + "Flight и Ticket. Модели описаны классами SQLAlchemy 2.x, связи 1:N реализованы через relationship. "
    + "Выполнены CRUD, поиск, фильтрация и сортировка. Покупка и отмена билета реализованы как транзакции с "
    + "атомарным изменением количества проданных мест. Обрабатываются отсутствие объекта, дубликаты, занятые места "
    + "и переполненные рейсы. Repository изолирует доступ к данным от бизнес-логики.");

  await doc.save(path.join(__dirname, "Отчет_ЛР12_Python_вариант8.docx"));
  console.log("saved");
})();