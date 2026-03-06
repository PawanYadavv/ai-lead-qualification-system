from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):
    id: str
    lead_id: str
    channel: str
    status: str
    subject: str
    body: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
