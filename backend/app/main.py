import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, documents, analysis, dashboard, chat, export
from app.config.settings import get_settings
from app.database.session import Base, engine, SessionLocal
from app.middleware.logging import RequestContextMiddleware
from app.auth.security import hash_password
from app.models.models import Role, User

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
settings = get_settings()


def seed_admin() -> None:
    with SessionLocal() as db:
        if not db.query(User).filter(User.email == "admin@example.com").first():
            db.add(User(email="admin@example.com", full_name="Administrator",
                        hashed_password=hash_password("ChangeMe123!"), role=Role.admin))
            db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.app_env == "development":
        seed_admin()
    yield


app = FastAPI(title="AI Financial Intelligence API", version="1.0.0", lifespan=lifespan)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API = "/api/v1"
app.include_router(auth.router, prefix=f"{API}/auth", tags=["Authentication"])
app.include_router(documents.router, prefix=f"{API}/documents", tags=["Documents"])
app.include_router(analysis.router, prefix=f"{API}/analysis", tags=["Analysis"])
app.include_router(dashboard.router, prefix=f"{API}/dashboard", tags=["Dashboard"])
app.include_router(chat.router, prefix=f"{API}/chat", tags=["Chat"])
app.include_router(export.router, prefix=f"{API}/export", tags=["Export"])


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
