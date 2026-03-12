from sqlalchemy.orm import Session

from app.models.chat_session import ChatSession
from app.models.lead import Lead
from app.models.message import Message
from app.models.tenant import Tenant
from app.services.lead_scoring import calculate_lead_score
from app.services.notification_service import send_qualified_lead_notification
from app.services.openai_service import OpenAIService, get_openai_service, is_valid_email, is_valid_name, is_valid_phone
from app.services.prompt_templates import build_system_prompt


VALIDATION_MESSAGES = {
    "email": "Hmm, that doesn't look like a valid email address. Could you double-check and share it again? (e.g. name@company.com)",
    "phone": "That phone number doesn't seem right \u2014 please enter a valid 10-digit mobile number (e.g. +91-9876543210).",
    "name": "I didn't quite catch your name — could you share your full name?",
}


def _validate_extracted_data(extracted: dict[str, str]) -> tuple[dict[str, str], str | None]:
    """Validate extracted email/phone/name. Returns cleaned data and an optional correction message."""
    corrections: list[str] = []

    if extracted.get("name") and not is_valid_name(extracted["name"]):
        extracted.pop("name")
        corrections.append(VALIDATION_MESSAGES["name"])

    if extracted.get("email") and not is_valid_email(extracted["email"]):
        extracted.pop("email")
        corrections.append(VALIDATION_MESSAGES["email"])

    if extracted.get("phone") and not is_valid_phone(extracted["phone"]):
        extracted.pop("phone")
        corrections.append(VALIDATION_MESSAGES["phone"])

    correction = " Also, ".join(corrections) if corrections else None
    return extracted, correction


REQUIRED_FIELDS = ["name", "email", "phone", "budget", "timeline", "requirement"]
FOLLOW_UP_QUESTIONS = {
    "name": "Could I get your name so I can personalize this for you?",
    "email": "What is the best email to reach you with next steps?",
    "phone": "Do you want to share a phone number for a quick callback?",
    "budget": "Do you have a rough budget range in mind?",
    "timeline": "What timeline are you targeting to get started?",
    "requirement": "Can you share a bit more about what you need help with?",
}


def get_missing_fields(lead: Lead) -> list[str]:
    missing: list[str] = []
    for field in REQUIRED_FIELDS:
        if not getattr(lead, field):
            missing.append(field)
    return missing


def get_greeting_message() -> str:
    return "Hi! I am here to help. Tell me a little about what you are looking for today."


def _merge_extracted_data(lead: Lead, session: ChatSession, extracted: dict[str, str]) -> None:
    # Always update with the latest extracted data — later messages have more accurate info.
    if extracted.get("name"):
        lead.name = extracted["name"]
        session.visitor_name = extracted["name"]

    if extracted.get("email"):
        lead.email = extracted["email"]
        session.visitor_email = extracted["email"]

    if extracted.get("phone"):
        lead.phone = extracted["phone"]
        session.visitor_phone = extracted["phone"]

    if extracted.get("budget"):
        lead.budget = extracted["budget"]

    if extracted.get("timeline"):
        lead.timeline = extracted["timeline"]

    if extracted.get("requirement"):
        lead.requirement = extracted["requirement"]


def _fallback_reply(missing_fields: list[str]) -> str:
    if not missing_fields:
        return "Thanks, this is very helpful. Would you like us to schedule a quick call to discuss next steps?"
    return FOLLOW_UP_QUESTIONS[missing_fields[0]]


def process_chat_turn(
    db: Session,
    tenant: Tenant,
    session: ChatSession,
    user_message: str,
    ai_service: OpenAIService | None = None,
) -> tuple[str, Lead]:
    ai_service = ai_service or get_openai_service()

    user_record = Message(
        session_id=session.id,
        tenant_id=tenant.id,
        role="user",
        content=user_message,
    )
    db.add(user_record)
    db.flush()

    lead = db.query(Lead).filter(Lead.chat_session_id == session.id).first()
    if not lead:
        lead = Lead(tenant_id=tenant.id, chat_session_id=session.id)
        db.add(lead)
        db.flush()

    history_rows = (
        db.query(Message)
        .filter(Message.session_id == session.id)
        .order_by(Message.created_at.asc())
        .all()
    )
    history = [{"role": row.role, "content": row.content} for row in history_rows]

    # Use full history for extraction (to find all mentioned fields),
    # but cap what we send for chat generation to avoid context overflow.
    MAX_CHAT_HISTORY = 30
    extracted = ai_service.extract_lead_fields(history[-MAX_CHAT_HISTORY:])
    extracted, validation_correction = _validate_extracted_data(extracted)
    _merge_extracted_data(lead, session, extracted)

    lead.score = calculate_lead_score(lead)
    lead.is_qualified = lead.score >= tenant.qualification_threshold
    session.status = "qualified" if lead.is_qualified else "open"

    missing_fields = get_missing_fields(lead)
    prompt = build_system_prompt(tenant.system_prompt, missing_fields)

    # If validation failed, override AI response with correction message
    if validation_correction:
        assistant_reply = validation_correction
    else:
        assistant_reply = ai_service.generate_chat_response(prompt, history[-MAX_CHAT_HISTORY:])
        if not assistant_reply:
            assistant_reply = _fallback_reply(missing_fields)

    assistant_record = Message(
        session_id=session.id,
        tenant_id=tenant.id,
        role="assistant",
        content=assistant_reply,
    )
    db.add(assistant_record)

    if lead.is_qualified and not lead.notified:
        send_qualified_lead_notification(db, tenant, lead)
        lead.notified = True


    db.flush()
    return assistant_reply, lead

