import secrets
import string
from datetime import UTC, datetime, timedelta

from app.core.config import settings
from app.core.exceptions import (
    AlreadyExistsError,
    EmailNotVerifiedError,
    InvalidCredentialsError,
    InvalidTokenError,
    NotFoundError,
)
from app.core.security import (
    create_access_token,
    create_email_token,
    create_password_reset_token,
    create_refresh_token,
    decode_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.otp_code import MAX_OTP_ATTEMPTS, OTPCode
from app.models.user import User, RefreshToken
from app.models.user_stats import UserStats
from app.repositories.stats_repository import StatsRepository
from app.repositories.user_repository import RefreshTokenRepository, UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: RefreshTokenRepository,
        stats_repo: StatsRepository,
    ):
        self._user_repo = user_repo
        self._token_repo = token_repo
        self._stats_repo = stats_repo

    async def register(self, data: RegisterRequest) -> User:
        if await self._user_repo.email_exists(data.email):
            raise AlreadyExistsError("Email already registered")
        if await self._user_repo.username_exists(data.username):
            raise AlreadyExistsError("Username already taken")

        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            country=data.country,
            city=data.city,
        )
        await user.save()

        # Initialize stats document
        await self._stats_repo.upsert(str(user.id), country=data.country, city=data.city)
        return user

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self._user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise InvalidCredentialsError("Account is disabled")
        if not user.is_email_verified:
            raise EmailNotVerifiedError()

        return await self._issue_token_pair(str(user.id))

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_refresh_token(refresh_token)
        jti = payload.get("jti")
        user_id = payload.get("sub")

        stored = await self._token_repo.get_by_jti(jti)
        if not stored:
            raise InvalidTokenError("Refresh token has been revoked")

        # Rotate: revoke old, issue new pair
        await self._token_repo.revoke_by_jti(jti)
        return await self._issue_token_pair(user_id)

    async def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_refresh_token(refresh_token)
            await self._token_repo.revoke_by_jti(payload.get("jti"))
        except Exception:
            pass  # Best-effort revocation

    async def logout_all_devices(self, user_id: str) -> None:
        await self._token_repo.revoke_all_for_user(user_id)

    async def generate_email_verification_token(self, user_id: str) -> str:
        user = await self._user_repo.get_by_id(user_id)
        return create_email_token(user.email)

    async def verify_email(self, token: str) -> None:
        payload = decode_token(token, "email_verify")
        email = payload.get("sub")
        user = await self._user_repo.get_by_email(email)
        if not user:
            raise NotFoundError("User not found")
        await self._user_repo.verify_email(str(user.id))

    async def request_password_reset(self, email: str) -> str:
        user = await self._user_repo.get_by_email(email)
        if not user:
            return ""  # Silent — never reveal whether email exists
        return create_password_reset_token(email)

    async def reset_password(self, token: str, new_password: str) -> None:
        payload = decode_token(token, "password_reset")
        email = payload.get("sub")
        user = await self._user_repo.get_by_email(email)
        if not user:
            raise NotFoundError("User not found")
        await self._user_repo.update_fields(str(user.id), password_hash=hash_password(new_password))
        await self._token_repo.revoke_all_for_user(str(user.id))

    # OTP-based flows (mobile-friendly)

    @staticmethod
    def _generate_otp() -> str:
        return "".join(secrets.choice(string.digits) for _ in range(6))

    async def generate_email_verification_otp(self, email: str) -> str:
        # Invalidate any previous unused OTPs for this email+purpose
        await OTPCode.find(OTPCode.email == email, OTPCode.purpose == "email_verify", OTPCode.used == False).delete()  # noqa: E712
        code = self._generate_otp()
        otp = OTPCode.create_for(email=email, code=code, purpose="email_verify", ttl_minutes=15)
        await otp.save()
        return code

    async def verify_email_otp(self, email: str, code: str) -> None:
        otp = await OTPCode.find_one(
            OTPCode.email == email,
            OTPCode.purpose == "email_verify",
            OTPCode.used == False,  # noqa: E712
        )
        if not otp or otp.is_expired:
            raise InvalidTokenError("Código inválido o expirado")
        if otp.attempts >= MAX_OTP_ATTEMPTS:
            raise InvalidTokenError("Demasiados intentos fallidos. Solicita un nuevo código.")
        if otp.code != code:
            await otp.set({OTPCode.attempts: otp.attempts + 1})
            raise InvalidTokenError("Código inválido o expirado")
        await otp.set({OTPCode.used: True})
        user = await self._user_repo.get_by_email(email)
        if user:
            await self._user_repo.verify_email(str(user.id))

    async def generate_password_reset_otp(self, email: str) -> str | None:
        user = await self._user_repo.get_by_email(email)
        if not user:
            return None  # Silent — never reveal whether email exists
        await OTPCode.find(OTPCode.email == email, OTPCode.purpose == "password_reset", OTPCode.used == False).delete()  # noqa: E712
        code = self._generate_otp()
        otp = OTPCode.create_for(email=email, code=code, purpose="password_reset", ttl_minutes=15)
        await otp.save()
        return code

    async def reset_password_otp(self, email: str, code: str, new_password: str) -> None:
        otp = await OTPCode.find_one(
            OTPCode.email == email,
            OTPCode.purpose == "password_reset",
            OTPCode.used == False,  # noqa: E712
        )
        if not otp or otp.is_expired:
            raise InvalidTokenError("Código inválido o expirado")
        if otp.attempts >= MAX_OTP_ATTEMPTS:
            raise InvalidTokenError("Demasiados intentos fallidos. Solicita un nuevo código.")
        if otp.code != code:
            await otp.set({OTPCode.attempts: otp.attempts + 1})
            raise InvalidTokenError("Código inválido o expirado")
        user = await self._user_repo.get_by_email(email)
        if not user:
            raise NotFoundError("User not found")
        await otp.set({OTPCode.used: True})
        await self._user_repo.update_fields(str(user.id), password_hash=hash_password(new_password))
        await self._token_repo.revoke_all_for_user(str(user.id))

    async def _issue_token_pair(self, user_id: str) -> TokenResponse:
        import uuid
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        # Decode to extract JTI for storage
        from jose import jwt as jose_jwt
        payload = jose_jwt.decode(
            refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": False},
        )
        jti = payload["jti"]
        expires_at = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        await self._token_repo.create(user_id=user_id, jti=jti, expires_at=expires_at)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
