from app.core.config import settings
from app.core.constants import ALLOWED_IMAGE_TYPES, MAX_PHOTO_SIZE_MB, PlaceCategory
from app.core.exceptions import AlreadyExistsError, NotFoundError, StorageError
from app.models.place import Place
from app.repositories.place_repository import PlaceRepository
from app.schemas.place import CreatePlaceRequest, UpdatePlaceRequest
from app.utils.slug import slugify
from app.utils.storage import store_file


class PlaceService:
    def __init__(self, place_repo: PlaceRepository):
        self._repo = place_repo

    async def create_place(self, data: CreatePlaceRequest) -> Place:
        slug = slugify(data.name)
        base_slug = slug
        counter = 1
        while await self._repo.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        place = Place(
            name=data.name,
            slug=slug,
            description=data.description,
            country=data.country,
            city=data.city,
            category=data.category,
            cover_image=data.cover_image,
            validation_radius=data.validation_radius,
            location={"type": "Point", "coordinates": [data.longitude, data.latitude]},
        )
        await place.save()
        return place

    async def get_place(self, place_id: str) -> Place:
        return await self._repo.get_by_id(place_id)

    async def get_by_slug(self, slug: str) -> Place:
        place = await self._repo.get_by_slug(slug)
        if not place:
            raise NotFoundError(f"Place '{slug}' not found")
        return place

    async def update_place(self, place_id: str, data: UpdatePlaceRequest) -> Place:
        place = await self._repo.get_by_id(place_id)
        update_data = data.model_dump(exclude_none=True)
        for key, val in update_data.items():
            setattr(place, key, val)
        await place.save()
        return place

    async def find_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        category: PlaceCategory | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> list[dict]:
        from app.utils.pagination import compute_skip
        radius_m = min(radius_km * 1000, settings.MAX_NEARBY_RADIUS_KM * 1000)
        skip = compute_skip(page, page_size)
        return await self._repo.find_nearby(
            longitude=longitude,
            latitude=latitude,
            radius_meters=radius_m,
            category=category,
            skip=skip,
            limit=page_size,
        )

    async def search(self, query: str, page: int, page_size: int) -> list[Place]:
        from app.utils.pagination import compute_skip
        skip = compute_skip(page, page_size)
        return await self._repo.search_text(query, skip=skip, limit=page_size)

    async def delete_place(self, place_id: str) -> None:
        place = await self._repo.get_by_id(place_id)
        await place.delete()

    async def upload_cover_image(self, place_id: str, content: bytes, content_type: str) -> Place:
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise StorageError(f"Tipo de imagen no soportado: {content_type}")
        if len(content) > MAX_PHOTO_SIZE_MB * 1024 * 1024:
            raise StorageError(f"La imagen supera el límite de {MAX_PHOTO_SIZE_MB}MB")
        url = await store_file(content, content_type)
        place = await self._repo.get_by_id(place_id)
        place.cover_image = url
        await place.save()
        return place

    async def list_by_city(self, city: str, page: int, page_size: int) -> list[Place]:
        from app.utils.pagination import compute_skip
        skip = compute_skip(page, page_size)
        return await self._repo.find_by_city(city, skip=skip, limit=page_size)
