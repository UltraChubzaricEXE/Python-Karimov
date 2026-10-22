"""Pydantic-схемы для API клиентов фитнес-центра (ЛР14, вариант 8)."""
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ClientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    age: int = Field(ge=1, le=129)
    membership: str = Field(default="месячный")
    membership_status: str = Field(default="активен")
    goals: list[str] = Field(default_factory=list)
    trainer: str = Field(default="", max_length=120)
    registered_at: str = Field(default="")

    @field_validator("membership")
    @classmethod
    def _valid_membership(cls, v: str) -> str:
        if v not in ("разовый", "месячный", "годовой"):
            raise ValueError("Допустимые типы абонемента: разовый, месячный, годовой")
        return v

    @field_validator("membership_status")
    @classmethod
    def _valid_status(cls, v: str) -> str:
        if v not in ("активен", "истёк", "заморожен", "отменён"):
            raise ValueError("Допустимые статусы: активен, истёк, заморожен, отменён")
        return v


class ClientUpdate(BaseModel):
    """Частичное обновление: все поля необязательны."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    age: Optional[int] = Field(default=None, ge=1, le=129)
    membership: Optional[str] = None
    membership_status: Optional[str] = None
    goals: Optional[list[str]] = None
    trainer: Optional[str] = None
    registered_at: Optional[str] = None

    @field_validator("membership")
    @classmethod
    def _valid_membership(cls, v):
        if v is not None and v not in ("разовый", "месячный", "годовой"):
            raise ValueError("Недопустимый тип абонемента")
        return v

    @field_validator("membership_status")
    @classmethod
    def _valid_status(cls, v):
        if v is not None and v not in ("активен", "истёк", "заморожен", "отменён"):
            raise ValueError("Недопустимый статус")
        return v


class ClientResponse(BaseModel):
    id: int
    name: str
    age: int
    membership: str
    membership_status: str
    goals: list[str]
    trainer: str
    registered_at: str

    @classmethod
    def from_client(cls, client) -> "ClientResponse":
        return cls(**client.to_dict())


class ClientsListResponse(BaseModel):
    items: list[ClientResponse]
    total: int


class ClientListParams(BaseModel):
    """Параметры фильтрации, сортировки и пагинации."""
    status: Optional[str] = None
    membership: Optional[str] = None
    sort: Optional[str] = None
    order: str = "asc"
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)