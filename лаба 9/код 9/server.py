"""TCP-сервер кинотеатра.

Принимает подключения нескольких клиентов (ThreadPoolExecutor),
разбирает запросы по протоколу JSON, обращается к сервису и отвечает.
"""
import json
import logging
import socket
from concurrent.futures import ThreadPoolExecutor

from exceptions import (CinemaError, ProtocolError, ValidationError)
from models import Movie
from protocol import decode_messages, encode_message, make_response
from repository import MovieRepository
from service import MovieService

HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 4096

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


class MovieServer:
    """Сетевой слой: общение с клиентами через TCP-сокет."""

    def __init__(self, service: MovieService, host: str = HOST, port: int = PORT) -> None:
        self.service = service
        self.host = host
        self.port = port
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._socket: socket.socket | None = None

    # --- диспетчер команд ---
    def _handle_request(self, request: dict) -> dict:
        if not isinstance(request.get("command"), str) or "data" not in request:
            raise ProtocolError("Запрос должен содержать поля command и data")
        command = request.get("command")
        data = request.get("data") or {}
        if command == "list":
            movies = self.service.list_movies()
            return make_response("ok", [m.to_dict() for m in movies])
        if command == "get":
            mid = int(data["id"])
            return make_response("ok", self.service.get_movie(mid).to_dict())
        if command == "create":
            movie = self.service.create_movie(data)
            return make_response("ok", movie.to_dict())
        if command == "update":
            mid = int(data.pop("id"))
            movie = self.service.update_movie(mid, data)
            return make_response("ok", movie.to_dict())
        if command == "delete":
            mid = int(data["id"])
            self.service.delete_movie(mid)
            return make_response("ok", {"deleted": mid})
        if command == "by_genre":
            movies = self.service.find_by_genre(str(data["genre"]))
            return make_response("ok", [m.to_dict() for m in movies])
        raise ProtocolError(f"Неизвестная команда: {command}")

    def _serve_client(self, conn: socket.socket, address) -> None:
        logging.info("Client connected: %s", address)
        buffer = ""
        try:
            conn.settimeout(30)
            while True:
                chunk = conn.recv(BUFFER_SIZE)
                if not chunk:
                    break  # клиент закрыл соединение
                buffer += chunk.decode("utf-8", errors="replace")
                messages, buffer = decode_messages(buffer)
                for message in messages:
                    logging.info("Command: %s", message.get("command"))
                    try:
                        response = self._handle_request(message)
                        logging.info("Command %s success", message.get("command"))
                    except KeyError as exc:
                        logging.warning("Missing field: %s", exc)
                        response = make_response("error", error=f"Отсутствует поле: {exc}")
                    except (ValueError, TypeError) as exc:
                        logging.warning("Bad request: %s", exc)
                        response = make_response("error", error=str(exc))
                    except (CinemaError, ProtocolError) as exc:
                        logging.warning("Domain error: %s", exc)
                        response = make_response("error", error=str(exc))
                    except Exception as exc:  # внутренняя ошибка
                        logging.exception("Internal error")
                        response = make_response("error", error="Внутренняя ошибка сервера")
                    conn.sendall(encode_message(response))
        except socket.timeout:
            logging.info("Client %s timeout", address)
        except (ConnectionResetError, BrokenPipeError):
            logging.info("Client %s connection lost", address)
        finally:
            conn.close()
            logging.info("Client disconnected: %s", address)

    def run(self, stop_event=None) -> None:
        """Запускает сервер и принимает клиентов в цикле.

        stop_event (threading.Event, опционально) позволяет корректно
        остановить сервер из другого потока (используется в тестах).
        """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket = server
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.settimeout(0.5)  # периодическая проверка stop_event
        server.bind((self.host, self.port))
        server.listen()
        logging.info("Server started on %s:%s", self.host, self.port)
        try:
            while True:
                if stop_event is not None and stop_event.is_set():
                    logging.info("Server stop requested")
                    break
                try:
                    conn, address = server.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break
                self._executor.submit(self._serve_client, conn, address)
        except KeyboardInterrupt:
            logging.info("Server stopped")
        finally:
            server.close()


def seed(repository: MovieRepository) -> None:
    """Заполняет репозиторий демонстрационными данными."""
    demo = [
        {"title": "Начало", "director": "Кристофер Нолан", "genre": "фантастика",
         "year": 2010, "duration_min": 148, "rating": 8.8},
        {"title": "Матрица", "director": "Лана и Лилли Вачовски", "genre": "фантастика",
         "year": 1999, "duration_min": 136, "rating": 8.7},
        {"title": "Криминальное чтиво", "director": "Квентин Тарантино", "genre": "криминал",
         "year": 1994, "duration_min": 154, "rating": 8.9},
        {"title": "Зелёная миля", "director": "Фрэнк Дарабонт", "genre": "драма",
         "year": 1999, "duration_min": 189, "rating": 9.1},
        {"title": "Достучаться до небес", "director": "Томас Ян", "genre": "комедия",
         "year": 1997, "duration_min": 87, "rating": 8.0},
        {"title": "Бойцовский клуб", "director": "Дэвид Финчер", "genre": "драма",
         "year": 1999, "duration_min": 139, "rating": 8.4},
    ]
    for item in demo:
        repository.add(Movie.from_dict({**item, "id": 0}))


if __name__ == "__main__":
    repo = MovieRepository()
    seed(repo)
    MovieServer(MovieService(repo)).run()