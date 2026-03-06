from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models.notification import Notification
from app.models.tenant import Tenant
from app.schemas.notification import NotificationOut


router = APIRouter(tags=["notifications"])


@router.get("/notifications", response_model=list[NotificationOut])
def get_notifications(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[NotificationOut]:
    notifications = (
        db.query(Notification)
        .filter(Notification.tenant_id == current_tenant.id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )
    return notifications
