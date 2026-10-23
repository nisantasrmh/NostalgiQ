"""Memory Lane FastAPI Application.

Provides REST API endpoints for:
- /health: Service status and configuration sanity check.
- /api/personas: Pre-loaded cultural persona profiles for instant demoing.
- /api/plan: Agent-driven reminiscence care plan grounded in Qloo taste graph.
- /api/compare: Side-by-side comparison between Qloo-grounded agent and generic LLM.
"""

import csv
import io
import json
import logging
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import quote_plus

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.agent.agent import ReminiscenceAgent
from backend.baseline.llm_only import GenericLLMBaseline
from backend.config import get_settings
from backend.models.schemas import (
    ComparisonResult,
    ElderProfile,
    MemoryPlan,
    PlaylistExportRequest,
    PlaylistExportResponse,
    PlaylistTrack,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("memory_lane")

settings = get_settings()

app = FastAPI(
    title="Memory Lane API",
    description="Agent-powered reminiscence therapy planning using the Qloo Taste Graph and clinical dietary adaptation.",
    version="0.1.0",
)

# CORS configuration
allowed_origins = list(
    dict.fromkeys(
        settings.parsed_cors_origins
        + [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_cors_headers(request: Request) -> Dict[str, str]:
    """Helper to attach CORS headers to error responses."""
    origin = request.headers.get("origin")
    headers: Dict[str, str] = {}
    if origin and (origin in allowed_origins or "*" in allowed_origins):
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
        headers["Access-Control-Allow-Methods"] = "*"
        headers["Access-Control-Allow-Headers"] = "*"
    elif allowed_origins:
        headers["Access-Control-Allow-Origin"] = allowed_origins[0]
        headers["Access-Control-Allow-Credentials"] = "true"
        headers["Access-Control-Allow-Methods"] = "*"
        headers["Access-Control-Allow-Headers"] = "*"
    return headers


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Format HTTP exceptions as JSON error responses with CORS headers."""
    logger.warning("HTTP error on %s %s: %s", request.method, request.url.path, exc.detail)
    headers = _get_cors_headers(request)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)},
        headers=headers,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all unhandled exception handler to return JSON error responses with CORS headers."""
    logger.exception("Unhandled error on %s %s: %s", request.method, request.url.path, exc)
    headers = _get_cors_headers(request)
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
        headers=headers,
    )

# Shared agent and baseline instances
agent = ReminiscenceAgent()
baseline = GenericLLMBaseline()

PERSONAS_FILE = Path(__file__).parent.parent / "data" / "demo_personas.json"


@app.get("/health", tags=["System"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint to verify server status and Qloo adapter mode."""
    return {
        "status": "ok",
        "app": "Memory Lane",
        "version": "0.1.0",
        "use_mock_qloo": settings.use_mock_qloo,
        "llm_provider": settings.llm_provider,
    }


@app.get("/api/personas", response_model=List[ElderProfile], tags=["Personas"])
async def get_demo_personas() -> List[ElderProfile]:
    """Retrieve pre-configured demo personas (e.g. Sharada in Pune, Arthur in Chicago)."""
    if not PERSONAS_FILE.exists():
        raise HTTPException(status_code=404, detail="Demo personas dataset not found.")
    try:
        with open(PERSONAS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [ElderProfile(**item) for item in data]
    except Exception as e:
        logger.error("Error reading demo personas: %s", e)
        raise HTTPException(status_code=500, detail="Could not load personas.")


@app.post("/api/plan", response_model=MemoryPlan, tags=["Planning"])
async def create_memory_plan(profile: ElderProfile) -> MemoryPlan:
    """Generate a personalized Memory Plan grounded in Qloo Taste Graph correlations.

    - Resets session state for the new profile request.
    - Queries Qloo for era- and region-correlated music, film, and dining.
    - Applies clinical dietary adaptation rules (texture modifications, glycemic substitutions).
    - Returns structured recommendations with an audit reasoning trail.
    """
    try:
        fresh_agent = ReminiscenceAgent(llm_provider=settings.llm_provider)
        plan = await fresh_agent.generate_plan(profile)
        return plan
    except Exception as e:
        logger.exception("Failed to generate memory plan: %s", e)
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")


@app.post("/api/compare", response_model=ComparisonResult, tags=["Evaluation"])
async def compare_with_baseline(profile: ElderProfile) -> ComparisonResult:
    """Compare Qloo-grounded memory plan with a generic ungrounded LLM baseline side-by-side."""
    try:
        fresh_agent = ReminiscenceAgent(llm_provider=settings.llm_provider)
        fresh_baseline = GenericLLMBaseline()
        qloo_plan = await fresh_agent.generate_plan(profile)
        comparison = await fresh_baseline.compare(profile, qloo_plan)
        return comparison
    except Exception as e:
        logger.exception("Failed to run comparison: %s", e)
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@app.post("/api/export-playlist", tags=["Caregiver Tools"])
async def export_playlist(payload: PlaylistExportRequest):
    """Export curated reminiscence playlist enriched with YouTube and Spotify links.

    Supports:
    - format="json": returns structured JSON with caregiver streaming links.
    - format="csv": returns a downloadable CSV file.
    """
    format_type = (payload.format or "json").strip().lower()
    if format_type not in ("json", "csv"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{payload.format}'. Supported formats: 'json', 'csv'.",
        )

    enriched_tracks: List[PlaylistTrack] = []
    for item in payload.music_recommendations:
        search_query = f"{item.title} {item.creator_or_artist or ''}".strip()
        encoded_query = quote_plus(search_query)
        youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        spotify_search_url = f"https://open.spotify.com/search/{encoded_query}"

        enriched_tracks.append(
            PlaylistTrack(
                title=item.title,
                artist=item.creator_or_artist,
                era=item.era,
                youtube_url=youtube_url,
                spotify_search_url=spotify_search_url,
            )
        )

    if format_type == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Title", "Artist", "Era", "YouTube URL", "Spotify Search URL"])
        for track in enriched_tracks:
            writer.writerow([
                track.title,
                track.artist or "",
                track.era or "",
                track.youtube_url,
                track.spotify_search_url,
            ])

        sanitized_name = "".join(c for c in payload.elder_name if c.isalnum() or c in ("-", "_")).strip() or "elder"
        filename = f"{sanitized_name}_playlist.csv"
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )

    return PlaylistExportResponse(
        elder_name=payload.elder_name,
        total_tracks=len(enriched_tracks),
        tracks=enriched_tracks,
    )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
