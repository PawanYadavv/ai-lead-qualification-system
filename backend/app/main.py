from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.routes import analytics, auth, chatbot, leads, notifications, tenants
from app.core.config import settings
from app.core.database import engine
from app.models import Base


app = FastAPI(title=settings.APP_NAME, version="0.1.0")

DASHBOARD_FILE = Path(__file__).resolve().parent / "utils" / "test_dashboard.html"

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/test-dashboard", response_class=HTMLResponse, include_in_schema=False)
def test_dashboard() -> HTMLResponse:
    if not DASHBOARD_FILE.exists():
        return HTMLResponse("<h1>Test dashboard not found.</h1>", status_code=404)
    return HTMLResponse(DASHBOARD_FILE.read_text(encoding="utf-8"))


app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(tenants.router, prefix=settings.API_V1_PREFIX)
app.include_router(chatbot.router, prefix=settings.API_V1_PREFIX)
app.include_router(leads.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(notifications.router, prefix=settings.API_V1_PREFIX)





