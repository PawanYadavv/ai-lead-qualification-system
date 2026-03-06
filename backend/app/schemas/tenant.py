from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TenantOut(BaseModel):
    id: str
    name: str
    slug: str
    widget_token: str
    system_prompt: str | None
    qualification_threshold: int
    notification_email: EmailStr | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TenantUpdate(BaseModel):
    system_prompt: str | None = Field(default=None, max_length=5000)
    qualification_threshold: int | None = Field(default=None, ge=1, le=100)
    notification_email: EmailStr | None = None
