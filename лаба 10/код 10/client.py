"""HTTP-клиент для REST API фитнес-центра. ЛР10, вариант 8."""
import requests

BASE = "http://127.0.0.1:5001"


def _nonempty(prompt):
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("Ошибка: пустое значение")


def _int_pos(prompt):
    while True:
        text = input(prompt).strip()
        if text.isdigit() and int(text) > 0:
            return int(text)
        print("Ошибка: целое положительное число")


def _read_client():
    return {
        "name": _nonempty("Имя клиента: "),
        "age": _int_pos("Возраст: "),
        "membership": input("Абонемент (разовый/месячный/годовой) [месячный]: ").strip() or "месячный",
        "membership_status": input("Статус (активен/истёк/заморожен/отменён) [активен]: ").strip() or "активен",
        "trainer": input("Тренер: ").strip() or "",
    }


def _print(clients):
    if not clients:
        print(" (пусто)")
        return
    for c in clients:
        print(f" №{c['id']}: {c['name']}, {c['age']} лет, абонемент «{c['membership']}» "
              f"({c['membership_status']})" + (f", тренер {c['trainer']}" if c.get("trainer") else ""))


def main():
    print("===== REST CLIENT. Фитнес-центр =====")
    while True:
        print("\n1. Получить список")
        print("2. Получить клиента по номеру")
        print("3. Создать клиента")
        print("4. Изменить клиента (PUT)")
        print("5. Частично изменить (PATCH)")
        print("6. Удалить клиента")
        print("7. Фильтрация (статус)")
        print("8. Сортировка по возрасту")
        print("9. Активные абонементы")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "1":
                r = requests.get(f"{BASE}/clients"); r.raise_for_status()
                _print(r.json())
            elif choice == "2":
                cid = _int_pos("Номер клиента: ")
                r = requests.get(f"{BASE}/clients/{cid}")
                if r.status_code == 404:
                    print("Ошибка:", r.json().get("error"))
                else:
                    r.raise_for_status(); _print([r.json()])
            elif choice == "3":
                r = requests.post(f"{BASE}/clients", json=_read_client())
                if r.status_code == 400:
                    print("Ошибка:", r.json().get("error"))
                else:
                    r.raise_for_status(); print("Создан:", r.json())
            elif choice == "4":
                cid = _int_pos("Номер клиента: ")
                r = requests.put(f"{BASE}/clients/{cid}", json=_read_client())
                print("Ошибка:" if r.status_code >= 400 else "Обновлён:", r.json().get("error") or r.json())
            elif choice == "5":
                cid = _int_pos("Номер клиента: ")
                field = input("Поле (age/membership_status/trainer): ").strip() or "age"
                value = input("Новое значение: ").strip()
                r = requests.patch(f"{BASE}/clients/{cid}", json={field: value})
                print("Ошибка:" if r.status_code >= 400 else "Обновлён:", r.json().get("error") or r.json())
            elif choice == "6":
                cid = _int_pos("Номер клиента: ")
                r = requests.delete(f"{BASE}/clients/{cid}")
                print("Удалён" if r.status_code == 204 else ("Ошибка: " + r.json().get("error", "")))
            elif choice == "7":
                st = input("Статус: ").strip()
                r = requests.get(f"{BASE}/clients", params={"status": st}); r.raise_for_status()
                _print(r.json())
            elif choice == "8":
                order = input("Порядок (asc/desc) [asc]: ").strip() or "asc"
                r = requests.get(f"{BASE}/clients", params={"sort": "age", "order": order}); r.raise_for_status()
                _print(r.json())
            elif choice == "9":
                r = requests.get(f"{BASE}/clients/who-active"); r.raise_for_status()
                _print(r.json())
            elif choice == "0":
                break
            else:
                print("Ошибка: нет такого пункта")
        except requests.RequestException as exc:
            print(f"Ошибка запроса: {exc}")
    print("Работа завершена")


if __name__ == "__main__":
    main()