from datetime import UTC, datetime, timedelta
from typing import Literal

from beanie import Document, Indexed
from pydantic import Field
from typing import Annotated


MAX_OTP_ATTEMPTS = 5


class OTPCode(Document):
    email: Annotated[str, Indexed()]
    code: str  # 6-digit string
    purpose: Literal["email_verify", "password_reset"]
    expires_at: datetime
    used: bool = False
    attempts: int = 0

    class Settings:
        name = "otp_codes"

    @classmethod
    def create_for(cls, email: str, code: str, purpose: Literal["email_verify", "password_reset"], ttl_minutes: int = 15) -> "OTPCode":
        return cls(
            email=email,
            code=code,
            purpose=purpose,
            expires_at=datetime.now(UTC) + timedelta(minutes=ttl_minutes),
        )

    @property
    def is_expired(self) -> bool:
        return datetime.now(UTC) > self.expires_at.replace(tzinfo=UTC)
