from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.models.destination import Destination
from app.models.place import Place
from app.repositories.destination_repository import DestinationRepository
from app.repositories.place_repository import PlaceRepository
from app.schemas.destination import CreateDestinationRequest, UpdateDestinationRequest
from app.utils.slug import slugify


class DestinationService:
    def __init__(self, destination_repo: DestinationRepository, place_repo: PlaceRepository):
        self._repo = destination_repo
        self._place_repo = place_repo

    async def create_destination(self, data: CreateDestinationRequest) -> Destination:
        existing = await self._repo.find_by_country_and_city(data.country, data.city)
        if existing:
            raise AlreadyExistsError(f"Destination '{data.city}, {data.country}' already exists")

        slug = slugify(f"{data.city}-{data.country}")
        base_slug = slug
        counter = 1
        while await self._repo.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        destination = Destination(
            name=data.name,
            slug=slug,
            country=data.country,
            city=data.city,
            description=data.description,
            cover_image=data.cover_image,
            timezone=data.timezone,
            currency=data.currency,
        )
        await destination.save()
        return destination

    async def get_destination(self, destination_id: str) -> Destination:
        return await self._repo.get_by_id(destination_id)

    async def get_by_slug(self, slug: str) -> Destination:
        destination = await self._repo.get_by_slug(slug)
        if not destination:
            raise NotFoundError(f"Destination '{slug}' not found")
        return destination

    async def list_destinations(
        self, page: int, page_size: int, country: str | None = None
    ) -> list[Destination]:
        from app.utils.pagination import compute_skip
        skip = compute_skip(page, page_size)
        if country:
            return await self._repo.list_by_country(country, skip=skip, limit=page_size)
        return await self._repo.list_active(skip=skip, limit=page_size)

    async def search(self, query: str, page: int, page_size: int) -> list[Destination]:
        from app.utils.pagination import compute_skip
        skip = compute_skip(page, page_size)
        return await self._repo.search_text(query, skip=skip, limit=page_size)

    async def update_destination(self, destination_id: str, data: UpdateDestinationRequest) -> Destination:
        destination = await self._repo.get_by_id(destination_id)
        update_data = data.model_dump(exclude_none=True)
        for key, val in update_data.items():
            setattr(destination, key, val)
        await destination.save()
        return destination

    async def delete_destination(self, destination_id: str) -> None:
        destination = await self._repo.get_by_id(destination_id)
        await destination.delete()

    async def get_places(self, destination_id: str, page: int, page_size: int) -> list[Place]:
        from app.utils.pagination import compute_skip
        destination = await self._repo.get_by_id(destination_id)
        skip = compute_skip(page, page_size)
        return await self._place_repo.find_by_country_and_city(
            destination.country, destination.city, skip=skip, limit=page_size
        )
