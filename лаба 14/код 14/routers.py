"""REST-роутер клиентов фитнес-центра (ЛР14, вариант 8).

HTTP-слой не содержит бизнес-логики — маршруты делегируют работу сервису.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from repository import ClientRepository
from schemas import (ClientsListResponse, ClientCreate, ClientResponse,
                     ClientUpdate)
from service import ClientNotFoundError, ClientService


# Единый сервис и репозиторий на всё приложение (данные сохраняются между запросами).
_repository = ClientRepository()
_service = ClientService(_repository)


def _get_service() -> ClientService:
    return _service


router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=ClientsListResponse)
def list_clients(
    status_: str | None = Query(default=None, alias="status"),
    membership: str | None = None,
    sort: str | None = None,
    order: str = "asc",
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: ClientService = Depends(_get_service),
):
    items = service.list_clients(status=status_, membership=membership,
                                 sort=sort, order=order, limit=limit, offset=offset)
    return ClientsListResponse(
        items=[ClientResponse.from_client(c) for c in items],
        total=service.total(status=status_, membership=membership),
    )


@router.get("/search", response_model=list[ClientResponse])
def search_clients(q: str = Query(min_length=1),
                   service: ClientService = Depends(_get_service)):
    return [ClientResponse.from_client(c) for c in service.search(q)]


@router.get("/statistics")
def client_statistics(service: ClientService = Depends(_get_service)):
    return service.statistics()


@router.get("/active", response_model=list[ClientResponse])
def active_memberships(service: ClientService = Depends(_get_service)):
    return [ClientResponse.from_client(c) for c in service.active_memberships()]


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, service: ClientService = Depends(_get_service)):
    try:
        return ClientResponse.from_client(service.get_client(client_id))
    except ClientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(payload: ClientCreate, service: ClientService = Depends(_get_service)):
    client = service.create_client(payload.model_dump())
    return ClientResponse.from_client(client)


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, payload: ClientCreate,
                  service: ClientService = Depends(_get_service)):
    try:
        client = service.update_client(client_id, payload.model_dump())
        return ClientResponse.from_client(client)
    except ClientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/{client_id}", response_model=ClientResponse)
def patch_client(client_id: int, payload: ClientUpdate,
                 service: ClientService = Depends(_get_service)):
    try:
        client = service.update_client(client_id, payload.model_dump(exclude_unset=True))
        return ClientResponse.from_client(client)
    except ClientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, service: ClientService = Depends(_get_service)):
    try:
        service.delete_client(client_id)
    except ClientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return None