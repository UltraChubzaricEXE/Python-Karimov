"""Лабораторная работа №12. Вариант 8. Авиабилеты (SQLAlchemy ORM).

Демонстрация: Passenger, Flight, Ticket; покупка и отмена билета
с транзакцией, поиск, фильтрация, сортировка, связи.
"""
import datetime as dt

from database import SessionLocal, init_db
from service import AirlineService


def seed(service: AirlineService) -> None:
    pas1 = service.register_passenger("Иванов Иван", "4502 123456", "ivan@example.com", "+79150000001")
    pas2 = service.register_passenger("Петрова Анна", "4502 654321", "anna@example.com", "+79150000002")
    pas3 = service.register_passenger("Сидоров Павел", "4502 987654", "pavel@example.com", "+79150000003")

    now = dt.datetime.now() + dt.timedelta(days=1)
    f1 = service.create_flight("SU-1001", "Москва", "Санкт-Петербург",
                               now, 3500, 60)
    f2 = service.create_flight("SU-1002", "Москва", "Сочи",
                               now + dt.timedelta(days=2), 12000, 40)
    f3 = service.create_flight("SU-1003", "Санкт-Петербург", "Москва",
                               now + dt.timedelta(days=3), 4000, 50)

    service.buy_ticket(pas1.id, f1.id, "12A")
    service.buy_ticket(pas1.id, f2.id, "05B")
    service.buy_ticket(pas2.id, f1.id, "14C")
    service.buy_ticket(pas3.id, f3.id, "01A")
    return pas1, pas2, pas3, f1, f2, f3


def main() -> None:
    print("===== ЛР12. Авиабилеты (SQLAlchemy ORM) =====")
    init_db()
    session = SessionLocal()
    service = AirlineService(session)

    # Начальные данные (если база пустая)
    if not service.list_passengers():
        seed(service)
        print("Созданы демонстрационные данные.")

    print("\n--- 1. Пассажиры ---")
    for p in service.list_passengers():
        print(f" #{p.id} {p.full_name}, паспорт {p.passport}, email {p.email}")

    print("\n--- 2. Рейсы ---")
    for f in service.list_flights():
        print(f" #{f.id} {f.number}: {f.origin} -> {f.destination}, "
              f"{f.departure.strftime('%d.%m %H:%M')}, {f.price:.0f} руб., "
              f"свободно {f.free_seats} из {f.total_seats}")

    print("\n--- 3. Поиск рейсов по направлению ---")
    found = service.search_flights("Москва")
    for f in found:
        print(f"  {f.number}: {f.origin} -> {f.destination}, {f.departure.strftime('%d.%m %H:%M')}")

    print("\n--- 4. Покупка билета (транзакция) ---")
    pas = service.list_passengers()[0]
    flight = service.search_flights("Москва")[1]
    print(f"Пассажир #{pas.id} покупает билет на рейс {flight.number}")
    before = flight.sold_seats
    ticket = service.buy_ticket(pas.id, flight.id, "20E")
    after = service.get_flight(flight.id).sold_seats
    print(f"Билет №{ticket.id} оформлен (место {ticket.seat}). "
          f"Продано мест: {before} -> {after}")

    print("\n--- 5. Попытка купить на полностью занятый рейс ---")
    # демонстрация ошибки: создадим рейс с одним местом и займём его
    full = service.create_flight("SU-FULL", "Казань", "Москва",
                                 dt.datetime.now() + dt.timedelta(days=1), 5000, 1)
    service.buy_ticket(pas.id, full.id, "01A")  # занимаем единственное место
    try:
        service.buy_ticket(pas.id, full.id, "01B")
    except Exception as exc:
        print(f"  Ошибка (ожидаемо): {exc}")

    print("\n--- 6. Отмена билета (транзакция) ---")
    t = service.passenger_tickets(pas.id)[0]
    f_before = service.get_flight(t.flight_id).sold_seats
    service.cancel_ticket(t.id)
    f_after = service.get_flight(t.flight_id).sold_seats
    print(f"Билет №{t.id} отменён. Продано мест на рейсе: {f_before} -> {f_after}")

    print("\n--- 7. Связь: билеты пассажира ---")
    for p in service.list_passengers():
        print(f" {p.full_name}: {[(t.seat, t.status) for t in service.passenger_tickets(p.id)]}")

    session.close()


if __name__ == "__main__":
    main()