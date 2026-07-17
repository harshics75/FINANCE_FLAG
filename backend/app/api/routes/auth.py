from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin
from app.auth.security import (create_access_token, create_refresh_token,
                               decode_token, hash_password, verify_password)
from app.database.session import get_db
from app.models.models import Role, User
from app.repositories.repositories import AuditLogRepository, UserRepository
from app.schemas.schemas import RefreshRequest, TokenPair, UserCreate, UserOut

router = APIRouter()


@router.post("/register", response_model=UserOut, dependencies=[Depends(require_admin)])
def register(payload: UserCreate, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    if repo.by_email(payload.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = repo.create(User(email=payload.email, full_name=payload.full_name,
                            hashed_password=hash_password(payload.password),
                            role=Role(payload.role)))
    return user


@router.post("/login", response_model=TokenPair)
def login(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = UserRepository(db).by_email(form.username)
    if not user or not verify_password(form.password, user.hashed_password) or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    AuditLogRepository(db).log(user.id, "login", ip=request.client.host if request.client else "")
    return TokenPair(access_token=create_access_token(user.id, user.role.value),
                     refresh_token=create_refresh_token(user.id, user.role.value))


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        claims = decode_token(payload.refresh_token)
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
    if claims.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")
    user = db.get(User, claims["sub"])
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User inactive")
    return TokenPair(access_token=create_access_token(user.id, user.role.value),
                     refresh_token=create_refresh_token(user.id, user.role.value))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
