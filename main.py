"""
3D Print Manager — FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

from database.db import init_db  # noqa: E402
from routers import costs, dashboard, jobs, rules, sales  # noqa: E402
from routers._templates import templates  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
    except Exception as exc:
        print(f"[ERROR] Cannot connect to PostgreSQL: {exc}")
        print("  Make sure the Docker container is running: docker compose up -d")
    yield


app = FastAPI(title="3D Print Manager", lifespan=lifespan, docs_url=None, redoc_url=None)

_BASE = Path(__file__).parent
app.mount("/static", StaticFiles(directory=_BASE / "static"), name="static")

app.include_router(dashboard.router)
app.include_router(rules.router)
app.include_router(jobs.router)
app.include_router(costs.router)
app.include_router(sales.router)


# ── Global error page ─────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "error.html",
        {"request": request, "active": "", "error": str(exc)},
        status_code=500,
    )
