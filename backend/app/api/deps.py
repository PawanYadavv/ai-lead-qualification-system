from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.tenant import Tenant
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    unauthorized_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            raise unauthorized_exc
    except JWTError as exc:
        raise unauthorized_exc from exc

    user = db.query(User).filter(User.email == subject).first()
    if user is None or not user.is_active:
        raise unauthorized_exc

    return user


def get_current_tenant(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> Tenant:
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    if not tenant.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account suspended. Please contact support.")
    return tenant
