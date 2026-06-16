from bson import ObjectId
from beanie.operators import Inc

from app.models.photo import Photo, PhotoLike, PhotoSave
from app.repositories.base import BaseRepository


class PhotoRepository(BaseRepository[Photo]):
    model = Photo

    async def get_by_visit(self, visit_id: str) -> list[Photo]:
        return await Photo.find(Photo.visit_id == visit_id, Photo.is_active == True).to_list()

    async def get_user_photos(self, user_id: str, skip: int = 0, limit: int = 20) -> list[Photo]:
        return (
            await Photo.find(Photo.user_id == user_id, Photo.is_active == True)
            .sort(-Photo.created_at)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def get_place_photos(self, place_id: str, skip: int = 0, limit: int = 20) -> list[Photo]:
        return (
            await Photo.find(Photo.place_id == place_id, Photo.is_active == True)
            .sort(-Photo.created_at)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def get_feed_recent(self, skip: int, limit: int) -> list[Photo]:
        return (
            await Photo.find(Photo.is_active == True)
            .sort(-Photo.created_at)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def get_feed_popular(self, skip: int, limit: int) -> list[Photo]:
        return (
            await Photo.find(Photo.is_active == True)
            .sort(-Photo.likes_count)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def get_feed_trending(self, hours: int = 24, skip: int = 0, limit: int = 20) -> list[dict]:
        from datetime import UTC, datetime, timedelta
        from app.database.mongodb import mongodb

        since = datetime.now(UTC) - timedelta(hours=hours)
        pipeline = [
            {"$match": {"is_active": True, "created_at": {"$gte": since}}},
            {
                "$addFields": {
                    "trend_score": {
                        "$add": [
                            "$likes_count",
                            {"$multiply": ["$comments_count", 2]},
                        ]
                    }
                }
            },
            {"$sort": {"trend_score": -1}},
            {"$skip": skip},
            {"$limit": limit},
        ]
        return await mongodb.db["photos"].aggregate(pipeline).to_list(length=None)

    async def get_feed_following(self, following_ids: list[str], skip: int, limit: int) -> list[Photo]:
        return (
            await Photo.find({"user_id": {"$in": following_ids}, "is_active": True})
            .sort(-Photo.created_at)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def increment_likes(self, photo_id: str, amount: int = 1) -> None:
        await Photo.find_one(Photo.id == ObjectId(photo_id)).update(Inc({"likes_count": amount}))

    async def increment_comments(self, photo_id: str, amount: int = 1) -> None:
        await Photo.find_one(Photo.id == ObjectId(photo_id)).update(Inc({"comments_count": amount}))


class PhotoLikeRepository(BaseRepository[PhotoLike]):
    model = PhotoLike

    async def get_like(self, user_id: str, photo_id: str) -> PhotoLike | None:
        """Returns any like record (active or inactive) — used to check history."""
        return await PhotoLike.find_one(PhotoLike.user_id == user_id, PhotoLike.photo_id == photo_id)

    async def has_liked(self, user_id: str, photo_id: str) -> bool:
        """Returns True only if the current active like exists."""
        like = await self.get_like(user_id, photo_id)
        return like is not None and like.is_active

    async def get_photo_likers(self, photo_id: str, skip: int = 0, limit: int = 20) -> list[PhotoLike]:
        return (
            await PhotoLike.find(PhotoLike.photo_id == photo_id, PhotoLike.is_active == True)
            .sort(-PhotoLike.created_at)
            .skip(skip)
            .limit(limit)
            .to_list()
        )


class PhotoSaveRepository(BaseRepository[PhotoSave]):
    model = PhotoSave

    async def has_saved(self, user_id: str, photo_id: str) -> bool:
        return await PhotoSave.find_one(
            PhotoSave.user_id == user_id, PhotoSave.photo_id == photo_id
        ) is not None

    async def save(self, user_id: str, photo_id: str) -> None:
        if not await self.has_saved(user_id, photo_id):
            await PhotoSave(user_id=user_id, photo_id=photo_id).insert()

    async def unsave(self, user_id: str, photo_id: str) -> None:
        doc = await PhotoSave.find_one(
            PhotoSave.user_id == user_id, PhotoSave.photo_id == photo_id
        )
        if doc:
            await doc.delete()

    async def get_saved_ids(self, user_id: str, photo_ids: list[str]) -> set[str]:
        docs = await PhotoSave.find(
            PhotoSave.user_id == user_id,
            {"photo_id": {"$in": photo_ids}},
        ).to_list()
        return {d.photo_id for d in docs}
