"""
Startup Prediction API Routes
Endpoints for researching startups and predicting unicorn outcomes
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio

from backend.engine.startup_engine import (
    StartupPredictionEngine,
    Startup,
    UnicornPrediction,
    BatchPrediction,
)

router = APIRouter(prefix="/api/startups", tags=["Startups"])

# Global engine instance
_engine: Optional[StartupPredictionEngine] = None


def get_engine() -> StartupPredictionEngine:
    global _engine
    if _engine is None:
        _engine = StartupPredictionEngine()
    return _engine


# In-memory cache for researched startups and predictions
startups_cache: Dict[str, Startup] = {}
predictions_cache: Dict[str, UnicornPrediction] = {}
batch_cache: Dict[str, BatchPrediction] = {}


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class ResearchStartupRequest(BaseModel):
    name: str
    batch: Optional[str] = None


class ResearchBatchRequest(BaseModel):
    batch_name: str
    company_names: Optional[List[str]] = None


class PredictStartupRequest(BaseModel):
    startup_id: str


class ChatRequest(BaseModel):
    startup_id: str
    message: str
    conversation_history: List[Dict] = []


class StartupSummary(BaseModel):
    id: str
    name: str
    industry: str
    stage: str
    unicorn_probability: Optional[float] = None
    confidence: float


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/health")
async def health():
    """Health check for startup prediction service."""
    engine = get_engine()
    return {
        "status": "healthy",
        "exa_available": engine.exa is not None,
        "llm_available": engine.llm is not None,
        "cached_startups": len(startups_cache),
        "cached_predictions": len(predictions_cache),
    }


@router.post("/research", response_model=Startup)
async def research_startup(request: ResearchStartupRequest):
    """
    Deep research on a single startup.
    Uses Exa API for web search + Claude for synthesis.
    """
    engine = get_engine()

    # Check cache
    cache_key = f"{request.name}:{request.batch or 'none'}"
    if cache_key in startups_cache:
        return startups_cache[cache_key]

    # Research
    startup = await engine.research_startup(request.name, request.batch)

    # Cache
    startups_cache[cache_key] = startup
    startups_cache[startup.id] = startup

    return startup


@router.post("/research/batch")
async def research_batch(request: ResearchBatchRequest, background_tasks: BackgroundTasks):
    """
    Research multiple startups in a batch.
    Returns immediately with batch_id, researches in background.
    """
    batch_id = f"batch_{request.batch_name.replace(' ', '_')}"

    # Start background research
    background_tasks.add_task(
        _research_batch_task,
        batch_id,
        request.batch_name,
        request.company_names
    )

    return {
        "batch_id": batch_id,
        "status": "researching",
        "batch_name": request.batch_name,
        "company_count": len(request.company_names) if request.company_names else "discovering",
    }


async def _research_batch_task(batch_id: str, batch_name: str, company_names: Optional[List[str]]):
    """Background task to research a batch."""
    engine = get_engine()

    startups = await engine.research_batch(batch_name, company_names)

    # Cache all startups
    for s in startups:
        startups_cache[s.id] = s
        startups_cache[f"{s.name}:{batch_name}"] = s

    # Generate predictions
    batch_prediction = engine.predict_batch(startups, batch_name)
    batch_cache[batch_id] = batch_prediction

    # Cache individual predictions
    for p in batch_prediction.startups:
        predictions_cache[p.startup_id] = p


@router.get("/research/batch/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get status of batch research."""
    if batch_id in batch_cache:
        batch = batch_cache[batch_id]
        return {
            "status": "complete",
            "batch": batch,
        }
    return {
        "status": "researching",
        "message": "Batch research in progress..."
    }


@router.post("/predict", response_model=UnicornPrediction)
async def predict_startup(request: PredictStartupRequest):
    """
    Predict unicorn probability for a researched startup.
    """
    # Check prediction cache
    if request.startup_id in predictions_cache:
        return predictions_cache[request.startup_id]

    # Get startup from cache
    if request.startup_id not in startups_cache:
        raise HTTPException(404, f"Startup {request.startup_id} not found. Research it first.")

    startup = startups_cache[request.startup_id]
    engine = get_engine()

    prediction = engine.predict_unicorn(startup)
    predictions_cache[request.startup_id] = prediction

    return prediction


@router.get("/predict/{startup_id}", response_model=UnicornPrediction)
async def get_prediction(startup_id: str):
    """Get existing prediction for a startup."""
    if startup_id not in predictions_cache:
        raise HTTPException(404, "Prediction not found. Run /predict first.")
    return predictions_cache[startup_id]


@router.post("/predict/batch", response_model=BatchPrediction)
async def predict_batch(request: ResearchBatchRequest):
    """
    Research and predict for an entire batch.
    """
    engine = get_engine()

    # Research all startups
    startups = await engine.research_batch(request.batch_name, request.company_names)

    # Cache startups
    for s in startups:
        startups_cache[s.id] = s

    # Predict
    batch_prediction = engine.predict_batch(startups, request.batch_name)

    # Cache
    batch_cache[request.batch_name] = batch_prediction
    for p in batch_prediction.startups:
        predictions_cache[p.startup_id] = p

    return batch_prediction


@router.post("/chat")
async def chat_with_prediction(request: ChatRequest):
    """
    Interactive chat about a startup prediction.
    Ask questions, drill down into factors, compare to benchmarks.
    """
    if request.startup_id not in startups_cache:
        raise HTTPException(404, "Startup not found")

    startup = startups_cache[request.startup_id]

    # Get or create prediction
    if request.startup_id not in predictions_cache:
        engine = get_engine()
        prediction = engine.predict_unicorn(startup)
        predictions_cache[request.startup_id] = prediction
    else:
        prediction = predictions_cache[request.startup_id]

    # Chat
    engine = get_engine()
    response = await engine.chat_about_prediction(
        prediction,
        startup,
        request.message,
        request.conversation_history
    )

    return {
        "response": response,
        "startup_name": startup.name,
        "prediction_summary": {
            "unicorn_probability": prediction.unicorn_probability,
            "expected_valuation": prediction.expected_valuation,
        }
    }


@router.get("/list")
async def list_startups():
    """List all researched startups."""
    summaries = []
    seen_ids = set()

    for key, startup in startups_cache.items():
        if startup.id in seen_ids:
            continue
        seen_ids.add(startup.id)

        prediction = predictions_cache.get(startup.id)

        summaries.append(StartupSummary(
            id=startup.id,
            name=startup.name,
            industry=startup.industry,
            stage=startup.current_stage.value,
            unicorn_probability=prediction.unicorn_probability if prediction else None,
            confidence=startup.confidence_score,
        ))

    return {"startups": summaries}


@router.get("/{startup_id}")
async def get_startup(startup_id: str):
    """Get a specific startup."""
    if startup_id not in startups_cache:
        raise HTTPException(404, "Startup not found")

    startup = startups_cache[startup_id]
    prediction = predictions_cache.get(startup_id)

    return {
        "startup": startup,
        "prediction": prediction,
    }


# =============================================================================
# YC-SPECIFIC ENDPOINTS
# =============================================================================

@router.post("/yc/batch")
async def analyze_yc_batch(
    batch_code: str,  # e.g., "W21", "S22"
    max_companies: int = 20
):
    """
    Analyze a Y Combinator batch.
    Discovers companies via Exa, researches them, and predicts outcomes.
    """
    batch_name = f"YC {batch_code}"

    engine = get_engine()

    # Discover companies in batch
    company_names = await engine._discover_batch_companies(batch_name)

    if not company_names:
        raise HTTPException(404, f"Could not find companies for {batch_name}")

    # Limit for demo
    company_names = company_names[:max_companies]

    # Research all
    startups = []
    for name in company_names:
        try:
            startup = await engine.research_startup(name, batch_name)
            startups.append(startup)
            startups_cache[startup.id] = startup
        except Exception as e:
            print(f"Failed to research {name}: {e}")

    if not startups:
        raise HTTPException(500, "Failed to research any companies")

    # Predict
    batch_prediction = engine.predict_batch(startups, batch_name)

    # Cache
    batch_cache[batch_name] = batch_prediction
    for p in batch_prediction.startups:
        predictions_cache[p.startup_id] = p

    return batch_prediction


@router.get("/yc/stats")
async def get_yc_stats():
    """Get Y Combinator historical statistics used for calibration."""
    return {
        "total_companies": 5000,
        "unicorns": 82,
        "unicorn_rate": 0.016,
        "centaur_rate": 0.05,
        "success_rate": 0.15,
        "avg_years_to_unicorn": 7,
        "avg_batch_size": 200,
        "notable_unicorns": [
            {"name": "Airbnb", "valuation": "$75B", "batch": "W09"},
            {"name": "Stripe", "valuation": "$95B", "batch": "S09"},
            {"name": "DoorDash", "valuation": "$71B", "batch": "S13"},
            {"name": "Coinbase", "valuation": "$68B", "batch": "S12"},
            {"name": "Instacart", "valuation": "$39B", "batch": "S12"},
            {"name": "Dropbox", "valuation": "$10B", "batch": "S07"},
            {"name": "Gusto", "valuation": "$10B", "batch": "W12"},
            {"name": "Brex", "valuation": "$12B", "batch": "W17"},
        ],
        "methodology": """
Predictions are based on a factor-based model calibrated on YC historical data:
- Team (30%): Prior exits, experience, domain expertise, network
- Market (25%): TAM size, growth rate, competition, timing
- Traction (20%): Revenue, growth rate, unit economics
- Timing (15%): Market maturity, regulatory environment
- Capital (10%): Funding efficiency, runway

The model converts factor scores to probabilities using a logistic function
calibrated so that average YC companies have ~1.6% unicorn probability,
matching historical rates.
        """
    }
