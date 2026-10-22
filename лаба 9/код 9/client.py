"""TCP-клиент кинотеатра.

Подключается к серверу, предоставляет пользователю меню команд,
формирует JSON-запросы, отправляет их и выводит ответы.
"""
import socket

from exceptions import ProtocolError
from protocol import decode_messages, encode_message

HOST = "127.0.0.1"
PORT = 5000
TIMEOUT = 5


class CinemaClient:
    """Клиентский слой: установка соединения, запросы, вывод."""

    def __init__(self, host: str = HOST, port: int = PORT) -> None:
        self.host = host
        self.port = port
        self.sock: socket.socket | None = None

    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(TIMEOUT)
        try:
            self.sock.connect((self.host, self.port))
        except (ConnectionRefusedError, socket.timeout) as exc:
            raise ConnectionError(f"Сервер недоступен: {exc}") from exc

    def close(self) -> None:
        if self.sock:
            self.sock.close()
            self.sock = None

    def send_command(self, command: str, data: dict | None = None) -> dict:
        """Отправляет запрос и получает ответ."""
        if self.sock is None:
            raise ConnectionError("Клиент не подключён")
        request = {"command": command, "data": data or {}}
        self.sock.sendall(encode_message(request))
        # читаем одну строку (один ответ) с учётом возможного склеивания
        buffer = ""
        while "\n" not in buffer:
            chunk = self.sock.recv(4096).decode("utf-8", errors="replace")
            if not chunk:
                raise ConnectionError("Соединение разорвано сервером")
            buffer += chunk
        messages, _ = decode_messages(buffer)
        if not messages:
            raise ProtocolError("Сервер вернул пустой ответ")
        return messages[0]

    def _read_nonempty(self, prompt: str) -> str:
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("Ошибка: значение не может быть пустым")

    def _read_float(self, prompt: str) -> float:
        while True:
            text = input(prompt).strip().replace(",", ".")
            try:
                return float(text)
            except ValueError:
                print("Ошибка: введите число")

    def _print_movies(self, movies: list) -> None:
        if not movies:
            print(" (фильмы не найдены)")
            return
        for m in movies:
            print(f" №{m['id']}: {m['title']} ({m['year']}) — {m['director']}; "
                  f"жанр: {m['genre']}; {m['duration_min']} мин; рейтинг {m['rating']}")

    def run(self) -> None:
        """Главное меню клиента."""
        print("=== КЛИЕНТ КИНОТЕАТРА ===")
        try:
            self.connect()
            print("Подключено к серверу.")
        except ConnectionError as exc:
            print(f"Ошибка подключения: {exc}")
            return

        while True:
            print("\n1. Получить список фильмов")
            print("2. Получить фильм по номеру")
            print("3. Создать фильм")
            print("4. Изменить фильм")
            print("5. Удалить фильм")
            print("6. Поиск фильмов по жанру")
            print("0. Выход")
            choice = input("Выберите команду: ").strip()
            try:
                if choice == "1":
                    self._cmd_list()
                elif choice == "2":
                    self._cmd_get()
                elif choice == "3":
                    self._cmd_create()
                elif choice == "4":
                    self._cmd_update()
                elif choice == "5":
                    self._cmd_delete()
                elif choice == "6":
                    self._cmd_by_genre()
                elif choice == "0":
                    break
                else:
                    print("Ошибка: нет такой команды")
            except (ConnectionError, ProtocolError) as exc:
                print(f"Ошибка: {exc}")
                break
            except Exception as exc:
                print(f"Ошибка: {exc}")
        self.close()
        print("Работа завершена")

    # --- обработчики команд ---
    def _cmd_list(self) -> None:
        response = self.send_command("list")
        self._print_movies(response["data"])

    def _cmd_get(self) -> None:
        mid = int(input("Номер фильма: ").strip())
        response = self.send_command("get", {"id": mid})
        self._print_movies([response["data"]])

    def _read_movie_data(self) -> dict:
        data = {
            "title": self._read_nonempty("Название: "),
            "director": self._read_nonempty("Режиссёр: "),
            "genre": self._read_nonempty("Жанр: "),
            "year": int(self._read_nonempty("Год выпуска: ")),
            "duration_min": int(self._read_nonempty("Продолжительность (мин): ")),
            "rating": self._read_float("Рейтинг (0..10): "),
        }
        return data

    def _cmd_create(self) -> None:
        data = self._read_movie_data()
        response = self.send_command("create", data)
        print("Создан фильм:", response["data"])

    def _cmd_update(self) -> None:
        mid = int(input("Номер фильма: ").strip())
        data = self._read_movie_data()
        data["id"] = mid
        response = self.send_command("update", data)
        print("Обновлён фильм:", response["data"])

    def _cmd_delete(self) -> None:
        mid = int(input("Номер фильма: ").strip())
        response = self.send_command("delete", {"id": mid})
        print("Удалён фильм №", response["data"]["deleted"])

    def _cmd_by_genre(self) -> None:
        genre = self._read_nonempty("Жанр: ")
        response = self.send_command("by_genre", {"genre": genre})
        self._print_movies(response["data"])


if __name__ == "__main__":
    CinemaClient().run()