from bson import ObjectId

from app.models.collection import Collection, UserCollectionProgress
from app.repositories.base import BaseRepository


class CollectionRepository(BaseRepository[Collection]):
    model = Collection

    async def get_by_slug(self, slug: str) -> Collection | None:
        return await Collection.find_one(Collection.slug == slug)

    async def get_all_active(self) -> list[Collection]:
        return await Collection.find(Collection.is_active == True).to_list()


class UserCollectionProgressRepository(BaseRepository[UserCollectionProgress]):
    model = UserCollectionProgress

    async def get_progress(self, user_id: str, collection_id: str) -> UserCollectionProgress | None:
        return await UserCollectionProgress.find_one(
            UserCollectionProgress.user_id == user_id,
            UserCollectionProgress.collection_id == collection_id,
        )

    async def get_all_user_progress(self, user_id: str) -> list[UserCollectionProgress]:
        return await UserCollectionProgress.find(UserCollectionProgress.user_id == user_id).to_list()

    async def get_completed_collections(self, user_id: str) -> list[UserCollectionProgress]:
        return await UserCollectionProgress.find(
            UserCollectionProgress.user_id == user_id,
            UserCollectionProgress.completed == True,
        ).to_list()

    async def upsert_progress(
        self,
        user_id: str,
        collection_id: str,
        visited_place_ids: list[str],
        completed: bool,
        completed_at=None,
    ) -> UserCollectionProgress:
        from datetime import UTC, datetime

        progress = await self.get_progress(user_id, collection_id)
        if progress:
            progress.visited_place_ids = visited_place_ids
            progress.completed = completed
            progress.completed_at = completed_at
            progress.updated_at = datetime.now(UTC)
            await progress.save()
        else:
            progress = UserCollectionProgress(
                user_id=user_id,
                collection_id=collection_id,
                visited_place_ids=visited_place_ids,
                completed=completed,
                completed_at=completed_at,
            )
            await progress.save()
        return progress
