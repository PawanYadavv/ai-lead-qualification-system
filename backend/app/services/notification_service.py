import smtplib
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.lead import Lead
from app.models.notification import Notification
from app.models.tenant import Tenant


def _build_notification_content(lead: Lead) -> tuple[str, str]:
    subject = f"Qualified Lead Alert - {lead.name or lead.email or lead.id}"
    body = (
        "A lead has crossed your qualification threshold.\n\n"
        f"Lead ID: {lead.id}\n"
        f"Name: {lead.name or 'N/A'}\n"
        f"Email: {lead.email or 'N/A'}\n"
        f"Phone: {lead.phone or 'N/A'}\n"
        f"Budget: {lead.budget or 'N/A'}\n"
        f"Timeline: {lead.timeline or 'N/A'}\n"
        f"Requirement: {lead.requirement or 'N/A'}\n"
        f"Score: {lead.score}\n"
    )
    return subject, body


def _append_delivery_error(body: str, error_message: str) -> str:
    return f"{body}\n\nDelivery error: {error_message}"


def _validate_smtp_settings() -> None:
    missing: list[str] = []

    if not settings.SMTP_HOST:
        missing.append("SMTP_HOST")
    if not settings.SMTP_USER:
        missing.append("SMTP_USER")
    if not settings.SMTP_PASS:
        missing.append("SMTP_PASS")
    if not settings.SMTP_FROM_EMAIL:
        missing.append("SMTP_FROM_EMAIL")

    if missing:
        raise RuntimeError("SMTP settings are incomplete: missing " + ", ".join(missing))


def _send_email(recipient: str, subject: str, body: str) -> None:
    _validate_smtp_settings()

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = recipient
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as server:
        server.ehlo()
        if settings.SMTP_USE_TLS:
            server.starttls()
            server.ehlo()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg)


def send_qualified_lead_notification(db: Session, tenant: Tenant, lead: Lead) -> Notification:
    subject, body = _build_notification_content(lead)
    notification = Notification(
        tenant_id=tenant.id,
        lead_id=lead.id,
        channel="email",
        status="pending",
        subject=subject,
        body=body,
    )
    db.add(notification)

    recipient = tenant.notification_email
    if not recipient:
        notification.status = "failed"
        notification.body = _append_delivery_error(body, "Recipient email is not configured for this tenant")
        return notification

    try:
        _send_email(recipient, subject, body)
        notification.status = "sent"
    except Exception as exc:
        notification.status = "failed"
        notification.body = _append_delivery_error(body, str(exc))

    return notification
