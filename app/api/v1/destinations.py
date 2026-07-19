from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import SuperUser
from app.dependencies.pagination import PaginationParams
from app.models.destination import Destination
from app.repositories.destination_repository import DestinationRepository
from app.repositories.place_repository import PlaceRepository
from app.schemas.destination import CreateDestinationRequest, DestinationResponse, UpdateDestinationRequest
from app.schemas.place import GeoPointSchema, PlaceResponse
from app.services.destination_service import DestinationService

router = APIRouter(prefix="/destinations", tags=["Destinations"])


def _get_destination_service() -> DestinationService:
    return DestinationService(DestinationRepository(), PlaceRepository())


@router.post("", status_code=status.HTTP_201_CREATED, response_model=DestinationResponse)
async def create_destination(data: CreateDestinationRequest, current_user: SuperUser):
    svc = _get_destination_service()
    destination = await svc.create_destination(data)
    return _to_response(destination)


@router.get("", response_model=list[DestinationResponse])
async def list_destinations(
    country: str | None = None,
    pagination: PaginationParams = Depends(),
):
    svc = _get_destination_service()
    destinations = await svc.list_destinations(pagination.page, pagination.page_size, country)
    return [_to_response(d) for d in destinations]


@router.get("/search", response_model=list[DestinationResponse])
async def search_destinations(
    q: str = Query(..., min_length=2),
    pagination: PaginationParams = Depends(),
):
    svc = _get_destination_service()
    destinations = await svc.search(q, pagination.page, pagination.page_size)
    return [_to_response(d) for d in destinations]


@router.get("/slug/{slug}", response_model=DestinationResponse)
async def get_destination_by_slug(slug: str):
    svc = _get_destination_service()
    destination = await svc.get_by_slug(slug)
    return _to_response(destination)


@router.get("/{destination_id}", response_model=DestinationResponse)
async def get_destination(destination_id: str):
    svc = _get_destination_service()
    destination = await svc.get_destination(destination_id)
    return _to_response(destination)


@router.get("/{destination_id}/places", response_model=list[PlaceResponse])
async def get_destination_places(destination_id: str, pagination: PaginationParams = Depends()):
    svc = _get_destination_service()
    places = await svc.get_places(destination_id, pagination.page, pagination.page_size)
    return [
        PlaceResponse(
            id=str(p.id),
            name=p.name,
            slug=p.slug,
            description=p.description,
            country=p.country,
            city=p.city,
            category=p.category,
            cover_image=p.cover_image,
            validation_radius=p.validation_radius,
            location=GeoPointSchema(type=p.location["type"], coordinates=p.location["coordinates"]),
            opening_hours=p.opening_hours,
            price_range=p.price_range,
            fun_fact=p.fun_fact,
            total_visits=p.total_visits,
            total_photos=p.total_photos,
            total_likes=p.total_likes,
        )
        for p in places
    ]


@router.patch("/{destination_id}", response_model=DestinationResponse)
async def update_destination(destination_id: str, data: UpdateDestinationRequest, current_user: SuperUser):
    svc = _get_destination_service()
    destination = await svc.update_destination(destination_id, data)
    return _to_response(destination)


@router.delete("/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_destination(destination_id: str, current_user: SuperUser):
    svc = _get_destination_service()
    await svc.delete_destination(destination_id)


def _to_response(destination: Destination) -> DestinationResponse:
    return DestinationResponse(
        id=str(destination.id),
        name=destination.name,
        slug=destination.slug,
        country=destination.country,
        city=destination.city,
        description=destination.description,
        cover_image=destination.cover_image,
        timezone=destination.timezone,
        currency=destination.currency,
        is_active=destination.is_active,
        created_at=destination.created_at,
        updated_at=destination.updated_at,
    )
