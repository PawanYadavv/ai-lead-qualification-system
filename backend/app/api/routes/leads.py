from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models.lead import Lead
from app.models.tenant import Tenant
from app.schemas.lead import LeadOut


router = APIRouter(tags=["leads"])


@router.get("/leads", response_model=list[LeadOut])
def get_tenant_leads(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[LeadOut]:
    leads = (
        db.query(Lead)
        .filter(Lead.tenant_id == current_tenant.id)
        .order_by(Lead.created_at.desc())
        .limit(limit)
        .all()
    )
    return leads
