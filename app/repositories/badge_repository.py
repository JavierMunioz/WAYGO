from bson import ObjectId

from app.models.badge import Badge, BadgeRequirement, UserBadge
from app.repositories.base import BaseRepository


class BadgeRepository(BaseRepository[Badge]):
    model = Badge

    async def get_by_slug(self, slug: str) -> Badge | None:
        return await Badge.find_one(Badge.slug == slug)

    async def get_all_active(self) -> list[Badge]:
        return await Badge.find(Badge.is_active == True).to_list()

    async def get_by_ids(self, badge_ids: list[str]) -> list[Badge]:
        oid_list = [ObjectId(bid) for bid in badge_ids]
        return await Badge.find({"_id": {"$in": oid_list}}).to_list()


class BadgeRequirementRepository(BaseRepository[BadgeRequirement]):
    model = BadgeRequirement

    async def get_by_badge_id(self, badge_id: str) -> BadgeRequirement | None:
        return await BadgeRequirement.find_one(BadgeRequirement.badge_id == badge_id)

    async def get_all(self) -> list[BadgeRequirement]:
        return await BadgeRequirement.find_all().to_list()


class UserBadgeRepository(BaseRepository[UserBadge]):
    model = UserBadge

    async def get_user_badge(self, user_id: str, badge_id: str) -> UserBadge | None:
        return await UserBadge.find_one(UserBadge.user_id == user_id, UserBadge.badge_id == badge_id)

    async def has_badge(self, user_id: str, badge_id: str) -> bool:
        return await self.get_user_badge(user_id, badge_id) is not None

    async def get_user_badges(self, user_id: str) -> list[UserBadge]:
        return await UserBadge.find(UserBadge.user_id == user_id).sort(-UserBadge.obtained_at).to_list()

    async def get_user_badge_ids(self, user_id: str) -> set[str]:
        ubs = await UserBadge.find(UserBadge.user_id == user_id).to_list()
        return {ub.badge_id for ub in ubs}
