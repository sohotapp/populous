"""
Startup Prediction API Routes
Enhanced with multi-source research and calibrated predictions
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio

# Try enhanced engine first, fall back to legacy
try:
    from backend.engine.enhanced_prediction import (
        EnhancedPredictionEngine,
        PredictionResult,
        BatchPredictionResult,
    )
    ENHANCED_ENGINE = True
except ImportError:
    from backend.engine.startup_engine import (
        StartupPredictionEngine,
        Startup,
        UnicornPrediction,
        BatchPrediction,
    )
    ENHANCED_ENGINE = False

router = APIRouter(prefix="/api/startups", tags=["Startups"])

# Global engine instance
_engine = None


def get_engine():
    global _engine
    if _engine is None:
        if ENHANCED_ENGINE:
            _engine = EnhancedPredictionEngine()
        else:
            from backend.engine.startup_engine import StartupPredictionEngine
            _engine = StartupPredictionEngine()
    return _engine


# In-memory caches
predictions_cache: Dict[str, Any] = {}
batch_cache: Dict[str, Any] = {}


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
    industry: Optional[str] = None
    unicorn_probability: Optional[float] = None
    confidence: float
    data_quality: str = "unknown"


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/health")
async def health():
    """Health check for startup prediction service."""
    engine = get_engine()
    return {
        "status": "healthy",
        "engine_type": "enhanced" if ENHANCED_ENGINE else "legacy",
        "exa_available": hasattr(engine, 'researcher') and engine.researcher.exa is not None,
        "llm_available": engine.llm is not None,
        "cached_predictions": len(predictions_cache),
        "cached_batches": len(batch_cache),
    }


@router.post("/research")
async def research_startup(request: ResearchStartupRequest):
    """
    Deep research and prediction for a single startup.
    Uses multi-source Exa queries + Claude extraction + proxy estimation.
    """
    engine = get_engine()

    # Check cache
    cache_key = f"{request.name}:{request.batch or 'none'}"
    if cache_key in predictions_cache:
        return predictions_cache[cache_key]

    try:
        if ENHANCED_ENGINE:
            # Use enhanced pipeline
            prediction = await engine.research_and_predict(request.name, request.batch)
            predictions_cache[cache_key] = prediction
            predictions_cache[prediction.startup_id] = prediction
            return prediction
        else:
            # Legacy engine
            startup = await engine.research_startup(request.name, request.batch)
            prediction = engine.predict_unicorn(startup)
            predictions_cache[cache_key] = prediction
            predictions_cache[prediction.startup_id] = prediction
            return prediction
    except Exception as e:
        raise HTTPException(500, f"Research failed: {str(e)}")


@router.post("/predict")
async def predict_startup(request: PredictStartupRequest):
    """
    Get prediction for a previously researched startup.
    """
    if request.startup_id in predictions_cache:
        return predictions_cache[request.startup_id]

    raise HTTPException(404, f"Startup {request.startup_id} not found. Research it first using /research endpoint.")


@router.get("/predict/{startup_id}")
async def get_prediction(startup_id: str):
    """Get existing prediction for a startup."""
    if startup_id not in predictions_cache:
        raise HTTPException(404, "Prediction not found. Run /research first.")
    return predictions_cache[startup_id]


@router.post("/predict/batch")
async def predict_batch(request: ResearchBatchRequest):
    """
    Research and predict for an entire batch.
    """
    engine = get_engine()

    # Get company names from fallback or request
    company_names = request.company_names

    if not company_names:
        # Use YC batch fallbacks
        YC_BATCH_FALLBACKS = {
            "YC W24": ["Simular", "Greptile", "Artisan AI", "Laminar", "Miru", "Draftaid", "Campana", "Peakflo"],
            "YC S23": ["Wondercraft", "Velt", "Turntable", "Reworkd AI", "Mintlify", "LlamaIndex", "Finch", "Baseten"],
            "YC W23": ["Resend", "Tremor", "Nango", "Firecrawl", "Dub", "Cal.com", "Buildship", "Trigger.dev"],
            "YC S22": ["Replit", "Supabase", "Anthropic", "PostHog", "Retool", "Deel", "Linear", "Railway"],
            "YC W22": ["Airplane", "Stytch", "Neon", "PropelAuth", "Raycast", "Instatus", "Loops", "WorkOS"],
            "YC S21": ["Airbyte", "Ashby", "Contra", "Sprig", "Swimm", "Monte Carlo", "Census", "Merge"],
            "YC W21": ["Merge API", "Clay", "Postscript", "Jeeves", "Gumroad", "Replo", "Slite", "Hive"],
            "YC S20": ["Gather", "Tandem", "ReadMe", "Temporal", "Streamlit", "Scale AI", "Mux", "Loom"],
        }
        company_names = YC_BATCH_FALLBACKS.get(request.batch_name, [])

    if not company_names:
        raise HTTPException(404, f"No companies found for batch {request.batch_name}")

    try:
        if ENHANCED_ENGINE:
            result = await engine.predict_batch(request.batch_name, company_names)
            batch_cache[request.batch_name] = result

            # Cache individual predictions
            for pred in result.startups:
                predictions_cache[pred.startup_id] = pred

            return result
        else:
            # Legacy batch prediction
            startups = await engine.research_batch(request.batch_name, company_names)
            result = engine.predict_batch(startups, request.batch_name)
            batch_cache[request.batch_name] = result
            return result

    except Exception as e:
        raise HTTPException(500, f"Batch prediction failed: {str(e)}")


@router.post("/chat")
async def chat_with_prediction(request: ChatRequest):
    """
    Interactive chat about a startup prediction.
    Ask questions, drill down into factors, compare to benchmarks.
    """
    if request.startup_id not in predictions_cache:
        raise HTTPException(404, "Startup not found. Research it first.")

    prediction = predictions_cache[request.startup_id]
    engine = get_engine()

    try:
        if ENHANCED_ENGINE:
            response = await engine.chat_about_prediction(
                prediction,
                request.message,
                request.conversation_history
            )
        else:
            # Legacy chat
            response = await engine.chat_about_prediction(
                prediction,
                None,  # No startup data in legacy
                request.message,
                request.conversation_history
            )

        return {
            "response": response,
            "startup_name": prediction.startup_name,
            "prediction_summary": {
                "unicorn_probability": prediction.unicorn_probability,
                "expected_valuation": prediction.expected_valuation,
                "data_quality": getattr(prediction, 'data_quality', 'unknown'),
            }
        }
    except Exception as e:
        return {
            "response": f"Chat error: {str(e)}",
            "startup_name": prediction.startup_name,
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

    for key, pred in predictions_cache.items():
        if hasattr(pred, 'startup_id'):
            if pred.startup_id in seen_ids:
                continue
            seen_ids.add(pred.startup_id)

            summaries.append(StartupSummary(
                id=pred.startup_id,
                name=pred.startup_name,
                industry=getattr(pred, 'industry', None),
                unicorn_probability=pred.unicorn_probability,
                confidence=getattr(pred, 'prediction_confidence', 0.5),
                data_quality=getattr(pred, 'data_quality', 'unknown'),
            ))

    return {"startups": summaries}


@router.get("/{startup_id}")
async def get_startup(startup_id: str):
    """Get a specific startup's full prediction."""
    if startup_id not in predictions_cache:
        raise HTTPException(404, "Startup not found")

    return {
        "prediction": predictions_cache[startup_id],
    }


# =============================================================================
# YC-SPECIFIC ENDPOINTS
# =============================================================================

@router.post("/yc/batch")
async def analyze_yc_batch(
    batch_code: str,
    max_companies: int = 10
):
    """
    Analyze a Y Combinator batch.
    Uses fallback company lists + multi-source research.
    """
    batch_name = f"YC {batch_code}"

    # Fallback company lists
    YC_BATCH_FALLBACKS = {
        "YC W24": ["Simular", "Greptile", "Artisan AI", "Laminar", "Miru", "Draftaid", "Campana", "Peakflo", "Orby AI", "Codegen"],
        "YC S23": ["Wondercraft", "Velt", "Turntable", "Reworkd AI", "Mintlify", "LlamaIndex", "Finch", "Copy.ai", "CodeComplete", "Baseten"],
        "YC W23": ["Resend", "Tremor", "Nango", "Firecrawl", "Dub", "Cal.com", "Buildship", "Trigger.dev", "Infisical", "OpenPipe"],
        "YC S22": ["Replit", "Supabase", "Anthropic", "PostHog", "Retool", "Deel", "Linear", "Braintrust", "Railway", "Vercel"],
        "YC W22": ["Airplane", "Stytch", "Neon", "PropelAuth", "Raycast", "Instatus", "Loops", "Knock", "Basedash", "WorkOS"],
        "YC S21": ["Airbyte", "Ashby", "Contra", "Sprig", "Swimm", "Monte Carlo", "Census", "Courier", "Merge", "Modern Treasury"],
        "YC W21": ["Merge API", "Clay", "Postscript", "Arctic Wolf", "Jeeves", "Gumroad", "Replo", "Copilot", "Slite", "Hive"],
        "YC S20": ["Gather", "Tandem", "ReadMe", "Temporal", "Streamlit", "Scale AI", "Mux", "Daily.co", "CodeSandbox", "Loom"],
    }

    company_names = YC_BATCH_FALLBACKS.get(batch_name, [])

    if not company_names:
        raise HTTPException(404, f"Could not find companies for {batch_name}")

    # Limit companies
    company_names = company_names[:max_companies]

    engine = get_engine()

    try:
        if ENHANCED_ENGINE:
            result = await engine.predict_batch(batch_name, company_names)
            batch_cache[batch_name] = result

            # Cache individual predictions
            for pred in result.startups:
                predictions_cache[pred.startup_id] = pred

            return result
        else:
            # Legacy
            startups = []
            for name in company_names:
                try:
                    startup = await engine.research_startup(name, batch_name)
                    startups.append(startup)
                except Exception as e:
                    print(f"Failed to research {name}: {e}")

            if not startups:
                raise HTTPException(500, "Failed to research any companies")

            result = engine.predict_batch(startups, batch_name)
            batch_cache[batch_name] = result

            for p in result.startups:
                predictions_cache[p.startup_id] = p

            return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Batch analysis failed: {str(e)}")


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
Enhanced Prediction Engine v2.0

MULTI-SOURCE RESEARCH:
- 15-20 Exa queries per startup (founders, funding, traction, market)
- Structured data extraction with confidence scoring
- Proxy estimation for missing metrics (revenue from employees, users from GitHub stars)

FACTOR MODEL (calibrated on YC historical data):
- Team (30%): Prior exits, experience, education, network, technical background
- Market (25%): TAM size, growth rate, competition intensity
- Traction (20%): Revenue, users, growth rate, product signals
- Timing (15%): Market cycle, sector heat, macro conditions
- Capital (10%): Funding efficiency, investor quality

CALIBRATION:
- Base unicorn rate: 1.6% (82 unicorns / 5,000 companies)
- Logistic transformation to convert factor scores to probabilities
- Monte Carlo simulation for confidence intervals
        """
    }


@router.get("/methodology")
async def get_methodology():
    """Get detailed methodology documentation."""
    return {
        "version": "2.0",
        "data_sources": {
            "primary": [
                "Exa API (web search)",
                "Claude (data extraction)",
            ],
            "signals": [
                "TechCrunch funding announcements",
                "LinkedIn company pages",
                "GitHub repositories",
                "Product Hunt launches",
                "G2/Capterra reviews",
                "Crunchbase public data",
            ]
        },
        "factor_weights": {
            "team": 0.30,
            "market": 0.25,
            "traction": 0.20,
            "timing": 0.15,
            "capital": 0.10,
        },
        "proxy_estimation": {
            "revenue": "employees × $80-200K/employee (by model/stage)",
            "users": "GitHub stars × 0.2, or G2 reviews × 50",
            "valuation": "funding × 4, or revenue × 12",
            "growth": "stage benchmarks + signal adjustments",
        },
        "confidence_scoring": {
            "high": "Multiple corroborating sources, recent data",
            "medium": "Single source or inferred data",
            "low": "Estimated or old data",
        },
        "calibration": {
            "base_rates": {
                "unicorn": 0.016,
                "centaur": 0.05,
                "success": 0.15,
            },
            "method": "Logistic transformation: P = base_rate × exp(4 × (composite - 0.5))",
        }
    }
