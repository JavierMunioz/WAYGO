from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.dependencies.auth import CurrentUser
from app.dependencies.pagination import PaginationParams
from app.repositories.badge_repository import BadgeRepository, BadgeRequirementRepository, UserBadgeRepository
from app.repositories.collection_repository import CollectionRepository, UserCollectionProgressRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.stats_repository import StatsRepository
from app.repositories.user_repository import UserRepository
from app.repositories.visit_repository import VisitRepository
from app.schemas.visit import ValidateVisitRequest, VisitResponse
from app.services.achievement_service import AchievementService
from app.services.notification_service import NotificationService
from app.services.points_service import PointsService
from app.services.visit_service import VisitService

router = APIRouter(prefix="/visits", tags=["Visits"])


def _get_visit_service() -> VisitService:
    return VisitService(
        visit_repo=VisitRepository(),
        place_repo=PlaceRepository(),
        user_repo=UserRepository(),
    )


def _get_achievement_service() -> AchievementService:
    notification_svc = NotificationService(NotificationRepository())
    points_svc = PointsService(UserRepository(), StatsRepository())
    return AchievementService(
        visit_repo=VisitRepository(),
        badge_repo=BadgeRepository(),
        badge_req_repo=BadgeRequirementRepository(),
        user_badge_repo=UserBadgeRepository(),
        collection_repo=CollectionRepository(),
        collection_progress_repo=UserCollectionProgressRepository(),
        user_repo=UserRepository(),
        points_svc=points_svc,
        notification_svc=notification_svc,
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=VisitResponse)
async def validate_visit(data: ValidateVisitRequest, background_tasks: BackgroundTasks, current_user: CurrentUser):
    visit_svc = _get_visit_service()
    visit, is_new = await visit_svc.validate_visit(str(current_user.id), data)

    if is_new:
        achievement_svc = _get_achievement_service()
        background_tasks.add_task(achievement_svc.process_visit, str(current_user.id), data.place_id)

    return VisitResponse(
        id=str(visit.id),
        user_id=visit.user_id,
        place_id=visit.place_id,
        latitude=visit.latitude,
        longitude=visit.longitude,
        distance=visit.distance,
        verified=visit.verified,
        created_at=visit.created_at,
    )


@router.get("/me", response_model=list[VisitResponse])
async def get_my_visits(current_user: CurrentUser, pagination: PaginationParams = Depends()):
    svc = _get_visit_service()
    visits = await svc.get_user_visits(str(current_user.id), pagination.page, pagination.page_size)
    return [
        VisitResponse(
            id=str(v.id),
            user_id=v.user_id,
            place_id=v.place_id,
            latitude=v.latitude,
            longitude=v.longitude,
            distance=v.distance,
            verified=v.verified,
            created_at=v.created_at,
        )
        for v in visits
    ]
