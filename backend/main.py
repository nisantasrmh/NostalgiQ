"""Memory Lane FastAPI Application.

Provides REST API endpoints for:
- /health: Service status and configuration sanity check.
- /api/personas: Pre-loaded cultural persona profiles for instant demoing.
- /api/plan: Agent-driven reminiscence care plan grounded in Qloo taste graph.
- /api/compare: Side-by-side comparison between Qloo-grounded agent and generic LLM.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.agent.agent import ReminiscenceAgent
from backend.baseline.llm_only import GenericLLMBaseline
from backend.config import get_settings
from backend.models.schemas import ComparisonResult, ElderProfile, MemoryPlan

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

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

    - Queries Qloo for era- and region-correlated music, film, and dining.
    - Applies clinical dietary adaptation rules (texture modifications, glycemic substitutions).
    - Returns structured recommendations with an audit reasoning trail.
    """
    try:
        plan = await agent.generate_plan(profile)
        return plan
    except Exception as e:
        logger.exception("Failed to generate memory plan: %s", e)
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")


@app.post("/api/compare", response_model=ComparisonResult, tags=["Evaluation"])
async def compare_with_baseline(profile: ElderProfile) -> ComparisonResult:
    """Compare Qloo-grounded memory plan with a generic ungrounded LLM baseline side-by-side."""
    try:
        qloo_plan = await agent.generate_plan(profile)
        comparison = await baseline.compare(profile, qloo_plan)
        return comparison
    except Exception as e:
        logger.exception("Failed to run comparison: %s", e)
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
