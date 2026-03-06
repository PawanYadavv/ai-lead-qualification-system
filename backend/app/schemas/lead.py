from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LeadOut(BaseModel):
    id: str
    chat_session_id: str
    name: str | None
    email: str | None
    phone: str | None
    budget: str | None
    timeline: str | None
    requirement: str | None
    score: int
    is_qualified: bool
    notified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
