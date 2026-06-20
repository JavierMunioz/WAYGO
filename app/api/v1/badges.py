import asyncio

from fastapi import APIRouter, BackgroundTasks, status

from app.dependencies.auth import CurrentUser, SuperUser
from app.models.badge import Badge, BadgeRequirement, UserBadge
from app.models.user import User
from app.models.place import Place as PlaceModel
from app.repositories.badge_repository import BadgeRepository, BadgeRequirementRepository, UserBadgeRepository
from app.repositories.visit_repository import VisitRepository
from app.schemas.badge import (
    BadgeDetailResponse,
    BadgePlaceProgress,
    BadgeRequirementResponse,
    BadgeResponse,
    BadgeWithProgressResponse,
    CreateBadgeRequest,
    UpdateBadgeRequest,
)
from app.services.badge_service import BadgeService
from app.utils.slug import slugify

router = APIRouter(prefix="/badges", tags=["Badges"])


def _get_badge_service() -> BadgeService:
    return BadgeService(
        badge_repo=BadgeRepository(),
        badge_req_repo=BadgeRequirementRepository(),
        user_badge_repo=UserBadgeRepository(),
        visit_repo=VisitRepository(),
    )


@router.get("", response_model=list[BadgeWithProgressResponse])
async def get_badges(current_user: CurrentUser):
    svc = _get_badge_service()
    return await svc.get_all_badges_with_progress(str(current_user.id))


@router.get("/{badge_id}/places", response_model=BadgeDetailResponse)
async def get_badge_detail(badge_id: str, current_user: CurrentUser):
    """Returns badge info + required places with visited status for the current user."""
    badge = await Badge.get(badge_id)
    if not badge:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Badge not found")

    user_id = str(current_user.id)
    visit_repo = VisitRepository()
    visited_ids = set(await visit_repo.get_user_visited_place_ids(user_id))

    req = await BadgeRequirement.find_one(BadgeRequirement.badge_id == badge_id)
    place_ids = req.place_ids if req else []

    # Fetch all required places in parallel
    place_docs = []
    if place_ids:
        place_docs = await asyncio.gather(
            *[PlaceModel.get(pid) for pid in place_ids],
            return_exceptions=True,
        )

    places_progress: list[BadgePlaceProgress] = []
    for doc in place_docs:
        if doc is None or isinstance(doc, Exception):
            continue
        places_progress.append(
            BadgePlaceProgress(
                place_id=str(doc.id),
                name=doc.name,
                city=doc.city,
                country=doc.country,
                slug=doc.slug,
                cover_image=doc.cover_image,
                visited=str(doc.id) in visited_ids,
            )
        )

    required_count = len(place_ids)
    visited_count = sum(1 for p in places_progress if p.visited)
    progress_pct = (visited_count / required_count * 100) if required_count > 0 else 0

    user_badge_repo = UserBadgeRepository()
    earned_ids = await user_badge_repo.get_user_badge_ids(user_id)

    return BadgeDetailResponse(
        id=badge_id,
        name=badge.name,
        slug=badge.slug,
        description=badge.description,
        image_url=badge.image_url,
        points=badge.points,
        city=badge.city,
        country=badge.country,
        level=badge.level,
        required_places=required_count,
        visited_places=visited_count,
        progress_pct=round(progress_pct, 1),
        completed=badge_id in earned_ids,
        places=places_progress,
    )


# ── Admin endpoints ────────────────────────────────────────────────────────────

@router.get("/admin/all", response_model=list[BadgeResponse])
async def admin_list_badges(current_user: SuperUser):
    badges = await Badge.find_all().to_list()
    return [_badge_to_response(b) for b in badges]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=BadgeResponse)
async def admin_create_badge(data: CreateBadgeRequest, background_tasks: BackgroundTasks, current_user: SuperUser):
    slug = slugify(data.name)
    existing = await Badge.find_one(Badge.slug == slug)
    if existing:
        slug = f"{slug}-{str(existing.id)[:6]}"

    badge = Badge(
        name=data.name,
        slug=slug,
        description=data.description,
        image_url=data.image_url,
        points=data.points,
        city=data.city,
        country=data.country,
        level=data.level,
    )
    await badge.save()

    badge_id = str(badge.id)
    if data.place_ids:
        req = BadgeRequirement(badge_id=badge_id, place_ids=data.place_ids)
        await req.save()
        background_tasks.add_task(_backfill_badge_for_existing_users, badge_id, data.place_ids)

    return _badge_to_response(badge)


@router.patch("/{badge_id}", response_model=BadgeResponse)
async def admin_update_badge(badge_id: str, data: UpdateBadgeRequest, background_tasks: BackgroundTasks, current_user: SuperUser):
    badge = await Badge.get(badge_id)
    if not badge:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Badge not found")

    update = data.model_dump(exclude_none=True, exclude={"place_ids"})
    if update:
        await badge.set(update)
        await badge.sync()

    if data.place_ids is not None:
        req = await BadgeRequirement.find_one(BadgeRequirement.badge_id == badge_id)
        if req:
            await req.set({BadgeRequirement.place_ids: data.place_ids})
        else:
            await BadgeRequirement(badge_id=badge_id, place_ids=data.place_ids).save()
        background_tasks.add_task(_backfill_badge_for_existing_users, badge_id, data.place_ids)

    return _badge_to_response(badge)


@router.delete("/{badge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_badge(badge_id: str, current_user: SuperUser):
    badge = await Badge.get(badge_id)
    if not badge:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Badge not found")

    req = await BadgeRequirement.find_one(BadgeRequirement.badge_id == badge_id)
    if req:
        await req.delete()

    user_badges = await UserBadge.find(UserBadge.badge_id == badge_id).to_list()
    for ub in user_badges:
        await ub.delete()

    await badge.delete()


@router.get("/{badge_id}/requirements", response_model=BadgeRequirementResponse)
async def admin_get_requirements(badge_id: str, current_user: SuperUser):
    req = await BadgeRequirement.find_one(BadgeRequirement.badge_id == badge_id)
    return BadgeRequirementResponse(
        badge_id=badge_id,
        place_ids=req.place_ids if req else [],
    )


async def _backfill_badge_for_existing_users(badge_id: str, place_ids: list[str]) -> None:
    """Award badge + points + notification to users who already qualify."""
    if not place_ids:
        return

    badge = await Badge.get(badge_id)
    if not badge:
        return

    from app.models.notification import Notification
    from app.repositories.notification_repository import NotificationRepository
    from app.repositories.stats_repository import StatsRepository
    from app.repositories.user_repository import UserRepository
    from app.services.notification_service import NotificationService
    from app.services.points_service import PointsService

    points_svc = PointsService(user_repo=UserRepository(), stats_repo=StatsRepository())
    notification_svc = NotificationService(NotificationRepository())

    required = set(place_ids)
    visit_repo = VisitRepository()
    user_badge_repo = UserBadgeRepository()

    all_users = await User.find_all().to_list()
    for user in all_users:
        user_id = str(user.id)
        already_earned = await user_badge_repo.has_badge(user_id, badge_id)
        if already_earned:
            continue
        visited_ids = set(await visit_repo.get_user_visited_place_ids(user_id))
        if required.issubset(visited_ids):
            await UserBadge(user_id=user_id, badge_id=badge_id).save()
            await points_svc.award_badge_earned(user_id, badge.points)
            await notification_svc.notify_new_badge(user_id, badge.name, badge_id)


def _badge_to_response(b: Badge) -> BadgeResponse:
    return BadgeResponse(
        id=str(b.id),
        name=b.name,
        slug=b.slug,
        description=b.description,
        image_url=b.image_url,
        points=b.points,
        city=b.city,
        country=b.country,
        level=b.level,
    )
