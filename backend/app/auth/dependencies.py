from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_token
from app.database.session import get_db
from app.models.models import Role, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    cred_exc = HTTPException(status.HTTP_401_UNAUTHORIZED, "Could not validate credentials",
                             headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = decode_token(token)
    except ValueError:
        raise cred_exc
    if payload.get("type") != "access":
        raise cred_exc
    user = db.get(User, payload.get("sub", ""))
    if not user or not user.is_active:
        raise cred_exc
    return user


def require_roles(*roles: Role):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user
    return checker


# Convenience guards
require_admin = require_roles(Role.admin)
require_finance = require_roles(Role.admin, Role.finance_manager)
require_any = require_roles(Role.admin, Role.finance_manager, Role.auditor)
