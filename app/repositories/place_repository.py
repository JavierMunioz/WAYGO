from beanie.operators import Inc
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.core.constants import PlaceCategory
from app.models.place import Place
from app.repositories.base import BaseRepository


class PlaceRepository(BaseRepository[Place]):
    model = Place

    async def get_by_slug(self, slug: str) -> Place | None:
        return await Place.find_one(Place.slug == slug)

    async def find_nearby(
        self,
        longitude: float,
        latitude: float,
        radius_meters: float,
        category: PlaceCategory | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[dict]:
        pipeline: list[dict] = [
            {
                "$geoNear": {
                    "near": {"type": "Point", "coordinates": [longitude, latitude]},
                    "distanceField": "distance_meters",
                    "maxDistance": radius_meters,
                    "spherical": True,
                    "query": {"is_active": True} | ({"category": category} if category else {}),
                }
            },
            {"$sort": {"distance_meters": 1}},
            {"$skip": skip},
            {"$limit": limit},
        ]
        from app.database.mongodb import mongodb
        return await mongodb.db["places"].aggregate(pipeline).to_list(length=None)

    async def search_text(self, query: str, skip: int = 0, limit: int = 20) -> list[Place]:
        return (
            await Place.find({"$text": {"$search": query}, "is_active": True})
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def find_by_category(self, category: PlaceCategory, skip: int = 0, limit: int = 20) -> list[Place]:
        return await Place.find(Place.category == category, Place.is_active == True).skip(skip).limit(limit).to_list()

    async def find_by_country(self, country: str, skip: int = 0, limit: int = 20) -> list[Place]:
        return (
            await Place.find(Place.country == country, Place.is_active == True)
            .sort(-Place.total_visits)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def find_by_city(self, city: str, skip: int = 0, limit: int = 20) -> list[Place]:
        return (
            await Place.find(Place.city == city, Place.is_active == True)
            .sort(-Place.total_visits)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def increment_counter(self, place_id: str, field: str, amount: int = 1) -> None:
        await Place.find_one(Place.id == ObjectId(place_id)).update(Inc({field: amount}))

    async def get_places_by_ids(self, place_ids: list[str]) -> list[Place]:
        oid_list = [ObjectId(pid) for pid in place_ids]
        return await Place.find({"_id": {"$in": oid_list}}).to_list()
