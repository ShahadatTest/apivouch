from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.demo import router as demo_router
from app.api.mcp import router as mcp_router
from app.api.outcomes import router as outcomes_router
from app.api.projects import router as projects_router
from app.core.config import APP_VERSION, CORS_ORIGINS, GIT_COMMIT, PROJECT_SLUG
from app.models.db import init_db

app = FastAPI(
    title="APIVouch",
    version=APP_VERSION,
    description="Evidence-based API diagnostics, agent-contract generation, and dynamic MCP tools.",
)
if CORS_ORIGINS:
    app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=["GET", "POST", "DELETE"], allow_headers=["content-type"])

init_db()
app.include_router(projects_router, prefix="/api")
app.include_router(outcomes_router, prefix="/api")
app.include_router(mcp_router)
app.include_router(demo_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "apivouch", "version": APP_VERSION, "commit": GIT_COMMIT}


@app.get("/.well-known/xagent-verification.json")
async def verification():
    return {"schemaVersion": 1, "slug": PROJECT_SLUG, "commit": GIT_COMMIT}


_frontend_candidates = [
    Path(__file__).resolve().parents[2] / "frontend",
    Path(__file__).resolve().parents[1] / "frontend",
]
_frontend = next((path for path in _frontend_candidates if path.exists()), _frontend_candidates[0])


@app.get("/", include_in_schema=False)
async def dashboard():
    if (_frontend / "index.html").exists():
        return FileResponse(_frontend / "index.html")
    return {"service": "apivouch", "docs": "/docs"}


@app.get("/app.js", include_in_schema=False)
async def dashboard_script():
    return FileResponse(_frontend / "app.js", media_type="application/javascript")
