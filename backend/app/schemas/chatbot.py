from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class StartSessionRequest(BaseModel):
    tenant_token: str
    visitor_name: str | None = Field(default=None, max_length=255)
    visitor_email: EmailStr | None = None
    visitor_phone: str | None = Field(default=None, max_length=50)


class StartSessionResponse(BaseModel):
    session_id: str
    greeting_message: str


class ChatMessageRequest(BaseModel):
    tenant_token: str
    message: str = Field(min_length=1, max_length=4000)


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatMessageResponse(BaseModel):
    session_id: str
    reply: str
    lead_score: int
    is_qualified: bool


class ConversationOut(BaseModel):
    session_id: str
    status: str
    visitor_name: str | None
    visitor_email: str | None
    visitor_phone: str | None
    created_at: datetime
    messages: list[MessageOut]
