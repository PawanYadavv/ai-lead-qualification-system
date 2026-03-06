from sqlalchemy.orm import Session

from app.models.chat_session import ChatSession
from app.models.lead import Lead
from app.models.message import Message
from app.models.tenant import Tenant
from app.services.lead_scoring import calculate_lead_score
from app.services.notification_service import send_qualified_lead_notification
from app.services.openai_service import OpenAIService, get_openai_service
from app.services.prompt_templates import build_system_prompt


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
    if not lead.name and extracted.get("name"):
        lead.name = extracted["name"]
        session.visitor_name = extracted["name"]

    if not lead.email and extracted.get("email"):
        lead.email = extracted["email"]
        session.visitor_email = extracted["email"]

    if not lead.phone and extracted.get("phone"):
        lead.phone = extracted["phone"]
        session.visitor_phone = extracted["phone"]

    if not lead.budget and extracted.get("budget"):
        lead.budget = extracted["budget"]

    if not lead.timeline and extracted.get("timeline"):
        lead.timeline = extracted["timeline"]

    if not lead.requirement and extracted.get("requirement"):
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

    extracted = ai_service.extract_lead_fields(history)
    _merge_extracted_data(lead, session, extracted)

    lead.score = calculate_lead_score(lead)
    lead.is_qualified = lead.score >= tenant.qualification_threshold
    session.status = "qualified" if lead.is_qualified else "open"

    missing_fields = get_missing_fields(lead)
    prompt = build_system_prompt(tenant.system_prompt, missing_fields)
    assistant_reply = ai_service.generate_chat_response(prompt, history)
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

