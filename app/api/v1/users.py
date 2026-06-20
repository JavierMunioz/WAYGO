from fastapi import APIRouter, Depends, status

from app.dependencies.auth import CurrentUser, OptionalUser
from app.dependencies.pagination import PaginationParams
from app.models.badge import Badge, UserBadge
from app.repositories.badge_repository import UserBadgeRepository
from app.repositories.collection_repository import UserCollectionProgressRepository
from app.repositories.follow_repository import FollowRepository
from app.repositories.stats_repository import StatsRepository
from app.repositories.user_repository import UserRepository
from app.schemas.badge import BadgeResponse, UserBadgeResponse
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.user import UpdateProfileRequest, UserProfileResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def _get_user_service() -> UserService:
    return UserService(
        user_repo=UserRepository(),
        follow_repo=FollowRepository(),
        user_badge_repo=UserBadgeRepository(),
        collection_progress_repo=UserCollectionProgressRepository(),
        stats_repo=StatsRepository(),
    )


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(current_user: CurrentUser):
    svc = _get_user_service()
    return await svc.get_profile(str(current_user.id), str(current_user.id))


@router.patch("/me", response_model=UserProfileResponse)
async def update_my_profile(data: UpdateProfileRequest, current_user: CurrentUser):
    svc = _get_user_service()
    await svc.update_profile(str(current_user.id), data)
    return await svc.get_profile(str(current_user.id), str(current_user.id))


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(user_id: str, current_user: OptionalUser):
    svc = _get_user_service()
    viewer_id = str(current_user.id) if current_user else None
    return await svc.get_profile(user_id, viewer_id)


@router.post("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def follow_user(user_id: str, current_user: CurrentUser):
    from app.repositories.notification_repository import NotificationRepository
    from app.services.follow_service import FollowService
    from app.services.notification_service import NotificationService

    svc = FollowService(
        follow_repo=FollowRepository(),
        user_repo=UserRepository(),
        notification_svc=NotificationService(NotificationRepository()),
    )
    await svc.follow(str(current_user.id), user_id, current_user.username)


@router.delete("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_user(user_id: str, current_user: CurrentUser):
    from app.services.follow_service import FollowService
    from app.services.notification_service import NotificationService
    from app.repositories.notification_repository import NotificationRepository

    svc = FollowService(
        follow_repo=FollowRepository(),
        user_repo=UserRepository(),
        notification_svc=NotificationService(NotificationRepository()),
    )
    await svc.unfollow(str(current_user.id), user_id)


@router.get("/{user_id}/badges", response_model=list[UserBadgeResponse])
async def get_user_badges(user_id: str, current_user: OptionalUser):
    """Returns badges earned by a given user. Public endpoint."""
    user_badge_repo = UserBadgeRepository()
    user_badges = await user_badge_repo.get_user_badges(user_id)

    result = []
    for ub in user_badges:
        badge = await Badge.get(ub.badge_id)
        if badge and badge.is_active:
            result.append(
                UserBadgeResponse(
                    badge=BadgeResponse(
                        id=str(badge.id),
                        name=badge.name,
                        slug=badge.slug,
                        description=badge.description,
                        image_url=badge.image_url,
                        points=badge.points,
                        city=badge.city,
                        country=badge.country,
                        level=badge.level,
                    ),
                    obtained_at=ub.obtained_at,
                )
            )
    return result


@router.get("/{user_id}/followers")
async def get_followers(user_id: str, pagination: PaginationParams = Depends()):
    from app.services.follow_service import FollowService
    from app.services.notification_service import NotificationService
    from app.repositories.notification_repository import NotificationRepository

    svc = FollowService(
        follow_repo=FollowRepository(),
        user_repo=UserRepository(),
        notification_svc=NotificationService(NotificationRepository()),
    )
    follows = await svc.get_followers(user_id, pagination.page, pagination.page_size)
    user_repo = UserRepository()
    users = []
    for f in follows:
        try:
            u = await user_repo.get_by_id(f.follower_id)
            users.append({"id": str(u.id), "username": u.username, "avatar_url": u.avatar_url})
        except Exception:
            pass
    return users


@router.get("/{user_id}/following")
async def get_following(user_id: str, pagination: PaginationParams = Depends()):
    from app.services.follow_service import FollowService
    from app.services.notification_service import NotificationService
    from app.repositories.notification_repository import NotificationRepository

    svc = FollowService(
        follow_repo=FollowRepository(),
        user_repo=UserRepository(),
        notification_svc=NotificationService(NotificationRepository()),
    )
    follows = await svc.get_following(user_id, pagination.page, pagination.page_size)
    user_repo = UserRepository()
    users = []
    for f in follows:
        try:
            u = await user_repo.get_by_id(f.following_id)
            users.append({"id": str(u.id), "username": u.username, "avatar_url": u.avatar_url})
        except Exception:
            pass
    return users
