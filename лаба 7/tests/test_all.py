# -*- coding: utf-8 -*-
"""Автоматические тесты ЛР7: отрефакторенная SOLID-архитектура фитнес-центра."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from entities import MembershipStatus, MembershipType
from infrastructure import (ConsoleNotifier, FileNotifier, InMemoryRepository)
from pricing import DiscountPricing, FamilyPricing, StandardPricing, price_for
from report import ReportGenerator
from service import DomainError, FitnessService


class FakeNotifier:
    """Тестовая заглушка уведомлений (не зависит от консоли)."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def notify(self, message: str) -> None:
        self.messages.append(message)


@pytest.fixture()
def service():
    repo = InMemoryRepository()
    notifier = FakeNotifier()
    svc = FitnessService(repo, notifier, pricing=StandardPricing())
    svc.add_trainer("Мария", "фитнес", 1200)
    svc.register_client("Иван Иванов", "+79151112233")
    return svc, repo, notifier


# ---------- SRP / DIP: сервис получает зависимости через конструктор ----------
def test_service_depends_on_abstractions():
    repo = InMemoryRepository()
    svc = FitnessService(repo, FakeNotifier())
    # сервис не знает реализацию репозитория - он зависит только от интерфейса
    assert svc.repository is repo


def test_notifier_is_called(service):
    svc, _, notifier = service
    svc.register_client("Павел", "+7")
    assert any("Павел" in m for m in notifier.messages)


# ---------- OCP: стратегии ценообразования ----------
def test_standard_pricing_default():
    assert price_for(MembershipType.SINGLE, StandardPricing()) == 600.0
    assert price_for(MembershipType.MONTHLY, StandardPricing()) == 3500.0
    assert price_for(MembershipType.YEARLY, StandardPricing()) == 32000.0


def test_discount_pricing():
    assert price_for(MembershipType.YEARLY, DiscountPricing(10)) == 28800.0
    assert price_for(MembershipType.MONTHLY, DiscountPricing(50)) == 1750.0


def test_family_pricing():
    assert price_for(MembershipType.MONTHLY, FamilyPricing()) == 3200.0


def test_switch_pricing_without_service_change(service):
    svc, _, _ = service
    m1 = svc.issue_membership(1, MembershipType.MONTHLY)
    assert m1.price == 3500.0  # стандартная
    svc.set_pricing(DiscountPricing(20))
    m2 = svc.issue_membership(1, MembershipType.MONTHLY)
    assert m2.price == 2800.0  # скидка - без изменения кода сервиса OCP


# ---------- Бизнес-операции ----------
def test_book_training(service):
    svc, _, _ = service
    m = svc.issue_membership(1, MembershipType.MONTHLY)
    tr = svc.book_training(m.id, 1, "2024-10-10 10:00")
    assert tr.membership_id == m.id
    assert tr.trainer_id == 1


def test_book_training_on_frozen_membership(service):
    svc, _, _ = service
    m = svc.issue_membership(1, MembershipType.MONTHLY)
    svc.freeze_membership(m.id)
    with pytest.raises(DomainError):
        svc.book_training(m.id, 1, "2024-10-10 10:00")


def test_cancel_training_is_idempotent_guard(service):
    svc, _, _ = service
    m = svc.issue_membership(1, MembershipType.MONTHLY)
    tr = svc.book_training(m.id, 1, "2024-10-11 10:00")
    svc.cancel_training(tr.id)
    with pytest.raises(DomainError):
        svc.cancel_training(tr.id)


def test_freeze_only_active(service):
    svc, _, _ = service
    m = svc.issue_membership(1, MembershipType.YEARLY)
    svc.freeze_membership(m.id)
    with pytest.raises(DomainError):
        svc.freeze_membership(m.id)


def test_client_not_found(service):
    svc, _, _ = service
    with pytest.raises(DomainError):
        svc.issue_membership(999, MembershipType.SINGLE)


# ---------- LSP / DIP: две реализации Notifier и Repository ----------
def test_file_notifier_lsp(tmp_path):
    path = tmp_path / "n.log"
    nf = FileNotifier(str(path))
    nf.notify("тест")
    assert "тест" in path.read_text(encoding="utf-8")


def test_two_repository_implementations_same_interface():
    # LSP: вторая реализация используется идентично интерфейсу
    repo_a = InMemoryRepository()
    svc_a = FitnessService(repo_a, FakeNotifier())
    c = svc_a.register_client("Тест", "+7")
    assert repo_a.get_client(c.id) is not None


# ---------- SRP: генератор отчёта ----------
def test_report_generator(service):
    svc, repo, _ = service
    svc.issue_membership(1, MembershipType.YEARLY)
    report = ReportGenerator(repo).generate()
    assert "Всего абонементов: 1" in report
    assert "Выручка" in report


# ---------- ConsoleNotifier (реализация Notifier) ----------
def test_console_notifier_implements_protocol():
    nf = ConsoleNotifier()
    assert callable(nf.notify)