from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models.chat_session import ChatSession
from app.models.lead import Lead
from app.models.tenant import Tenant
from app.schemas.analytics import AnalyticsOut


router = APIRouter(tags=["analytics"])


@router.get("/analytics", response_model=AnalyticsOut)
def get_analytics(
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> AnalyticsOut:
    total_leads = (
        db.query(func.count(Lead.id)).filter(Lead.tenant_id == current_tenant.id).scalar() or 0
    )
    qualified_leads = (
        db.query(func.count(Lead.id))
        .filter(Lead.tenant_id == current_tenant.id, Lead.is_qualified.is_(True))
        .scalar()
        or 0
    )
    avg_score = db.query(func.avg(Lead.score)).filter(Lead.tenant_id == current_tenant.id).scalar() or 0

    total_conversations = (
        db.query(func.count(ChatSession.id))
        .filter(ChatSession.tenant_id == current_tenant.id)
        .scalar()
        or 0
    )
    open_conversations = (
        db.query(func.count(ChatSession.id))
        .filter(ChatSession.tenant_id == current_tenant.id, ChatSession.status == "open")
        .scalar()
        or 0
    )

    rate = (qualified_leads / total_leads * 100) if total_leads else 0.0

    return AnalyticsOut(
        total_leads=total_leads,
        qualified_leads=qualified_leads,
        qualification_rate=round(rate, 2),
        total_conversations=total_conversations,
        open_conversations=open_conversations,
        avg_lead_score=round(float(avg_score), 2),
    )
