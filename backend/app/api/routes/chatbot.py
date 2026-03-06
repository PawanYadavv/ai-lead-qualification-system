from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models.chat_session import ChatSession
from app.models.lead import Lead
from app.models.message import Message
from app.models.tenant import Tenant
from app.schemas.chatbot import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationOut,
    MessageOut,
    StartSessionRequest,
    StartSessionResponse,
)
from app.services.conversation_service import get_greeting_message, process_chat_turn


router = APIRouter(tags=["chatbot"])


def _get_tenant_by_widget_token(db: Session, tenant_token: str) -> Tenant:
    tenant = db.query(Tenant).filter(Tenant.widget_token == tenant_token).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid tenant token")
    return tenant


@router.post("/chatbot/session/start", response_model=StartSessionResponse)
def start_chat_session(payload: StartSessionRequest, db: Session = Depends(get_db)) -> StartSessionResponse:
    tenant = _get_tenant_by_widget_token(db, payload.tenant_token)

    session = ChatSession(
        tenant_id=tenant.id,
        visitor_name=payload.visitor_name,
        visitor_email=payload.visitor_email,
        visitor_phone=payload.visitor_phone,
    )
    db.add(session)
    db.flush()

    lead = Lead(
        tenant_id=tenant.id,
        chat_session_id=session.id,
        name=payload.visitor_name,
        email=payload.visitor_email,
        phone=payload.visitor_phone,
    )
    db.add(lead)

    greeting_message = get_greeting_message()
    db.add(
        Message(
            session_id=session.id,
            tenant_id=tenant.id,
            role="assistant",
            content=greeting_message,
        )
    )

    db.commit()
    return StartSessionResponse(session_id=session.id, greeting_message=greeting_message)


@router.post("/chatbot/session/{session_id}/message", response_model=ChatMessageResponse)
def send_chat_message(
    session_id: str,
    payload: ChatMessageRequest,
    db: Session = Depends(get_db),
) -> ChatMessageResponse:
    tenant = _get_tenant_by_widget_token(db, payload.tenant_token)

    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.tenant_id == tenant.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    reply, lead = process_chat_turn(db=db, tenant=tenant, session=session, user_message=payload.message)
    db.commit()

    return ChatMessageResponse(
        session_id=session_id,
        reply=reply,
        lead_score=lead.score,
        is_qualified=lead.is_qualified,
    )


@router.get("/chatbot/session/{session_id}/messages", response_model=list[MessageOut])
def get_public_session_messages(
    session_id: str,
    tenant_token: str = Query(...),
    db: Session = Depends(get_db),
) -> list[MessageOut]:
    tenant = _get_tenant_by_widget_token(db, tenant_token)

    messages = (
        db.query(Message)
        .join(ChatSession, ChatSession.id == Message.session_id)
        .filter(Message.session_id == session_id, ChatSession.tenant_id == tenant.id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return messages


@router.get("/conversations", response_model=list[ConversationOut])
def get_tenant_conversations(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[ConversationOut]:
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.tenant_id == current_tenant.id)
        .order_by(ChatSession.created_at.desc())
        .limit(limit)
        .all()
    )

    response: list[ConversationOut] = []
    for session in sessions:
        messages = (
            db.query(Message)
            .filter(Message.session_id == session.id)
            .order_by(Message.created_at.asc())
            .all()
        )
        response.append(
            ConversationOut(
                session_id=session.id,
                status=session.status,
                visitor_name=session.visitor_name,
                visitor_email=session.visitor_email,
                visitor_phone=session.visitor_phone,
                created_at=session.created_at,
                messages=messages,
            )
        )

    return response
