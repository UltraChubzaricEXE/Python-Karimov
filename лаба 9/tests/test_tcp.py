# -*- coding: utf-8 -*-
"""Интеграционный тест ЛР9: реальный TCP-обмен клиент <-> сервер.

Проверяет полную цепочку Client -> TCP -> Server -> Service -> Repository.
"""
import socket
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from protocol import decode_messages, encode_message
from repository import MovieRepository
from server import MovieServer, seed
from service import MovieService

HOST, PORT = "127.0.0.1", 0  # порт 0 -> ОС выберет свободный


def test_full_tcp_roundtrip():
    repo = MovieRepository()
    seed(repo)
    server = MovieServer(MovieService(repo), HOST, PORT)
    # узнаём реально занятый порт
    sock_for_bind = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_for_bind.bind((HOST, 0))
    real_port = sock_for_bind.getsockname()[1]
    sock_for_bind.close()

    server.port = real_port
    server.host = HOST
    stop = threading.Event()
    thread = threading.Thread(target=server.run, kwargs={"stop_event": stop}, daemon=True)
    thread.start()
    time.sleep(0.3)

    errors = []

    def try_connect():
        attempts = 0
        while attempts < 50:
            try:
                s = socket.create_connection((HOST, real_port), timeout=2)
                return s
            except OSError:
                time.sleep(0.1)
                attempts += 1
        raise RuntimeError("Server not available")

    try:
        # --- запрос list ---
        s = try_connect()
        s.sendall(encode_message({"command": "list", "data": {}}))
        buf = _read_until_newline(s)
        msgs, _ = decode_messages(buf)
        assert msgs[0]["status"] == "ok"
        assert len(msgs[0]["data"]) >= 5
        s.close()

        # --- запрос by_genre ---
        s = try_connect()
        s.sendall(encode_message({"command": "by_genre", "data": {"genre": "фантастика"}}))
        buf = _read_until_newline(s)
        msgs, _ = decode_messages(buf)
        assert msgs[0]["status"] == "ok"
        assert all(m["genre"] == "фантастика" for m in msgs[0]["data"])
        s.close()

        # --- запрос create ---
        s = try_connect()
        new = {"title": "Дюна", "director": "Дени Вильнёв", "genre": "фантастика",
               "year": 2021, "duration_min": 155, "rating": 8.0}
        s.sendall(encode_message({"command": "create", "data": new}))
        buf = _read_until_newline(s)
        msgs, _ = decode_messages(buf)
        assert msgs[0]["status"] == "ok"
        created_id = msgs[0]["data"]["id"]
        s.close()

        # --- запрос get ---
        s = try_connect()
        s.sendall(encode_message({"command": "get", "data": {"id": created_id}}))
        buf = _read_until_newline(s)
        msgs, _ = decode_messages(buf)
        assert msgs[0]["data"]["title"] == "Дюна"
        s.close()

        # --- запрос delete и повторный get -> error ---
        s = try_connect()
        s.sendall(encode_message({"command": "delete", "data": {"id": created_id}}))
        buf = _read_until_newline(s)
        msgs, _ = decode_messages(buf)
        assert msgs[0]["status"] == "ok"
        s.close()

        s = try_connect()
        s.sendall(encode_message({"command": "get", "data": {"id": created_id}}))
        buf = _read_until_newline(s)
        msgs, _ = decode_messages(buf)
        assert msgs[0]["status"] == "error"
        s.close()

        # --- неизвестная команда -> error ---
        s = try_connect()
        s.sendall(encode_message({"command": "nope", "data": {}}))
        buf = _read_until_newline(s)
        msgs, _ = decode_messages(buf)
        assert msgs[0]["status"] == "error"
        s.close()

    except Exception as exc:  # pragma: no cover
        errors.append(exc)
    finally:
        stop.set()
        thread.join(timeout=5)

    if errors:
        raise errors[0]


def _read_until_newline(sock: socket.socket, timeout: float = 5.0) -> str:
    sock.settimeout(timeout)
    buffer = ""
    while "\n" not in buffer:
        chunk = sock.recv(4096).decode("utf-8", errors="replace")
        if not chunk:
            break
        buffer += chunk
    return buffer