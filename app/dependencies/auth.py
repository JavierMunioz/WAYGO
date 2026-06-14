from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository

_bearer = HTTPBearer(auto_error=False)


def _get_user_repo() -> UserRepository:
    return UserRepository()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    user_repo: Annotated[UserRepository, Depends(_get_user_repo)],
) -> User:
    if not credentials:
        raise UnauthorizedError("Bearer token required")

    payload = decode_access_token(credentials.credentials)
    user_id: str = payload.get("sub")

    user = await user_repo.get_by_id_or_none(user_id)
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    return user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_superuser:
        raise ForbiddenError("Superuser access required")
    return current_user


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    user_repo: Annotated[UserRepository, Depends(_get_user_repo)],
) -> User | None:
    if not credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str = payload.get("sub")
        return await user_repo.get_by_id_or_none(user_id)
    except Exception:
        return None


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
SuperUser = Annotated[User, Depends(get_current_superuser)]
