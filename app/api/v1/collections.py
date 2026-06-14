from fastapi import APIRouter

from app.dependencies.auth import CurrentUser
from app.repositories.collection_repository import CollectionRepository, UserCollectionProgressRepository
from app.repositories.visit_repository import VisitRepository
from app.schemas.collection import CollectionProgressResponse
from app.services.collection_service import CollectionService

router = APIRouter(prefix="/collections", tags=["Collections"])


def _get_collection_service() -> CollectionService:
    return CollectionService(
        collection_repo=CollectionRepository(),
        progress_repo=UserCollectionProgressRepository(),
        visit_repo=VisitRepository(),
    )


@router.get("", response_model=list[CollectionProgressResponse])
async def get_collections(current_user: CurrentUser):
    svc = _get_collection_service()
    return await svc.get_all_with_progress(str(current_user.id))
