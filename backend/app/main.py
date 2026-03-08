from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import admin, analytics, auth, chatbot, leads, notifications, tenants
from app.core.config import settings
from app.core.database import engine
from app.models import Base


app = FastAPI(title=settings.APP_NAME, version="0.1.0")

DASHBOARD_FILE = Path(__file__).resolve().parent / "utils" / "test_dashboard.html"
CLIENT_DASHBOARD = Path(__file__).resolve().parents[2] / "frontend" / "dashboard" / "index.html"
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

if FRONTEND_DIR.exists():
    # Expose demo files under /frontend so widget pages can be tested from the same Railway domain.
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


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


@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def client_dashboard() -> HTMLResponse:
    if not CLIENT_DASHBOARD.exists():
        return HTMLResponse("<h1>Dashboard not found.</h1>", status_code=404)
    return HTMLResponse(CLIENT_DASHBOARD.read_text(encoding="utf-8"))


app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(tenants.router, prefix=settings.API_V1_PREFIX)
app.include_router(chatbot.router, prefix=settings.API_V1_PREFIX)
app.include_router(leads.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(notifications.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)





