from fastapi import APIRouter, BackgroundTasks, status

from app.dependencies.auth import CurrentUser
from app.repositories.stats_repository import StatsRepository
from app.repositories.user_repository import RefreshTokenRepository, UserRepository
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordOTPRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailOTPRequest,
    VerifyEmailRequest,
)
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService
from app.utils.email import send_reset_email, send_verification_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _get_auth_service() -> AuthService:
    return AuthService(
        user_repo=UserRepository(),
        token_repo=RefreshTokenRepository(),
        stats_repo=StatsRepository(),
    )


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
async def register(data: RegisterRequest, background_tasks: BackgroundTasks):
    svc = _get_auth_service()
    user = await svc.register(data)
    code = await svc.generate_email_verification_otp(user.email)
    background_tasks.add_task(send_verification_email, user.email, code)
    return MessageResponse(message="Registration successful. Please verify your email.")


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    svc = _get_auth_service()
    return await svc.login(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest):
    svc = _get_auth_service()
    return await svc.refresh(data.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(data: RefreshTokenRequest, current_user: CurrentUser):
    svc = _get_auth_service()
    await svc.logout(data.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.post("/logout-all", response_model=MessageResponse)
async def logout_all_devices(current_user: CurrentUser):
    svc = _get_auth_service()
    await svc.logout_all_devices(str(current_user.id))
    return MessageResponse(message="Logged out from all devices")


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(data: VerifyEmailRequest):
    svc = _get_auth_service()
    await svc.verify_email(data.token)
    return MessageResponse(message="Email verified successfully")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(data: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    svc = _get_auth_service()
    code = await svc.generate_password_reset_otp(data.email)
    if code:
        background_tasks.add_task(send_reset_email, data.email, code)
    return MessageResponse(message="Si ese correo existe, recibirás un código de verificación")


@router.post("/verify-email-otp", response_model=MessageResponse)
async def verify_email_otp(data: VerifyEmailOTPRequest):
    svc = _get_auth_service()
    await svc.verify_email_otp(data.email, data.code)
    return MessageResponse(message="Email verificado correctamente")


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(data: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    """Resend email verification OTP. Reuses ForgotPasswordRequest (only needs email)."""
    svc = _get_auth_service()
    user = await UserRepository().get_by_email(data.email)
    if user and not user.is_email_verified:
        code = await svc.generate_email_verification_otp(data.email)
        background_tasks.add_task(send_verification_email, data.email, code)
    # Always return 200 — don't reveal whether the email exists or is already verified
    return MessageResponse(message="Si ese correo existe y no está verificado, recibirás un nuevo código")


@router.post("/reset-password-otp", response_model=MessageResponse)
async def reset_password_otp(data: ResetPasswordOTPRequest):
    svc = _get_auth_service()
    await svc.reset_password_otp(data.email, data.code, data.new_password)
    return MessageResponse(message="Contraseña restablecida correctamente")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: ResetPasswordRequest):
    svc = _get_auth_service()
    await svc.reset_password(data.token, data.new_password)
    return MessageResponse(message="Password reset successfully")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(data: ChangePasswordRequest, current_user: CurrentUser):
    from app.core.security import hash_password, verify_password
    from app.core.exceptions import InvalidCredentialsError

    if not verify_password(data.current_password, current_user.password_hash):
        raise InvalidCredentialsError("Current password is incorrect")

    user_repo = UserRepository()
    await user_repo.update_fields(str(current_user.id), password_hash=hash_password(data.new_password))
    return MessageResponse(message="Password changed successfully")
