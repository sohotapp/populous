"""
Enhanced Startup Prediction Engine
Uses multi-source research, proxy estimation, and calibrated scoring
"""

import os
import math
import asyncio
import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
from dataclasses import dataclass

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

from backend.engine.data_sources import (
    MultiSourceResearchEngine, CompanyData, DataPoint, DataConfidence
)
from backend.engine.proxy_estimator import (
    ProxyEstimator, ScoringEngine, EstimatedMetric
)


# =============================================================================
# OUTPUT MODELS
# =============================================================================

class FactorScore(BaseModel):
    """Detailed factor score with breakdown"""
    name: str
    score: float
    confidence: float
    weight: float
    weighted_contribution: float
    breakdown: Dict
    data_sources: List[str] = []


class PredictionResult(BaseModel):
    """Complete prediction result"""
    startup_id: str
    startup_name: str

    # Probability estimates
    unicorn_probability: float
    centaur_probability: float  # $100M-$1B
    success_probability: float  # Any positive exit
    failure_probability: float

    # Valuation estimates
    expected_valuation: float
    valuation_p10: float
    valuation_p50: float
    valuation_p90: float

    # Timeline
    years_to_unicorn: Optional[float] = None
    years_to_exit: float

    # Factor scores (0-1)
    team_score: float
    market_score: float
    traction_score: float
    timing_score: float
    capital_score: float

    # Detailed breakdowns
    factor_details: List[FactorScore] = []

    # Insights
    key_strengths: List[str] = []
    key_risks: List[str] = []
    detailed_reasoning: str = ""

    # Confidence
    prediction_confidence: float
    data_quality: str  # "high", "medium", "low"
    source_count: int = 0

    # Metadata
    model_version: str = "v2.0"
    researched_at: datetime = Field(default_factory=datetime.now)


class BatchPredictionResult(BaseModel):
    """Batch prediction results"""
    batch_name: str
    batch_size: int
    expected_unicorns: float
    unicorn_range: Tuple[int, int]
    expected_centaurs: float
    expected_total_value: float  # Billions
    batch_quality_score: float
    market_timing_score: float
    startups: List[PredictionResult] = []
    top_unicorn_candidates: List[str] = []
    highest_risk_startups: List[str] = []
    detailed_analysis: Optional[str] = None


# =============================================================================
# PREDICTION ENGINE
# =============================================================================

class EnhancedPredictionEngine:
    """
    Production-grade startup prediction engine

    Features:
    - Multi-source data collection (Exa queries + extraction)
    - Proxy estimation for missing metrics
    - Calibrated scoring (YC historical data)
    - Monte Carlo simulation
    - Confidence intervals
    """

    # Factor weights (calibrated on YC historical data)
    FACTOR_WEIGHTS = {
        "team": 0.30,
        "market": 0.25,
        "traction": 0.20,
        "timing": 0.15,
        "capital": 0.10,
    }

    # YC historical calibration
    YC_BASE_UNICORN_RATE = 0.016  # 1.6%
    YC_BASE_CENTAUR_RATE = 0.05   # 5%
    YC_BASE_SUCCESS_RATE = 0.15   # 15%

    def __init__(self):
        self.researcher = MultiSourceResearchEngine()
        self.estimator = ProxyEstimator()
        self.scorer = ScoringEngine()
        self.llm = Anthropic() if Anthropic and os.environ.get("ANTHROPIC_API_KEY") else None

    async def research_and_predict(self, company_name: str, batch: Optional[str] = None) -> PredictionResult:
        """
        Full pipeline: research -> extract -> estimate -> score -> predict
        """
        # Step 1: Multi-source research
        company_data = await self.researcher.research_company(company_name, batch)

        # Step 2: Estimate missing metrics
        estimates = self.estimator.estimate_all(company_data)

        # Step 3: Score all factors
        scores = self._score_all_factors(company_data, estimates)

        # Step 4: Generate prediction
        prediction = self._generate_prediction(company_name, company_data, scores, estimates)

        # Step 5: Generate insights
        prediction = await self._generate_insights(prediction, company_data, scores)

        return prediction

    async def predict_batch(self, batch_name: str, company_names: List[str]) -> BatchPredictionResult:
        """
        Predict outcomes for an entire batch
        """
        predictions = []

        for name in company_names:
            try:
                pred = await self.research_and_predict(name, batch_name)
                predictions.append(pred)
            except Exception as e:
                print(f"[Batch] Failed to predict {name}: {e}")

        if not predictions:
            raise ValueError(f"No successful predictions for batch {batch_name}")

        # Aggregate statistics
        unicorn_probs = [p.unicorn_probability for p in predictions]
        expected_unicorns = sum(unicorn_probs)

        # Monte Carlo for unicorn range
        ranges = self._simulate_batch_outcomes(unicorn_probs, n_simulations=10000)

        # Expected value (sum of expected valuations)
        total_value = sum(p.expected_valuation for p in predictions) / 1e9  # Billions

        # Batch quality (average of composite scores)
        quality_scores = [
            p.team_score * 0.3 + p.market_score * 0.25 + p.traction_score * 0.2 +
            p.timing_score * 0.15 + p.capital_score * 0.1
            for p in predictions
        ]
        batch_quality = sum(quality_scores) / len(quality_scores)

        # Timing score
        timing_avg = sum(p.timing_score for p in predictions) / len(predictions)

        # Sort by probability
        sorted_preds = sorted(predictions, key=lambda p: p.unicorn_probability, reverse=True)

        return BatchPredictionResult(
            batch_name=batch_name,
            batch_size=len(predictions),
            expected_unicorns=expected_unicorns,
            unicorn_range=ranges,
            expected_centaurs=sum(p.centaur_probability for p in predictions),
            expected_total_value=total_value,
            batch_quality_score=batch_quality,
            market_timing_score=timing_avg,
            startups=predictions,
            top_unicorn_candidates=[p.startup_name for p in sorted_preds[:3]],
            highest_risk_startups=[p.startup_name for p in sorted_preds[-3:] if p.failure_probability > 0.8],
        )

    def _score_all_factors(self, company: CompanyData, estimates: Dict[str, EstimatedMetric]) -> Dict[str, FactorScore]:
        """Score all prediction factors"""
        scores = {}

        # Team score
        team_score, team_conf, team_breakdown = self.scorer.score_team(company)
        scores["team"] = FactorScore(
            name="Team",
            score=team_score,
            confidence=team_conf,
            weight=self.FACTOR_WEIGHTS["team"],
            weighted_contribution=team_score * self.FACTOR_WEIGHTS["team"],
            breakdown=team_breakdown,
            data_sources=["linkedin", "crunchbase", "news"]
        )

        # Market score
        market_score, market_conf, market_breakdown = self.scorer.score_market(company, estimates)
        scores["market"] = FactorScore(
            name="Market",
            score=market_score,
            confidence=market_conf,
            weight=self.FACTOR_WEIGHTS["market"],
            weighted_contribution=market_score * self.FACTOR_WEIGHTS["market"],
            breakdown=market_breakdown,
            data_sources=["industry_reports", "news"]
        )

        # Traction score
        traction_score, traction_conf, traction_breakdown = self.scorer.score_traction(company, estimates)
        scores["traction"] = FactorScore(
            name="Traction",
            score=traction_score,
            confidence=traction_conf,
            weight=self.FACTOR_WEIGHTS["traction"],
            weighted_contribution=traction_score * self.FACTOR_WEIGHTS["traction"],
            breakdown=traction_breakdown,
            data_sources=["company_announcements", "github", "product_hunt"]
        )

        # Timing score
        timing_score, timing_conf, timing_breakdown = self.scorer.score_timing(company)
        scores["timing"] = FactorScore(
            name="Timing",
            score=timing_score,
            confidence=timing_conf,
            weight=self.FACTOR_WEIGHTS["timing"],
            weighted_contribution=timing_score * self.FACTOR_WEIGHTS["timing"],
            breakdown=timing_breakdown,
            data_sources=["market_analysis"]
        )

        # Capital score
        capital_score, capital_conf, capital_breakdown = self.scorer.score_capital(company, estimates)
        scores["capital"] = FactorScore(
            name="Capital",
            score=capital_score,
            confidence=capital_conf,
            weight=self.FACTOR_WEIGHTS["capital"],
            weighted_contribution=capital_score * self.FACTOR_WEIGHTS["capital"],
            breakdown=capital_breakdown,
            data_sources=["crunchbase", "news"]
        )

        return scores

    def _generate_prediction(
        self,
        name: str,
        company: CompanyData,
        scores: Dict[str, FactorScore],
        estimates: Dict[str, EstimatedMetric]
    ) -> PredictionResult:
        """Generate prediction from scores"""

        # Composite score (weighted average)
        composite = sum(s.weighted_contribution for s in scores.values())

        # Average confidence
        avg_confidence = sum(s.confidence * s.weight for s in scores.values())

        # Convert composite to probabilities using logistic function
        # Calibrated so composite=0.5 -> base YC rate
        odds_multiplier = math.exp(4 * (composite - 0.5))

        unicorn_prob = min(0.60, self.YC_BASE_UNICORN_RATE * odds_multiplier)
        centaur_prob = min(0.80, self.YC_BASE_CENTAUR_RATE * odds_multiplier)
        success_prob = min(0.95, self.YC_BASE_SUCCESS_RATE * odds_multiplier)
        failure_prob = 1 - success_prob

        # Valuation estimation
        base_valuation = self._estimate_base_valuation(company, estimates)
        expected_val = base_valuation * (1 + composite)

        # Valuation distribution (log-normal)
        val_std = expected_val * 0.5  # High variance
        val_p10 = expected_val * 0.3
        val_p50 = expected_val * 0.7
        val_p90 = expected_val * 2.5

        # Time to exit
        years_to_exit = 7 - (composite * 3)  # Better companies exit faster

        # Data quality assessment
        if avg_confidence > 0.6:
            data_quality = "high"
        elif avg_confidence > 0.4:
            data_quality = "medium"
        else:
            data_quality = "low"

        # Generate strengths and risks
        strengths, risks = self._identify_strengths_risks(scores)

        return PredictionResult(
            startup_id=f"startup_{hash(name) % 1000000000}",
            startup_name=name,
            unicorn_probability=unicorn_prob,
            centaur_probability=centaur_prob,
            success_probability=success_prob,
            failure_probability=failure_prob,
            expected_valuation=expected_val,
            valuation_p10=val_p10,
            valuation_p50=val_p50,
            valuation_p90=val_p90,
            years_to_unicorn=8 - (composite * 4) if unicorn_prob > 0.05 else None,
            years_to_exit=years_to_exit,
            team_score=scores["team"].score,
            market_score=scores["market"].score,
            traction_score=scores["traction"].score,
            timing_score=scores["timing"].score,
            capital_score=scores["capital"].score,
            factor_details=list(scores.values()),
            key_strengths=strengths,
            key_risks=risks,
            prediction_confidence=avg_confidence,
            data_quality=data_quality,
            source_count=company.source_count,
        )

    def _estimate_base_valuation(self, company: CompanyData, estimates: Dict[str, EstimatedMetric]) -> float:
        """Estimate base valuation"""
        # Start with funding-based estimate
        if company.funding.last_valuation and company.funding.last_valuation.value:
            return company.funding.last_valuation.value

        if "valuation" in estimates:
            return estimates["valuation"].value

        if company.funding.total_raised and company.funding.total_raised.value:
            return company.funding.total_raised.value * 4  # 4x raised

        # Default for early stage
        return 10_000_000

    def _identify_strengths_risks(self, scores: Dict[str, FactorScore]) -> Tuple[List[str], List[str]]:
        """Identify key strengths and risks from scores"""
        strengths = []
        risks = []

        for factor_name, score in scores.items():
            if score.score >= 0.7:
                # Strength
                if factor_name == "team":
                    if score.breakdown.get("note") != "no_founder_data":
                        exits = sum(1 for k, v in score.breakdown.items() if "_exits" in k and v > 0)
                        if exits > 0:
                            strengths.append(f"Experienced team with {exits} prior exit(s)")
                        else:
                            strengths.append("Strong founding team")
                elif factor_name == "market":
                    tam = score.breakdown.get("tam_billions", 0)
                    if tam > 50:
                        strengths.append(f"Large market opportunity (${tam:.0f}B TAM)")
                    else:
                        strengths.append("Favorable market dynamics")
                elif factor_name == "traction":
                    revenue = score.breakdown.get("revenue_annual", 0)
                    if revenue > 1_000_000:
                        strengths.append(f"Strong traction (${revenue/1e6:.1f}M ARR)")
                    else:
                        strengths.append("Growing traction metrics")
                elif factor_name == "timing":
                    if score.breakdown.get("timing") == "hot":
                        strengths.append("Excellent market timing (hot sector)")
                    else:
                        strengths.append("Favorable market timing")
                elif factor_name == "capital":
                    if score.breakdown.get("top_investor"):
                        strengths.append(f"Backed by top-tier investors")
                    elif score.breakdown.get("capital_efficiency", 0) > 0.5:
                        strengths.append("Strong capital efficiency")

            elif score.score <= 0.35:
                # Risk
                if factor_name == "team":
                    risks.append("Limited founder track record data")
                elif factor_name == "market":
                    risks.append("Market opportunity concerns")
                elif factor_name == "traction":
                    risks.append("Limited traction evidence")
                elif factor_name == "timing":
                    if score.breakdown.get("timing") == "cooling":
                        risks.append("Sector timing concerns (cooling market)")
                    else:
                        risks.append("Market timing uncertainty")
                elif factor_name == "capital":
                    risks.append("Capital efficiency concerns")

        # Ensure at least one of each
        if not strengths:
            best = max(scores.values(), key=lambda s: s.score)
            strengths.append(f"Relative strength in {best.name.lower()}")

        if not risks:
            risks.append("Standard early-stage execution risks")

        return strengths[:4], risks[:4]

    async def _generate_insights(
        self,
        prediction: PredictionResult,
        company: CompanyData,
        scores: Dict[str, FactorScore]
    ) -> PredictionResult:
        """Generate detailed AI insights"""

        if not self.llm:
            # Fallback to template
            prediction.detailed_reasoning = self._generate_template_reasoning(prediction, scores)
            return prediction

        # Build context for LLM
        context = f"""
Company: {prediction.startup_name}
Industry: {company.industry.value if company.industry else 'Unknown'}

FACTOR SCORES:
- Team: {prediction.team_score:.0%} (weight: 30%)
- Market: {prediction.market_score:.0%} (weight: 25%)
- Traction: {prediction.traction_score:.0%} (weight: 20%)
- Timing: {prediction.timing_score:.0%} (weight: 15%)
- Capital: {prediction.capital_score:.0%} (weight: 10%)

PREDICTION:
- Unicorn probability: {prediction.unicorn_probability:.1%}
- Expected valuation: ${prediction.expected_valuation/1e6:.1f}M
- Data confidence: {prediction.data_quality}

STRENGTHS: {', '.join(prediction.key_strengths)}
RISKS: {', '.join(prediction.key_risks)}

SCORE BREAKDOWNS:
"""
        for name, score in scores.items():
            context += f"\n{name.upper()}: {score.breakdown}"

        prompt = f"""{context}

Write a 3-4 sentence executive summary of this startup's unicorn potential.
Be specific about:
1. The key factor driving the prediction (positive or negative)
2. What would need to change for a better outcome
3. Comparison to typical YC company (1.6% base unicorn rate)

Keep it concise and actionable."""

        try:
            response = self.llm.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            prediction.detailed_reasoning = response.content[0].text
        except Exception as e:
            print(f"[Insight] LLM error: {e}")
            prediction.detailed_reasoning = self._generate_template_reasoning(prediction, scores)

        return prediction

    def _generate_template_reasoning(self, prediction: PredictionResult, scores: Dict[str, FactorScore]) -> str:
        """Generate template-based reasoning"""
        # Find best and worst factors
        sorted_scores = sorted(scores.items(), key=lambda x: x[1].score, reverse=True)
        best = sorted_scores[0]
        worst = sorted_scores[-1]

        # Determine tier
        if prediction.unicorn_probability > 0.05:
            tier = "above-average"
        elif prediction.unicorn_probability > 0.016:
            tier = "average"
        else:
            tier = "below-average"

        return f"""{prediction.startup_name} shows {tier} unicorn potential with a {prediction.unicorn_probability:.1%} probability of reaching $1B+ valuation.

KEY FACTORS:
- {best[0].capitalize()} Score: {best[1].score:.0%} - {self._score_label(best[1].score)}
- {worst[0].capitalize()} Score: {worst[1].score:.0%} - {self._score_label(worst[1].score)}

STRENGTHS: {', '.join(prediction.key_strengths[:2])}
RISKS: {', '.join(prediction.key_risks[:2])}

Based on YC historical data (82 unicorns from ~5,000 companies), the baseline rate is 1.6%. This company's factor scores place it in the {tier} tier."""

    def _score_label(self, score: float) -> str:
        """Convert score to label"""
        if score >= 0.7:
            return "Strong"
        if score >= 0.5:
            return "Moderate"
        if score >= 0.3:
            return "Developing"
        return "Needs Work"

    def _simulate_batch_outcomes(self, probs: List[float], n_simulations: int = 10000) -> Tuple[int, int]:
        """Monte Carlo simulation for batch unicorn range"""
        outcomes = []
        for _ in range(n_simulations):
            unicorns = sum(1 for p in probs if random.random() < p)
            outcomes.append(unicorns)

        outcomes.sort()
        p10 = outcomes[int(n_simulations * 0.1)]
        p90 = outcomes[int(n_simulations * 0.9)]

        return (p10, p90)

    async def chat_about_prediction(
        self,
        prediction: PredictionResult,
        message: str,
        history: List[Dict] = []
    ) -> str:
        """Interactive chat about a prediction"""

        if not self.llm:
            return "Chat unavailable - no LLM configured"

        # Build context
        context = f"""You are an analyst discussing the startup prediction for {prediction.startup_name}.

PREDICTION SUMMARY:
- Unicorn probability: {prediction.unicorn_probability:.1%}
- Expected valuation: ${prediction.expected_valuation/1e6:.1f}M
- Data confidence: {prediction.data_quality}

FACTOR SCORES:
- Team: {prediction.team_score:.0%} (weight: 30%)
- Market: {prediction.market_score:.0%} (weight: 25%)
- Traction: {prediction.traction_score:.0%} (weight: 20%)
- Timing: {prediction.timing_score:.0%} (weight: 15%)
- Capital: {prediction.capital_score:.0%} (weight: 10%)

KEY STRENGTHS: {', '.join(prediction.key_strengths)}
KEY RISKS: {', '.join(prediction.key_risks)}

DETAILED ANALYSIS: {prediction.detailed_reasoning}

Answer the user's question about this prediction. Be specific and reference the data."""

        messages = [{"role": "system", "content": context}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        try:
            # Convert system message format
            response = self.llm.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                system=context,
                messages=messages[1:]  # Exclude system message
            )
            return response.content[0].text
        except Exception as e:
            return f"Error: {e}"
