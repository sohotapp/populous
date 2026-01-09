"""
Simulation API Endpoints

This is the "What-If" interface that makes enterprises pay premium.
Allows running scenarios, sensitivity analysis, and Monte Carlo simulations.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class ScenarioAdjustment(BaseModel):
    """A single parameter adjustment"""
    parameter: str  # "team_score", "market_score", etc.
    adjustment_type: str = "percentage"  # "percentage", "absolute", "override"
    value: float
    rationale: str = ""


class RunScenarioRequest(BaseModel):
    """Request to run a custom scenario"""
    company_name: str
    scenario_name: str
    adjustments: List[ScenarioAdjustment]
    base_prediction: Dict[str, Any]  # The current prediction to adjust


class SensitivityRequest(BaseModel):
    """Request for sensitivity analysis"""
    company_name: str
    parameter: str
    min_value: float = 0.0
    max_value: float = 1.0
    steps: int = 20
    base_prediction: Dict[str, Any]


class MonteCarloRequest(BaseModel):
    """Request for Monte Carlo simulation"""
    company_name: str
    simulations: int = 10000
    factor_uncertainty: Optional[Dict[str, List[float]]] = None  # {"team_score": [0.8, 1.2]}
    base_prediction: Dict[str, Any]
    seed: Optional[int] = None


class StressTestRequest(BaseModel):
    """Request for stress test"""
    company_name: str
    scenario_type: str  # "market_downturn", "competitive_disruption", "execution_crisis", "funding_winter", "custom"
    custom_shocks: Optional[List[Dict[str, Any]]] = None
    base_prediction: Dict[str, Any]


class BullBaseBearRequest(BaseModel):
    """Request for Bull/Base/Bear scenarios"""
    company_name: str
    base_prediction: Dict[str, Any]
    adjustment_pct: float = 20.0  # How much to adjust factors


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/scenario")
async def run_scenario(request: RunScenarioRequest):
    """
    Run a custom what-if scenario.

    Adjust any combination of factors and see the impact on:
    - Unicorn probability
    - Expected valuation
    - Recommendation
    """
    from backend.engine.simulation.scenario_engine import (
        ScenarioEngine, Scenario, ScenarioType, ParameterAdjustment
    )

    engine = ScenarioEngine(
        base_prediction=request.base_prediction,
        company_data={}
    )

    adjustments = [
        ParameterAdjustment(
            parameter_path=adj.parameter,
            adjustment_type=adj.adjustment_type,
            adjustment_value=adj.value,
            rationale=adj.rationale
        )
        for adj in request.adjustments
    ]

    scenario = Scenario(
        scenario_name=request.scenario_name,
        scenario_type=ScenarioType.CUSTOM,
        description=f"Custom scenario for {request.company_name}",
        adjustments=adjustments
    )

    result = engine.run_scenario(scenario)

    return {
        "company_name": request.company_name,
        "scenario_name": result.scenario_name,
        "base_probability": result.base_probability,
        "adjusted_probability": result.adjusted_probability,
        "probability_delta": result.probability_delta,
        "probability_delta_pct": (result.probability_delta / result.base_probability * 100) if result.base_probability else 0,
        "base_valuation": result.base_valuation,
        "adjusted_valuation": result.adjusted_valuation,
        "valuation_delta": result.valuation_delta,
        "base_recommendation": result.base_recommendation,
        "adjusted_recommendation": result.adjusted_recommendation,
        "recommendation_changed": result.recommendation_changed,
        "factor_deltas": result.factor_deltas,
        "impact_summary": result.impact_summary
    }


@router.post("/sensitivity")
async def run_sensitivity(request: SensitivityRequest):
    """
    Run sensitivity analysis on a single parameter.

    Shows how changes in one input affect the output.
    Perfect for understanding which factors matter most.
    """
    from backend.engine.simulation.scenario_engine import ScenarioEngine

    engine = ScenarioEngine(
        base_prediction=request.base_prediction,
        company_data={}
    )

    result = engine.run_sensitivity_analysis(
        parameter=request.parameter,
        min_value=request.min_value,
        max_value=request.max_value,
        steps=request.steps
    )

    return {
        "company_name": request.company_name,
        "parameter": result.parameter,
        "parameter_display_name": result.parameter_display_name,
        "base_value": result.base_value,
        "base_probability": result.base_probability,
        "min_probability": result.min_probability,
        "max_probability": result.max_probability,
        "elasticity": result.elasticity,
        "inflection_points": result.inflection_points,
        "chart_data": {
            "values": result.values,
            "probabilities": result.probabilities
        }
    }


@router.post("/monte-carlo")
async def run_monte_carlo(request: MonteCarloRequest):
    """
    Run Monte Carlo simulation with uncertainty distributions.

    This is what sophisticated investors pay for:
    - Full probability distribution, not just point estimate
    - Confidence intervals
    - Tail risk analysis
    """
    from backend.engine.simulation.scenario_engine import ScenarioEngine

    engine = ScenarioEngine(
        base_prediction=request.base_prediction,
        company_data={}
    )

    # Convert uncertainty format
    factor_uncertainty = None
    if request.factor_uncertainty:
        factor_uncertainty = {
            k: (v[0], v[1])
            for k, v in request.factor_uncertainty.items()
        }

    result = engine.run_monte_carlo(
        simulations=request.simulations,
        factor_uncertainty=factor_uncertainty,
        seed=request.seed
    )

    return {
        "company_name": request.company_name,
        "simulations": result.simulations,
        "distribution_stats": {
            "mean": result.mean_probability,
            "median": result.median_probability,
            "std_dev": result.std_dev,
            "skewness": result.skewness,
            "kurtosis": result.kurtosis
        },
        "percentiles": {
            "p5": result.p5,
            "p10": result.p10,
            "p25": result.p25,
            "p50": result.p50,
            "p75": result.p75,
            "p90": result.p90,
            "p95": result.p95
        },
        "confidence_intervals": {
            "ci_90": list(result.ci_90),
            "ci_95": list(result.ci_95),
            "ci_99": list(result.ci_99)
        },
        "outcome_probabilities": {
            "prob_unicorn": result.prob_unicorn,
            "prob_centaur": result.prob_centaur,
            "prob_success": result.prob_success,
            "prob_failure": result.prob_failure
        },
        "histogram": {
            "bins": result.histogram_bins,
            "counts": result.histogram_counts
        }
    }


@router.post("/stress-test")
async def run_stress_test(request: StressTestRequest):
    """
    Run stress test with correlated shocks.

    Critical for risk management:
    - Market downturn scenarios
    - Competitive disruption
    - Execution crisis
    - Funding winter
    """
    from backend.engine.simulation.scenario_engine import (
        ScenarioEngine,
        create_market_downturn_stress_test,
        create_competitive_disruption_stress_test,
        create_execution_crisis_stress_test,
        create_funding_winter_stress_test
    )

    engine = ScenarioEngine(
        base_prediction=request.base_prediction,
        company_data={}
    )

    # Get shocks based on scenario type
    if request.scenario_type == "market_downturn":
        scenario_name, shocks = create_market_downturn_stress_test()
    elif request.scenario_type == "competitive_disruption":
        scenario_name, shocks = create_competitive_disruption_stress_test()
    elif request.scenario_type == "execution_crisis":
        scenario_name, shocks = create_execution_crisis_stress_test()
    elif request.scenario_type == "funding_winter":
        scenario_name, shocks = create_funding_winter_stress_test()
    elif request.scenario_type == "custom" and request.custom_shocks:
        scenario_name = "Custom Stress Test"
        shocks = request.custom_shocks
    else:
        raise HTTPException(400, "Invalid scenario type or missing custom shocks")

    result = engine.run_stress_test(scenario_name, shocks)

    return {
        "company_name": request.company_name,
        "scenario_name": result.scenario_name,
        "description": result.description,
        "shocks_applied": result.shocks,
        "base_probability": result.base_probability,
        "stressed_probability": result.stressed_probability,
        "probability_drop": result.probability_drop,
        "probability_drop_pct": result.probability_drop_pct,
        "survives_scenario": result.survives_scenario,
        "vulnerability_rating": result.vulnerability_rating,
        "recovery_time_estimate": result.recovery_time_estimate
    }


@router.post("/bull-base-bear")
async def run_bull_base_bear(request: BullBaseBearRequest):
    """
    Run standard Bull/Base/Bear scenario analysis.

    This is the bread-and-butter of investment analysis:
    - Bull case: All factors improve by X%
    - Base case: Current state
    - Bear case: All factors decline by X%
    """
    from backend.engine.simulation.scenario_engine import ScenarioEngine

    engine = ScenarioEngine(
        base_prediction=request.base_prediction,
        company_data={}
    )

    scenarios = engine.create_preset_scenarios()

    return {
        "company_name": request.company_name,
        "scenarios": [
            {
                "name": s.scenario_name,
                "type": s.scenario_type.value if hasattr(s.scenario_type, 'value') else str(s.scenario_type),
                "probability": s.adjusted_probability,
                "probability_delta": s.probability_delta,
                "valuation": s.adjusted_valuation,
                "recommendation": s.adjusted_recommendation
            }
            for s in scenarios
        ]
    }


@router.get("/presets")
async def get_scenario_presets():
    """
    Get available scenario presets and stress tests.

    Helps users understand what simulations are available.
    """
    return {
        "scenario_types": [
            {
                "id": "bull_case",
                "name": "Bull Case",
                "description": "Optimistic scenario with all factors improving"
            },
            {
                "id": "base_case",
                "name": "Base Case",
                "description": "Current state projection"
            },
            {
                "id": "bear_case",
                "name": "Bear Case",
                "description": "Pessimistic scenario with all factors declining"
            }
        ],
        "stress_tests": [
            {
                "id": "market_downturn",
                "name": "Market Downturn",
                "description": "2008/2022-style market crash with -30% market score, -40% timing, -25% capital"
            },
            {
                "id": "competitive_disruption",
                "name": "Competitive Disruption",
                "description": "Major competitor enters with -25% market, -15% traction"
            },
            {
                "id": "execution_crisis",
                "name": "Execution Crisis",
                "description": "Key founder leaves / major pivot with -35% team, -20% traction"
            },
            {
                "id": "funding_winter",
                "name": "Funding Winter",
                "description": "Venture capital pullback with -40% capital, -30% timing"
            }
        ],
        "sensitivity_parameters": [
            {
                "id": "team_score",
                "name": "Team Score",
                "description": "Impact of team quality changes",
                "default_range": [0.0, 1.0]
            },
            {
                "id": "market_score",
                "name": "Market Score",
                "description": "Impact of market opportunity changes",
                "default_range": [0.0, 1.0]
            },
            {
                "id": "traction_score",
                "name": "Traction Score",
                "description": "Impact of traction/revenue changes",
                "default_range": [0.0, 1.0]
            },
            {
                "id": "timing_score",
                "name": "Timing Score",
                "description": "Impact of market timing changes",
                "default_range": [0.0, 1.0]
            },
            {
                "id": "capital_score",
                "name": "Capital Score",
                "description": "Impact of capital efficiency changes",
                "default_range": [0.0, 1.0]
            }
        ]
    }
