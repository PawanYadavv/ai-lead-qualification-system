from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models.tenant import Tenant
from app.schemas.tenant import TenantOut, TenantUpdate


router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/me", response_model=TenantOut)
def get_my_tenant(current_tenant: Tenant = Depends(get_current_tenant)) -> TenantOut:
    return current_tenant


@router.patch("/me", response_model=TenantOut)
def update_my_tenant(
    payload: TenantUpdate,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> TenantOut:
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(current_tenant, key, value)

    db.add(current_tenant)
    db.commit()
    db.refresh(current_tenant)
    return current_tenant
