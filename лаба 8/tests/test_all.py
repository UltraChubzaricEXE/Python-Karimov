# -*- coding: utf-8 -*-
"""Автоматические тесты ЛР8: паттерны (Factory, Strategy, Repository, Observer)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from factories import DiscountPricing, FamilyPricing, MembershipFactory, StandardPricing
from models import MembershipType
from observers import EventLogObserver, NotificationObserver, StatisticsObserver
from repositories import FileRepository, InMemoryRepository
from service import DomainError, FitnessService
from interfaces import Repository


@pytest.fixture()
def mem_repo():
    return InMemoryRepository()


@pytest.fixture()
def service(mem_repo):
    return FitnessService(mem_repo)


@pytest.fixture()
def observed_service(mem_repo):
    svc = FitnessService(mem_repo)
    svc.attach(EventLogObserver())
    svc.attach(NotificationObserver())
    svc.attach(StatisticsObserver())
    return svc


# ---------- Factory ----------
def test_factory_creates_correct_types():
    spec = MembershipFactory.create(MembershipType.MONTHLY)
    assert spec.mtype == MembershipType.MONTHLY


def test_factory_base_prices():
    assert MembershipFactory.create(MembershipType.SINGLE).price == 600.0
    assert MembershipFactory.create(MembershipType.MONTHLY).price == 3500.0
    assert MembershipFactory.create(MembershipType.YEARLY).price == 32000.0


def test_factory_with_strategy():
    spec = MembershipFactory.create(MembershipType.MONTHLY, DiscountPricing(10))
    assert spec.price == 3150.0


def test_factory_builds_membership():
    spec = MembershipFactory.create(MembershipType.YEARLY, FamilyPricing())
    m = spec.build(1)
    assert m.client_id == 1
    assert m.mtype == MembershipType.YEARLY


# ---------- Strategy ----------
def test_standard_pricing():
    assert StandardPricing().calculate(1000) == 1000


def test_discount_pricing():
    assert DiscountPricing(20).calculate(1000) == 800


def test_family_pricing():
    assert FamilyPricing().calculate(3500) == 3200


def test_switch_strategy_without_service_change(service):
    service.register_client("Иван", "+7")
    m1 = service.issue_membership(1, MembershipType.MONTHLY)
    assert m1.price == 3500.0
    service.set_pricing(DiscountPricing(50))
    m2 = service.issue_membership(1, MembershipType.MONTHLY)
    assert m2.price == 1750.0  # OCP/Strategy: сервис не менялся


# ---------- Repository ----------
def test_in_memory_repository(service):
    service.register_client("Иван", "+7")
    m = service.issue_membership(1, MembershipType.SINGLE)
    assert service.repository.get_membership(m.id) is m
    assert len(service.repository.all_memberships()) == 1


def test_file_repository_persists(tmp_path):
    path = tmp_path / "m.json"
    repo1 = FileRepository(str(path))
    svc1 = FitnessService(repo1)
    svc1.register_client("Иван", "+7")
    svc1.issue_membership(1, MembershipType.YEARLY)
    # новый репозиторий читает данные из файла (LSP/DIP)
    repo2 = FileRepository(str(path))
    assert len(repo2.all_memberships()) == 1
    assert repo2.all_memberships()[0].mtype == MembershipType.YEARLY


def test_repository_interchangeable():
    # LSP: обе реализации используют один интерфейс Repository
    for repo in (InMemoryRepository(), FileRepository("l8_test_tmp.json")):
        svc = FitnessService(repo)
        svc.register_client("Тест", "+7")
        svc.issue_membership(1, MembershipType.MONTHLY)
        assert len(repo.all_memberships()) == 1


# ---------- Observer ----------
def test_observer_notified_on_client_creation(observed_service):
    observed_service.register_client("Иван", "+7")
    logger = observed_service._observers[0]
    assert any(e == "client_created" for e, _ in logger.events)


def test_observer_notified_on_membership(observed_service):
    observed_service.register_client("Иван", "+7")
    observed_service.issue_membership(1, MembershipType.MONTHLY)
    notification = observed_service._observers[1]
    assert any("membership_created" in m for m in notification.messages)


def test_observer_statistics_counts(observed_service):
    observed_service.register_client("Иван", "+7")
    observed_service.issue_membership(1, MembershipType.SINGLE)
    observed_service.issue_membership(1, MembershipType.MONTHLY)
    stats = observed_service._observers[2]
    assert stats.counts["membership_created"] == 2
    assert stats.counts["client_created"] == 1


def test_observer_log_enables_undo_like_history(observed_service):
    # наблюдатель-журнал хранит историю событий (как история команд)
    observed_service.register_client("Иван", "+7")
    observed_service.issue_membership(1, MembershipType.SINGLE)
    logger = observed_service._observers[0]
    assert len(logger.events) == 2


# ---------- Бизнес-логика ----------
def test_domain_error_on_missing_membership(service):
    with pytest.raises(DomainError):
        service.freeze_membership(999)  # объект не найден


def test_freeze_only_active(service):
    service.register_client("Иван", "+7")
    m = service.issue_membership(1, MembershipType.MONTHLY)
    service.freeze_membership(m.id)
    with pytest.raises(DomainError):
        service.freeze_membership(m.id)


def test_register_client_validation(service):
    with pytest.raises(DomainError):
        service.register_client("  ")  # пустое имя