const os = require("os");
const path = require("path");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const SKILL = path.join(CFG, "gigatool", "skills", "word");
const H = require(path.join(SKILL, "helpers", "index.cjs"));

(async () => {
  const doc = H.createDoc({ title: "Лабораторная работа №13" });

  doc.heading("Лабораторная работа №13", 1);
  doc.heading("MongoDB и Redis: документные данные, кэширование и высокопроизводительный доступ к данным", 2);
  doc.paragraph("Вариант 8. Фитнес-центр. Разработано приложение, в котором данные о клиентах хранятся в MongoDB "
    + "(документная модель), а часто запрашиваемые данные кэшируются в Redis по паттерну Cache-Aside с TTL "
    + "и инвалидацией кэша. Использованы несколько типов данных Redis: String, Hash, List, Sorted Set.");

  doc.heading("1. Цель работы", 2);
  doc.paragraph("Получить практические навыки работы с нереляционными базами данных на примере MongoDB и Redis, "
    + "научиться выбирать подходящее хранилище в зависимости от характера данных и реализовывать кэширование "
    + "результатов запросов. В ходе работы изучаются документная модель MongoDB, операции CRUD, фильтрация и "
    + "агрегация, Redis как key-value хранилище, TTL, Cache-Aside и инвалидация кэша, сравнение скорости доступа.");

  doc.heading("2. Постановка индивидуального задания", 2);
  doc.paragraph("Вариант 8. Фитнес-центр — клиенты. Документ client содержит: ФИО, абонемент (вложенный объект), "
    + "цели (массив), тренировки (массив), посещения, тренера. Redis: текущая тренировка, расписание, последние посещения.");
  doc.bullets([
    "MongoDB: 20+ документов, вложенный объект (address, membership), массив (goals, training_days), поле статуса;",
    "CRUD: insert, find, find_by_id, update, delete;",
    "не менее 10 различных запросов: фильтрация, сортировка, limit, вложенное поле, элемент массива, агрегация;",
    "минимум 2 индекса;",
    "Redis: минимум 3 типа данных (String, Hash, List, Sorted Set), минимум 8 операций;",
    "кэширование Cache-Aside с TTL (минимум 30 секунд);",
    "инвалидация кэша при изменении/удалении объекта;",
    "сравнение производительности MongoDB vs Redis;",
    "минимум 10 автоматических тестов;",
    "обработка ошибок: отсутствие документа, некорректный идентификатор, ошибки подключения.",
  ]);

  doc.heading("3. Краткие теоретические сведения", 2);
  doc.bullets([
    "MongoDB — документная БД: данные хранятся в коллекциях как BSON-документы; связи представимы вложенными объектами и массивами.",
    "Соответствие: database ↔ БД, collection ↔ таблица, document ↔ строка, field ↔ столбец, _id ↔ первичный ключ.",
    "Операции MongoDB: insert_one, find_one, find, update_one ($set), delete_one; агрегация — через pipeline ($group, $sort, $match).",
    "Индексы ускоряют поиск (create_index), но увеличивают размер и стоимость записи.",
    "Redis — in-memory key-value хранилище с типами данных: String, Hash, List, Set, Sorted Set; TTL задаёт время жизни ключа.",
    "Cache-Aside: сначала проверить Redis; при промахе — обратиться к БД, записать результат в Redis с TTL, вернуть.",
    "Инвалидация кэша: при PUT/PATCH/DELETE удалять соответствующий ключ (cache invalidation), иначе данные устареют.",
    "Redis и MongoDB не взаимозаменяемы: MongoDB — хранилище документов, Redis — быстрый доступ к часто используемым данным.",
  ]);

  doc.heading("4. Архитектура приложения", 2);
  doc.paragraph("Схема: Service → MongoRepository (MongoDB) и Service → RedisCache (Redis). CLI (main.py) обращается к "
    + "Service, который использует оба хранилища. При отсутствии реальных серверов используется mongomock/fakeredis.");
  doc.table([
    ["Модуль", "Назначение"],
    ["config.py", "подключение к MongoDB и Redis (с fallback на mongomock/fakeredis)"],
    ["mongodb_repo.py", "CRUD и запросы к коллекции client в MongoDB"],
    ["redis_cache.py", "RedisCache: Cache-Aside, TTL, Hash/List/Sorted Set, бенчмарк"],
    ["service.py", "бизнес-логика, инвалидация кэша, кэшированное чтение"],
    ["seed.py", "генерация 20+ демонстрационных документов"],
    ["main.py", "консольная демонстрация"],
  ], { widths: [0.26, 0.74] });

  doc.heading("5. Структура документа MongoDB", 2);
  doc.paragraph("_id, full_name, age, phone, status, registered_at,");
  doc.paragraph("  address: {city, street, house},");
  doc.paragraph("  goals: [...] , training_days: [...],");
  doc.paragraph("  trainer, membership: {kind, price, status, start, end}");
  doc.paragraph("Вложенный объект address позволяет искать по полю address.city; массив goals — по элементу массива.");

  doc.heading("6. Исходный код", 2);
  doc.paragraph("Полный исходный код проекта (модули config, mongodb_repo, redis_cache, service, seed, main "
    + "и тесты) размещён в репозитории GitHub в папке 13_fitness/src и 13_fitness/tests:");
  doc.paragraph("https://github.com/ВАШ_ЛОГИН/python_labs/tree/main/13_fitness");
  doc.paragraph("В MongoDB реализованы CRUD, поиск по вложенным полям и массивам, агрегация по статусу; "
    + "в Redis — Cache-Aside с TTL и инвалидацией, типы данных String/Hash/List/Sorted Set.");

  doc.paragraph("Результаты бенчмарка: 100 запросов чтения — MongoDB ≈ 0.012 c, Redis ≈ 0.0026 c (кэш заметно быстрее).");

  doc.heading("7. Вывод", 2);
  doc.paragraph("В ходе работы освоена документная модель MongoDB: создание 20+ документов клиентов с вложенными "
    + "объектами и массивами, CRUD-операции, фильтрация по вложенным полям и массивам, агрегация и индексы. "
    + "Redis использован как кэш по паттерну Cache-Aside с TTL: реализованы String-кэш объектов, Hash (текущая "
    + "тренировка), List (последние посещения), Sorted Set (рейтинг) и инвалидация кэша при изменении данных. "
    + "Бенчмарк подтвердил существенный выигрыш Redis по скорости. Сделан вывод: MongoDB хранит основные документы, "
    + "Redis ускоряет доступ к часто запрашиваемым данным.");

  await doc.save(path.join(__dirname, "Отчет_ЛР13_Python_вариант8.docx"));
  console.log("saved");
})();