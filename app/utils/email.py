import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_verify_html(code: str) -> str:
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;background:#0d0d0d;color:#fff;border-radius:16px;padding:32px;">
      <h1 style="color:#00C896;letter-spacing:4px;margin:0 0 8px">WAYGO</h1>
      <p style="color:#aaa;margin:0 0 24px">Explora. Visita. Comparte.</p>
      <hr style="border-color:#222;margin:0 0 24px">
      <h2 style="margin:0 0 12px">Verifica tu correo</h2>
      <p style="color:#ccc;margin:0 0 24px">Usa este código en la app para verificar tu cuenta. Válido por 15 minutos.</p>
      <div style="background:#1a1a1a;border:2px solid #00C896;border-radius:12px;padding:20px;text-align:center;margin:0 0 24px">
        <span style="font-size:36px;font-weight:900;letter-spacing:12px;color:#00C896">{code}</span>
      </div>
      <p style="color:#666;font-size:12px;margin:0">Si no creaste una cuenta en WAYGO, ignora este correo.</p>
    </div>
    """


def _build_reset_html(code: str) -> str:
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;background:#0d0d0d;color:#fff;border-radius:16px;padding:32px;">
      <h1 style="color:#00C896;letter-spacing:4px;margin:0 0 8px">WAYGO</h1>
      <p style="color:#aaa;margin:0 0 24px">Explora. Visita. Comparte.</p>
      <hr style="border-color:#222;margin:0 0 24px">
      <h2 style="margin:0 0 12px">Restablecer contraseña</h2>
      <p style="color:#ccc;margin:0 0 24px">Usa este código en la app para crear una nueva contraseña. Válido por 15 minutos.</p>
      <div style="background:#1a1a1a;border:2px solid #FF6B35;border-radius:12px;padding:20px;text-align:center;margin:0 0 24px">
        <span style="font-size:36px;font-weight:900;letter-spacing:12px;color:#FF6B35">{code}</span>
      </div>
      <p style="color:#666;font-size:12px;margin:0">Si no solicitaste esto, ignora este correo. Tu contraseña no cambiará.</p>
    </div>
    """


def send_verification_email(to_email: str, code: str) -> None:
    _send(
        to=to_email,
        subject="WAYGO — Verifica tu cuenta",
        html=_build_verify_html(code),
    )


def send_reset_email(to_email: str, code: str) -> None:
    _send(
        to=to_email,
        subject="WAYGO — Código para restablecer contraseña",
        html=_build_reset_html(code),
    )


def _send(to: str, subject: str, html: str) -> None:
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP not configured — skipping email to %s", to)
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to
    msg.attach(MIMEText(html, "html"))

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, to, msg.as_string())
        logger.info("Email sent to %s — %s", to, subject)
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to, exc)
