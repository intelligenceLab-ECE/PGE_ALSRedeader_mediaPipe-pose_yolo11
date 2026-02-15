from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.src.web_api import api_router, get_meta_info, get_runtime_status, shutdown_services

app = FastAPI(title="AI Playground API", version="1.0.0")
app.include_router(api_router)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "services": get_runtime_status(),
    }


@app.get("/api/meta")
def api_meta() -> Dict[str, Any]:
    return get_meta_info()


@app.on_event("shutdown")
def on_shutdown() -> None:
    shutdown_services()


STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists() and (STATIC_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")


@app.get("/{full_path:path}")
def spa_fallback(full_path: str):
    if full_path.startswith("api") or full_path == "health":
        return JSONResponse({"message": "Not found"}, status_code=404)

    if not STATIC_DIR.exists():
        return JSONResponse({"message": "Frontend build not found"}, status_code=503)

    requested = STATIC_DIR / full_path
    if full_path and requested.exists() and requested.is_file():
        return FileResponse(requested)

    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)

    return JSONResponse({"message": "Frontend build not found"}, status_code=503)
