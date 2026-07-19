import re
from datetime import UTC, datetime

from pymongo import UpdateOne

from app.models.hotelbeds_destination import HotelbedsDestination
from app.repositories.base import BaseRepository


class HotelbedsDestinationRepository(BaseRepository[HotelbedsDestination]):
    model = HotelbedsDestination

    async def search_by_name(self, query: str, limit: int = 8) -> list[HotelbedsDestination]:
        pattern = re.escape(query.strip())
        return (
            await HotelbedsDestination.find({"name": {"$regex": pattern, "$options": "i"}})
            .limit(limit)
            .to_list()
        )

    async def get_by_code(self, code: str) -> HotelbedsDestination | None:
        return await HotelbedsDestination.find_one(HotelbedsDestination.code == code.upper())

    async def count_all(self) -> int:
        return await HotelbedsDestination.find({}).count()

    async def bulk_upsert(self, rows: list[dict]) -> int:
        """rows: [{code, name, country_code}] — upsert masivo por código."""
        if not rows:
            return 0
        now = datetime.now(UTC)
        ops = [
            UpdateOne(
                {"code": row["code"]},
                {"$set": {**row, "updated_at": now}},
                upsert=True,
            )
            for row in rows
        ]
        result = await HotelbedsDestination.get_motor_collection().bulk_write(ops, ordered=False)
        return result.upserted_count + result.modified_count
