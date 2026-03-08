from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.tenant import Tenant
from app.schemas.tenant import TenantOut

router = APIRouter(prefix="/admin", tags=["admin"])


def _verify_admin_key(x_admin_key: str = Header(...)) -> str:
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin key")
    return x_admin_key


@router.get("/tenants", response_model=list[TenantOut])
def list_all_tenants(
    db: Session = Depends(get_db),
    _: str = Depends(_verify_admin_key),
) -> list[TenantOut]:
    return db.query(Tenant).order_by(Tenant.created_at.desc()).all()


@router.patch("/tenants/{tenant_id}/activate", response_model=TenantOut)
def activate_tenant(
    tenant_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(_verify_admin_key),
) -> TenantOut:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    tenant.is_active = True
    db.commit()
    db.refresh(tenant)
    return tenant


@router.patch("/tenants/{tenant_id}/deactivate", response_model=TenantOut)
def deactivate_tenant(
    tenant_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(_verify_admin_key),
) -> TenantOut:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    tenant.is_active = False
    db.commit()
    db.refresh(tenant)
    return tenant
