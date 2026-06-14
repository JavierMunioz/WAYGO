from app.repositories.collection_repository import CollectionRepository, UserCollectionProgressRepository
from app.repositories.visit_repository import VisitRepository
from app.schemas.collection import CollectionProgressResponse


class CollectionService:
    def __init__(
        self,
        collection_repo: CollectionRepository,
        progress_repo: UserCollectionProgressRepository,
        visit_repo: VisitRepository,
    ):
        self._collection_repo = collection_repo
        self._progress_repo = progress_repo
        self._visit_repo = visit_repo

    async def get_all_with_progress(self, user_id: str) -> list[CollectionProgressResponse]:
        collections = await self._collection_repo.get_all_active()
        visited_ids = set(await self._visit_repo.get_user_visited_place_ids(user_id))
        progress_map = {
            p.collection_id: p
            for p in await self._progress_repo.get_all_user_progress(user_id)
        }

        result = []
        for col in collections:
            col_id = str(col.id)
            required = set(col.place_ids)
            visited_in_col = visited_ids.intersection(required)
            total = len(required)
            visited_count = len(visited_in_col)
            progress_pct = (visited_count / total * 100) if total > 0 else 0
            progress = progress_map.get(col_id)

            result.append(
                CollectionProgressResponse(
                    id=col_id,
                    name=col.name,
                    slug=col.slug,
                    description=col.description,
                    cover_image=col.cover_image,
                    points=col.points,
                    total_places=total,
                    visited_places=visited_count,
                    progress_pct=round(progress_pct, 1),
                    completed=progress.completed if progress else False,
                    completed_at=progress.completed_at if progress else None,
                )
            )
        return result
