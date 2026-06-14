from fastapi import APIRouter, status

from app.dependencies.auth import CurrentUser, SuperUser
from app.models.badge import Badge, BadgeRequirement
from app.repositories.badge_repository import BadgeRepository, BadgeRequirementRepository, UserBadgeRepository
from app.repositories.visit_repository import VisitRepository
from app.schemas.badge import (
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


# ── Admin endpoints ────────────────────────────────────────────────────────────

@router.get("/admin/all", response_model=list[BadgeResponse])
async def admin_list_badges(current_user: SuperUser):
    badges = await Badge.find_all().to_list()
    return [_badge_to_response(b) for b in badges]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=BadgeResponse)
async def admin_create_badge(data: CreateBadgeRequest, current_user: SuperUser):
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

    if data.place_ids:
        req = BadgeRequirement(badge_id=str(badge.id), place_ids=data.place_ids)
        await req.save()

    return _badge_to_response(badge)


@router.patch("/{badge_id}", response_model=BadgeResponse)
async def admin_update_badge(badge_id: str, data: UpdateBadgeRequest, current_user: SuperUser):
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

    return _badge_to_response(badge)


@router.get("/{badge_id}/requirements", response_model=BadgeRequirementResponse)
async def admin_get_requirements(badge_id: str, current_user: SuperUser):
    req = await BadgeRequirement.find_one(BadgeRequirement.badge_id == badge_id)
    return BadgeRequirementResponse(
        badge_id=badge_id,
        place_ids=req.place_ids if req else [],
    )


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
