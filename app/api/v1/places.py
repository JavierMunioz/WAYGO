from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from app.core.constants import PlaceCategory
from app.dependencies.auth import CurrentUser, OptionalUser, SuperUser
from app.dependencies.pagination import PaginationParams
from app.repositories.photo_repository import PhotoRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.visit_repository import VisitRepository
from app.schemas.photo import PhotoResponse
from app.schemas.place import (
    CreatePlaceRequest,
    NearbyPlaceResponse,
    PlaceDetailResponse,
    PlaceResponse,
    UpdatePlaceRequest,
)
from app.services.place_service import PlaceService

router = APIRouter(prefix="/places", tags=["Places"])


def _get_place_service() -> PlaceService:
    return PlaceService(PlaceRepository())


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PlaceResponse)
async def create_place(data: CreatePlaceRequest, current_user: SuperUser):
    svc = _get_place_service()
    place = await svc.create_place(data)
    return _to_response(place)


@router.delete("/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_place(place_id: str, current_user: SuperUser):
    svc = _get_place_service()
    await svc.delete_place(place_id)


@router.post("/{place_id}/cover-image", response_model=PlaceResponse)
async def upload_place_cover(
    place_id: str,
    current_user: SuperUser,
    file: UploadFile = File(...),
):
    svc = _get_place_service()
    content = await file.read()
    place = await svc.upload_cover_image(place_id, content, file.content_type or "image/jpeg")
    return _to_response(place)


@router.get("/nearby", response_model=list[NearbyPlaceResponse])
async def get_nearby_places(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=5.0, ge=0.1, le=50.0),
    category: PlaceCategory | None = None,
    pagination: PaginationParams = Depends(),
):
    svc = _get_place_service()
    raw = await svc.find_nearby(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        category=category,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return [
        NearbyPlaceResponse(
            id=str(p.get("_id", p.get("id", ""))),
            name=p["name"],
            slug=p["slug"],
            description=p["description"],
            country=p["country"],
            city=p["city"],
            category=p["category"],
            cover_image=p.get("cover_image"),
            validation_radius=p["validation_radius"],
            location=p["location"],
            total_visits=p.get("total_visits", 0),
            total_photos=p.get("total_photos", 0),
            total_likes=p.get("total_likes", 0),
            distance_meters=round(p.get("distance_meters", 0), 1),
        )
        for p in raw
    ]


@router.get("/search", response_model=list[PlaceResponse])
async def search_places(
    q: str = Query(..., min_length=2),
    pagination: PaginationParams = Depends(),
):
    svc = _get_place_service()
    places = await svc.search(q, pagination.page, pagination.page_size)
    return [_to_response(p) for p in places]


@router.get("/{place_id}", response_model=PlaceDetailResponse)
async def get_place(place_id: str, current_user: OptionalUser):
    svc = _get_place_service()
    place = await svc.get_place(place_id)

    user_has_visited = False
    if current_user:
        visit_repo = VisitRepository()
        user_has_visited = await visit_repo.has_verified_visit(str(current_user.id), place_id)

    return PlaceDetailResponse(
        **_to_response(place).model_dump(),
        user_has_visited=user_has_visited,
    )


@router.get("/{place_id}/photos", response_model=list[PhotoResponse])
async def get_place_photos(
    place_id: str,
    pagination: PaginationParams = Depends(),
):
    repo = PhotoRepository()
    photos = await repo.get_place_photos(
        place_id=place_id,
        skip=(pagination.page - 1) * pagination.page_size,
        limit=pagination.page_size,
    )
    return [
        PhotoResponse(
            id=str(p.id),
            user_id=p.user_id,
            place_id=p.place_id,
            visit_id=p.visit_id,
            image_url=p.image_url,
            caption=p.caption,
            likes_count=p.likes_count,
            comments_count=p.comments_count,
            created_at=p.created_at,
        )
        for p in photos
    ]


@router.patch("/{place_id}", response_model=PlaceResponse)
async def update_place(place_id: str, data: UpdatePlaceRequest, current_user: SuperUser):
    svc = _get_place_service()
    place = await svc.update_place(place_id, data)
    return _to_response(place)


def _to_response(place) -> PlaceResponse:
    from app.schemas.place import GeoPointSchema
    return PlaceResponse(
        id=str(place.id),
        name=place.name,
        slug=place.slug,
        description=place.description,
        country=place.country,
        city=place.city,
        category=place.category,
        cover_image=place.cover_image,
        validation_radius=place.validation_radius,
        location=GeoPointSchema(
            type=place.location["type"],
            coordinates=place.location["coordinates"],
        ),
        total_visits=place.total_visits,
        total_photos=place.total_photos,
        total_likes=place.total_likes,
    )
