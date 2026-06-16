from app.core.constants import FeedMode
from app.repositories.follow_repository import FollowRepository
from app.repositories.photo_repository import PhotoLikeRepository, PhotoRepository, PhotoSaveRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.user_repository import UserRepository
from app.schemas.photo import FeedItemResponse
from app.schemas.user import UserMiniResponse
from app.utils.pagination import compute_skip


class FeedService:
    def __init__(
        self,
        photo_repo: PhotoRepository,
        like_repo: PhotoLikeRepository,
        save_repo: PhotoSaveRepository,
        user_repo: UserRepository,
        place_repo: PlaceRepository,
        follow_repo: FollowRepository,
    ):
        self._photo_repo = photo_repo
        self._like_repo = like_repo
        self._save_repo = save_repo
        self._user_repo = user_repo
        self._place_repo = place_repo
        self._follow_repo = follow_repo

    async def get_feed(
        self,
        current_user_id: str,
        mode: FeedMode,
        page: int,
        page_size: int,
    ) -> list[FeedItemResponse]:
        skip = compute_skip(page, page_size)

        if mode == FeedMode.RECENT:
            raw_photos = await self._photo_repo.get_feed_recent(skip, page_size)
        elif mode == FeedMode.POPULAR:
            raw_photos = await self._photo_repo.get_feed_popular(skip, page_size)
        elif mode == FeedMode.TRENDING:
            raw_photos = await self._photo_repo.get_feed_trending(hours=48, skip=skip, limit=page_size)
        elif mode == FeedMode.FOLLOWING:
            following_ids = await self._follow_repo.get_following_ids(current_user_id)
            if not following_ids:
                return []
            raw_photos = await self._photo_repo.get_feed_following(following_ids, skip, page_size)
        else:
            raw_photos = await self._photo_repo.get_feed_recent(skip, page_size)

        return await self._enrich_photos(raw_photos, current_user_id)

    async def _enrich_photos(self, photos: list, current_user_id: str) -> list[FeedItemResponse]:
        if not photos:
            return []

        # Collect unique user_ids and place_ids for batch fetching
        from bson import ObjectId

        photo_dicts = []
        for p in photos:
            if hasattr(p, "model_dump"):
                d = p.model_dump()
                d["id"] = str(p.id)
            else:
                d = dict(p)
                if "_id" in d:
                    d["id"] = str(d.pop("_id"))
            photo_dicts.append(d)

        user_ids = list({p["user_id"] for p in photo_dicts})
        place_ids = list({p["place_id"] for p in photo_dicts})
        photo_ids = [p["id"] for p in photo_dicts]

        # Batch fetch users and places
        users_map: dict[str, any] = {}
        places_map: dict[str, any] = {}

        from app.models.user import User
        from app.models.place import Place

        for uid in user_ids:
            try:
                u = await self._user_repo.get_by_id(uid)
                users_map[uid] = u
            except Exception:
                pass

        for pid in place_ids:
            try:
                pl = await self._place_repo.get_by_id(pid)
                places_map[pid] = pl
            except Exception:
                pass

        # Batch check likes and saves
        liked_set: set[str] = set()
        for photo_id in photo_ids:
            if await self._like_repo.has_liked(current_user_id, photo_id):
                liked_set.add(photo_id)

        saved_set = await self._save_repo.get_saved_ids(current_user_id, photo_ids)

        result = []
        for photo_d in photo_dicts:
            photo_id = photo_d["id"]
            user = users_map.get(photo_d["user_id"])
            place = places_map.get(photo_d["place_id"])
            if not user or not place:
                continue

            result.append(
                FeedItemResponse(
                    id=photo_id,
                    image_url=photo_d["image_url"],
                    caption=photo_d.get("caption"),
                    likes_count=photo_d.get("likes_count", 0),
                    comments_count=photo_d.get("comments_count", 0),
                    created_at=photo_d["created_at"],
                    user=UserMiniResponse(
                        id=str(user.id),
                        username=user.username,
                        avatar_url=user.avatar_url,
                        points=user.points,
                    ),
                    place_name=place.name,
                    place_city=place.city,
                    place_id=str(place.id),
                    user_has_liked=photo_id in liked_set,
                    is_saved=photo_id in saved_set,
                )
            )

        return result
