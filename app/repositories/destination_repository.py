from app.models.destination import Destination
from app.repositories.base import BaseRepository


class DestinationRepository(BaseRepository[Destination]):
    model = Destination

    async def get_by_slug(self, slug: str) -> Destination | None:
        return await Destination.find_one(Destination.slug == slug)

    async def find_by_country_and_city(self, country: str, city: str) -> Destination | None:
        return await Destination.find_one(Destination.country == country, Destination.city == city)

    async def search_text(self, query: str, skip: int = 0, limit: int = 20) -> list[Destination]:
        return (
            await Destination.find({"$text": {"$search": query}, "is_active": True})
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def list_active(self, skip: int = 0, limit: int = 20) -> list[Destination]:
        return (
            await Destination.find(Destination.is_active == True)
            .sort(Destination.name)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def list_by_country(self, country: str, skip: int = 0, limit: int = 20) -> list[Destination]:
        return (
            await Destination.find(Destination.country == country, Destination.is_active == True)
            .sort(Destination.name)
            .skip(skip)
            .limit(limit)
            .to_list()
        )
