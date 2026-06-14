from datetime import UTC, datetime

from beanie.operators import Inc, Set
from bson import ObjectId
from pymongo import ReturnDocument

from app.core.exceptions import NotFoundError
from app.models.user import RefreshToken, User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        return await User.find_one(User.email == email)

    async def get_by_username(self, username: str) -> User | None:
        return await User.find_one(User.username == username)

    async def email_exists(self, email: str) -> bool:
        return await User.find_one(User.email == email) is not None

    async def username_exists(self, username: str) -> bool:
        return await User.find_one(User.username == username) is not None

    async def increment_counter(self, user_id: str, field: str, amount: int = 1) -> None:
        await User.find_one(User.id == ObjectId(user_id)).update(Inc({field: amount}))

    async def increment_points(self, user_id: str, points: int) -> None:
        await User.find_one(User.id == ObjectId(user_id)).update(
            Inc({"points": points}),
            Set({"updated_at": datetime.now(UTC)}),
        )

    async def update_fields(self, user_id: str, **fields) -> User:
        fields["updated_at"] = datetime.now(UTC)
        await User.find_one(User.id == ObjectId(user_id)).update(Set(fields))
        user = await self.get_by_id(user_id)
        return user

    async def verify_email(self, user_id: str) -> None:
        await User.find_one(User.id == ObjectId(user_id)).update(
            Set({"is_email_verified": True, "updated_at": datetime.now(UTC)})
        )

    async def get_leaderboard_global(self, skip: int, limit: int) -> list[User]:
        return await User.find(User.is_active == True).sort(-User.points).skip(skip).limit(limit).to_list()

    async def get_leaderboard_by_country(self, country: str, skip: int, limit: int) -> list[User]:
        return (
            await User.find(User.country == country, User.is_active == True)
            .sort(-User.points)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def get_leaderboard_by_city(self, city: str, skip: int, limit: int) -> list[User]:
        return (
            await User.find(User.city == city, User.is_active == True)
            .sort(-User.points)
            .skip(skip)
            .limit(limit)
            .to_list()
        )


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    model = RefreshToken

    async def create(self, user_id: str, jti: str, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(user_id=user_id, jti=jti, expires_at=expires_at)
        return await self.save(token)

    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        return await RefreshToken.find_one(RefreshToken.jti == jti)

    async def revoke_by_jti(self, jti: str) -> None:
        token = await self.get_by_jti(jti)
        if token:
            await token.delete()

    async def revoke_all_for_user(self, user_id: str) -> None:
        await RefreshToken.find(RefreshToken.user_id == user_id).delete()
