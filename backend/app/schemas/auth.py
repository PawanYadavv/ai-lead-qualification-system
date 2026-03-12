from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    business_name: str = Field(min_length=2, max_length=255)
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    notification_email: EmailStr | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TenantBasic(BaseModel):
    id: str
    name: str
    slug: str
    widget_token: str
    qualification_threshold: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserOut(BaseModel):
    id: str
    tenant_id: str
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
    tenant: TenantBasic
    