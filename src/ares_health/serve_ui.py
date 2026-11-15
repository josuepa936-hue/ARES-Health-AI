"""Serve the compiled React frontend and synthetic template from local FastAPI.

Only documented, known static paths are served. No general file-browser route,
user uploads, network-hosting defaults or dynamic downloads are introduced.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

DEFAULT_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def install_compiled_frontend(app: FastAPI, dist: Path = DEFAULT_DIST, *, public_demo: bool = False) -> None:
    """Register compiled assets after API routes; no bundling at request time."""
    root = dist.resolve()
    assets = root / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets)), name="ares-frontend-assets")

    @app.get("/", include_in_schema=False)
    def integrated_home():
        index = root / "index.html"
        if not index.is_file():
            raise HTTPException(
                status_code=503,
                detail="ARES frontend is not built. Run npm ci and npm run build in frontend/.",
            )
        if public_demo:
            return HTMLResponse(index.read_text(encoding="utf-8").replace(
                "<html", '<html data-public-demo="1"', 1))
        return FileResponse(str(index), media_type="text/html")

    @app.get("/synthetic-template.csv", include_in_schema=False)
    def fictional_csv_template():
        file = root / "synthetic-template.csv"
        if not file.is_file():
            raise HTTPException(status_code=503, detail="Synthetic template requires a frontend build.")
        return FileResponse(str(file), media_type="text/csv", filename="synthetic-template.csv")
