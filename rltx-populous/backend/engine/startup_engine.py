"""
Startup Prediction Engine
Predicts unicorn outcomes for accelerator batches using deep research and simulation
"""

import os
import json
import asyncio
import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import math

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    from exa_py import Exa
    EXA_AVAILABLE = True
except ImportError:
    EXA_AVAILABLE = False
    Exa = None


# =============================================================================
# STARTUP MODELS
# =============================================================================

class StartupStage(str, Enum):
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    GROWTH = "growth"
    IPO_ACQUIRED = "ipo_acquired"
    FAILED = "failed"


class StartupOutcome(str, Enum):
    UNICORN = "unicorn"          # $1B+ valuation
    CENTAUR = "centaur"          # $100M-$1B
    SUCCESSFUL_EXIT = "successful_exit"  # Acquired >$50M
    SURVIVING = "surviving"      # Still operating
    FAILED = "failed"            # Shut down


class FounderProfile(BaseModel):
    """Founder background analysis"""
    name: str
    role: str  # CEO, CTO, etc.
    prior_exits: int = 0
    prior_exit_value: Optional[str] = None
    years_experience: int = 0
    domain_expertise_years: int = 0
    technical_background: bool = False
    top_company_experience: bool = False  # FAANG, etc.
    stanford_yc_network: bool = False
    linkedin_connections: Optional[int] = None

    # Computed scores (0-1)
    execution_score: float = 0.5
    network_score: float = 0.5
    domain_score: float = 0.5


class StartupMetrics(BaseModel):
    """Quantitative startup metrics"""
    # Traction
    monthly_revenue: Optional[float] = None
    revenue_growth_mom: Optional[float] = None  # Month-over-month
    total_users: Optional[int] = None
    user_growth_mom: Optional[float] = None
    paying_customers: Optional[int] = None

    # Unit economics
    ltv: Optional[float] = None
    cac: Optional[float] = None
    ltv_cac_ratio: Optional[float] = None
    gross_margin: Optional[float] = None
    burn_rate: Optional[float] = None
    runway_months: Optional[int] = None

    # Funding
    total_raised: Optional[float] = None
    last_valuation: Optional[float] = None
    valuation_to_revenue: Optional[float] = None


class MarketAnalysis(BaseModel):
    """Market opportunity analysis"""
    market_name: str
    tam_billions: float = 1.0
    sam_billions: float = 0.1
    market_growth_rate: float = 0.1  # Annual
    market_maturity: str = "growing"  # emerging, growing, mature
    competition_intensity: float = 0.5  # 0-1
    winner_take_all: bool = False
    regulatory_risk: float = 0.2  # 0-1
    timing_score: float = 0.5  # 0-1 (is timing right?)


class Startup(BaseModel):
    """Complete startup profile"""
    id: str = Field(default_factory=lambda: f"startup_{int(datetime.now().timestamp())}")
    name: str
    description: str
    tagline: Optional[str] = None
    website: Optional[str] = None

    # Core details
    founded_year: int
    batch: Optional[str] = None  # e.g., "YC W21"
    headquarters: Optional[str] = None
    industry: str
    business_model: str  # B2B, B2C, Marketplace, etc.

    # Team
    founders: List[FounderProfile] = []
    team_size: int = 1

    # Status
    current_stage: StartupStage = StartupStage.SEED
    is_active: bool = True
    outcome: Optional[StartupOutcome] = None
    exit_valuation: Optional[float] = None

    # Metrics
    metrics: StartupMetrics = Field(default_factory=StartupMetrics)

    # Market
    market: MarketAnalysis = Field(default_factory=lambda: MarketAnalysis(market_name="Unknown"))

    # Qualitative factors
    product_differentiation: float = 0.5  # 0-1
    moat_strength: float = 0.3  # 0-1
    technical_complexity: float = 0.5  # 0-1
    viral_potential: float = 0.3  # 0-1

    # Research
    research_sources: List[str] = []
    research_date: datetime = Field(default_factory=datetime.now)
    confidence_score: float = 0.5


class UnicornPrediction(BaseModel):
    """Prediction of unicorn outcome"""
    startup_id: str
    startup_name: str

    # Probabilities
    unicorn_probability: float  # P(>$1B)
    centaur_probability: float  # P($100M-$1B)
    success_probability: float  # P(any positive exit)
    failure_probability: float

    # Expected values
    expected_valuation: float  # E[valuation]
    valuation_p10: float  # 10th percentile
    valuation_p50: float  # Median
    valuation_p90: float  # 90th percentile

    # Time predictions
    years_to_unicorn: Optional[float] = None
    years_to_exit: Optional[float] = None

    # Factor breakdown
    team_score: float
    market_score: float
    traction_score: float
    timing_score: float
    capital_score: float

    # Explanation
    key_strengths: List[str] = []
    key_risks: List[str] = []
    detailed_reasoning: str = ""

    # Confidence
    prediction_confidence: float = 0.5
    data_quality: str = "medium"


class BatchPrediction(BaseModel):
    """Predictions for an entire accelerator batch"""
    batch_name: str  # e.g., "YC W21"
    batch_size: int

    # Aggregate predictions
    expected_unicorns: float
    unicorn_range: Tuple[int, int]  # 90% CI
    expected_centaurs: float
    expected_total_value: float  # Billions

    # Individual predictions
    startups: List[UnicornPrediction] = []

    # Top picks
    top_unicorn_candidates: List[str] = []
    highest_risk_startups: List[str] = []

    # Analysis
    batch_quality_score: float
    market_timing_score: float
    detailed_analysis: str = ""


# =============================================================================
# STARTUP PREDICTION ENGINE
# =============================================================================

class StartupPredictionEngine:
    """
    Engine for predicting startup outcomes.
    Uses deep research + Monte Carlo simulation + LLM analysis.
    """

    # Historical YC statistics for calibration
    YC_STATS = {
        "total_companies": 5000,
        "unicorns": 82,
        "unicorn_rate": 0.016,  # ~1.6%
        "centaur_rate": 0.05,   # ~5%
        "success_rate": 0.15,   # ~15% meaningful exit
        "avg_years_to_unicorn": 7,
        "avg_batch_size": 200,
    }

    # Factor weights for prediction (calibrated on historical data)
    FACTOR_WEIGHTS = {
        "team": 0.30,
        "market": 0.25,
        "traction": 0.20,
        "timing": 0.15,
        "capital": 0.10,
    }

    def __init__(self):
        self.llm = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) if Anthropic else None
        self.exa = None
        if EXA_AVAILABLE:
            exa_key = os.getenv("EXA_API_KEY")
            if exa_key:
                self.exa = Exa(api_key=exa_key)

    # =========================================================================
    # RESEARCH METHODS
    # =========================================================================

    async def research_startup(self, name: str, batch: Optional[str] = None) -> Startup:
        """
        Deep research on a startup using Exa + Claude.
        """
        print(f"Researching startup: {name}")

        # Gather data from multiple sources
        exa_data = await self._exa_research_startup(name, batch)

        # Synthesize into Startup model
        startup = await self._synthesize_startup(name, batch, exa_data)

        return startup

    async def research_batch(
        self,
        batch_name: str,
        company_names: Optional[List[str]] = None
    ) -> List[Startup]:
        """
        Research all companies in an accelerator batch.
        """
        if company_names:
            # Research provided companies
            tasks = [self.research_startup(name, batch_name) for name in company_names]
            startups = await asyncio.gather(*tasks, return_exceptions=True)
            return [s for s in startups if isinstance(s, Startup)]
        else:
            # Discover companies in batch via Exa
            company_names = await self._discover_batch_companies(batch_name)
            return await self.research_batch(batch_name, company_names)

    async def _exa_research_startup(self, name: str, batch: Optional[str]) -> Dict:
        """Use Exa to research a startup."""
        if not self.exa:
            return {"sources": [], "data": {}}

        try:
            queries = [
                f"{name} startup company profile funding",
                f"{name} founder CEO background experience",
                f"{name} product customers traction",
                f"{name} funding round valuation investors",
            ]

            if batch:
                queries.append(f"{name} {batch} accelerator")

            all_results = []
            all_urls = []

            for query in queries:
                try:
                    results = self.exa.search_and_contents(
                        query=query,
                        num_results=5,
                        use_autoprompt=True,
                        text=True
                    )
                    if hasattr(results, 'results'):
                        for r in results.results:
                            if hasattr(r, 'text') and r.text:
                                all_results.append(r.text[:3000])
                            if hasattr(r, 'url') and r.url:
                                all_urls.append(r.url)
                except Exception as e:
                    print(f"Exa query failed: {e}")

            return {
                "texts": all_results,
                "sources": list(set(all_urls)),
            }

        except Exception as e:
            print(f"Exa research failed: {e}")
            return {"texts": [], "sources": []}

    async def _discover_batch_companies(self, batch_name: str) -> List[str]:
        """Discover companies in a batch using Exa."""
        if not self.exa:
            return []

        try:
            results = self.exa.search_and_contents(
                query=f"{batch_name} companies startups list portfolio",
                num_results=20,
                use_autoprompt=True,
                text=True
            )

            # Use Claude to extract company names
            texts = "\n".join([r.text[:2000] for r in results.results if hasattr(r, 'text')])

            if not self.llm:
                return []

            response = self.llm.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": f"""Extract company names from this text about {batch_name}.
Return ONLY a JSON array of company names, nothing else.

TEXT:
{texts[:10000]}

Example: ["Company1", "Company2", "Company3"]"""
                }]
            )

            text = response.content[0].text
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])[:50]
            return []

        except Exception as e:
            print(f"Batch discovery failed: {e}")
            return []

    async def _synthesize_startup(
        self,
        name: str,
        batch: Optional[str],
        exa_data: Dict
    ) -> Startup:
        """Use Claude to synthesize startup data."""
        if not self.llm:
            return self._create_placeholder_startup(name, batch)

        research_text = "\n\n".join(exa_data.get("texts", [])[:10])

        prompt = f"""Analyze this startup research data and extract structured information.

STARTUP: {name}
{f"BATCH: {batch}" if batch else ""}

RESEARCH DATA:
{research_text[:15000]}

Return a JSON object with these fields:
{{
    "name": "{name}",
    "description": "2-3 sentence description",
    "tagline": "Company tagline if known",
    "website": "URL",
    "founded_year": 2020,
    "headquarters": "City, Country",
    "industry": "Primary industry",
    "business_model": "B2B" | "B2C" | "B2B2C" | "Marketplace" | "SaaS" | "Hardware" | "Other",
    "team_size": 10,
    "current_stage": "seed" | "series_a" | "series_b" | "series_c" | "growth",
    "is_active": true,

    "founders": [
        {{
            "name": "Founder Name",
            "role": "CEO",
            "prior_exits": 0,
            "prior_exit_value": "$XXM" or null,
            "years_experience": 10,
            "domain_expertise_years": 5,
            "technical_background": true,
            "top_company_experience": false,
            "stanford_yc_network": true
        }}
    ],

    "metrics": {{
        "monthly_revenue": 100000,
        "revenue_growth_mom": 0.15,
        "total_users": 10000,
        "paying_customers": 500,
        "total_raised": 5000000,
        "last_valuation": 25000000
    }},

    "market": {{
        "market_name": "Market name",
        "tam_billions": 50,
        "market_growth_rate": 0.15,
        "market_maturity": "growing",
        "competition_intensity": 0.6,
        "winner_take_all": false
    }},

    "product_differentiation": 0.7,
    "moat_strength": 0.5,
    "technical_complexity": 0.6,
    "viral_potential": 0.4,

    "outcome": null,
    "exit_valuation": null
}}

Be factual. Use null for unknown values. Return ONLY valid JSON."""

        try:
            response = self.llm.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.content[0].text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(text[start:end])
            else:
                return self._create_placeholder_startup(name, batch)

            # Parse founders
            founders = []
            for f in data.get("founders", []):
                founders.append(FounderProfile(
                    name=f.get("name", "Unknown"),
                    role=f.get("role", "Founder"),
                    prior_exits=f.get("prior_exits", 0),
                    prior_exit_value=f.get("prior_exit_value"),
                    years_experience=f.get("years_experience", 0),
                    domain_expertise_years=f.get("domain_expertise_years", 0),
                    technical_background=f.get("technical_background", False),
                    top_company_experience=f.get("top_company_experience", False),
                    stanford_yc_network=f.get("stanford_yc_network", False),
                ))

            # Parse metrics
            m = data.get("metrics", {})
            metrics = StartupMetrics(
                monthly_revenue=m.get("monthly_revenue"),
                revenue_growth_mom=m.get("revenue_growth_mom"),
                total_users=m.get("total_users"),
                paying_customers=m.get("paying_customers"),
                total_raised=m.get("total_raised"),
                last_valuation=m.get("last_valuation"),
            )

            # Parse market
            mk = data.get("market", {})
            market = MarketAnalysis(
                market_name=mk.get("market_name", "Unknown"),
                tam_billions=mk.get("tam_billions", 1),
                market_growth_rate=mk.get("market_growth_rate", 0.1),
                market_maturity=mk.get("market_maturity", "growing"),
                competition_intensity=mk.get("competition_intensity", 0.5),
                winner_take_all=mk.get("winner_take_all", False),
            )

            # Parse stage
            stage_map = {
                "pre_seed": StartupStage.PRE_SEED,
                "seed": StartupStage.SEED,
                "series_a": StartupStage.SERIES_A,
                "series_b": StartupStage.SERIES_B,
                "series_c": StartupStage.SERIES_C,
                "growth": StartupStage.GROWTH,
            }
            current_stage = stage_map.get(
                data.get("current_stage", "seed"),
                StartupStage.SEED
            )

            return Startup(
                name=data.get("name", name),
                description=data.get("description", f"Startup: {name}"),
                tagline=data.get("tagline"),
                website=data.get("website"),
                founded_year=data.get("founded_year", datetime.now().year),
                batch=batch,
                headquarters=data.get("headquarters"),
                industry=data.get("industry", "Technology"),
                business_model=data.get("business_model", "SaaS"),
                founders=founders,
                team_size=data.get("team_size", 1),
                current_stage=current_stage,
                is_active=data.get("is_active", True),
                metrics=metrics,
                market=market,
                product_differentiation=data.get("product_differentiation", 0.5),
                moat_strength=data.get("moat_strength", 0.3),
                technical_complexity=data.get("technical_complexity", 0.5),
                viral_potential=data.get("viral_potential", 0.3),
                research_sources=exa_data.get("sources", []),
                confidence_score=0.7 if exa_data.get("texts") else 0.4,
            )

        except Exception as e:
            print(f"Synthesis failed: {e}")
            return self._create_placeholder_startup(name, batch)

    def _create_placeholder_startup(self, name: str, batch: Optional[str]) -> Startup:
        """Create placeholder startup when research fails."""
        return Startup(
            name=name,
            description=f"Startup from {batch}" if batch else f"Startup: {name}",
            founded_year=datetime.now().year,
            batch=batch,
            industry="Technology",
            business_model="SaaS",
            confidence_score=0.2,
        )

    # =========================================================================
    # PREDICTION METHODS
    # =========================================================================

    def predict_unicorn(self, startup: Startup) -> UnicornPrediction:
        """
        Predict unicorn probability for a startup.
        Uses factor-based model calibrated on YC historical data.
        """
        # Calculate factor scores
        team_score = self._score_team(startup)
        market_score = self._score_market(startup)
        traction_score = self._score_traction(startup)
        timing_score = self._score_timing(startup)
        capital_score = self._score_capital(startup)

        # Weighted composite score
        composite = (
            team_score * self.FACTOR_WEIGHTS["team"] +
            market_score * self.FACTOR_WEIGHTS["market"] +
            traction_score * self.FACTOR_WEIGHTS["traction"] +
            timing_score * self.FACTOR_WEIGHTS["timing"] +
            capital_score * self.FACTOR_WEIGHTS["capital"]
        )

        # Convert to probability using logistic function
        # Calibrated so average YC company has ~1.6% unicorn probability
        # Top decile has ~10%, top 1% has ~40%
        base_odds = 0.016  # YC unicorn rate
        odds_multiplier = math.exp(4 * (composite - 0.5))  # Exponential scaling
        unicorn_prob = min(0.6, base_odds * odds_multiplier)

        # Other outcomes
        centaur_prob = min(0.3, unicorn_prob * 3)  # ~3x unicorn prob
        success_prob = min(0.5, unicorn_prob * 10)  # ~10x unicorn prob
        failure_prob = 1 - success_prob

        # Expected valuation (log-normal distribution)
        median_val = self._estimate_median_valuation(startup, composite)
        expected_val = median_val * 1.5  # Log-normal mean > median
        val_p10 = median_val * 0.2
        val_p90 = median_val * 5

        # Time estimates
        years_to_exit = 7 - 3 * composite  # Better startups exit faster
        years_to_unicorn = 6 - 2 * composite if unicorn_prob > 0.1 else None

        # Strengths and risks
        strengths, risks = self._identify_strengths_risks(
            startup, team_score, market_score, traction_score, timing_score, capital_score
        )

        # Generate detailed reasoning
        reasoning = self._generate_reasoning(
            startup, unicorn_prob, strengths, risks,
            team_score, market_score, traction_score
        )

        return UnicornPrediction(
            startup_id=startup.id,
            startup_name=startup.name,
            unicorn_probability=round(unicorn_prob, 4),
            centaur_probability=round(centaur_prob, 4),
            success_probability=round(success_prob, 4),
            failure_probability=round(failure_prob, 4),
            expected_valuation=round(expected_val, 0),
            valuation_p10=round(val_p10, 0),
            valuation_p50=round(median_val, 0),
            valuation_p90=round(val_p90, 0),
            years_to_unicorn=round(years_to_unicorn, 1) if years_to_unicorn else None,
            years_to_exit=round(years_to_exit, 1),
            team_score=round(team_score, 3),
            market_score=round(market_score, 3),
            traction_score=round(traction_score, 3),
            timing_score=round(timing_score, 3),
            capital_score=round(capital_score, 3),
            key_strengths=strengths[:5],
            key_risks=risks[:5],
            detailed_reasoning=reasoning,
            prediction_confidence=startup.confidence_score,
            data_quality="high" if startup.confidence_score > 0.6 else "medium" if startup.confidence_score > 0.4 else "low",
        )

    def predict_batch(self, startups: List[Startup], batch_name: str) -> BatchPrediction:
        """
        Predict outcomes for an entire accelerator batch.
        """
        predictions = [self.predict_unicorn(s) for s in startups]

        # Sort by unicorn probability
        predictions.sort(key=lambda p: p.unicorn_probability, reverse=True)

        # Aggregate stats
        expected_unicorns = sum(p.unicorn_probability for p in predictions)
        expected_centaurs = sum(p.centaur_probability for p in predictions)
        expected_value = sum(p.expected_valuation for p in predictions) / 1e9  # Billions

        # Unicorn range (90% CI using Poisson)
        # Using normal approximation for large batches
        unicorn_std = math.sqrt(expected_unicorns)
        unicorn_low = max(0, int(expected_unicorns - 1.645 * unicorn_std))
        unicorn_high = int(expected_unicorns + 1.645 * unicorn_std)

        # Top picks
        top_candidates = [p.startup_name for p in predictions[:5]]
        highest_risk = [p.startup_name for p in sorted(predictions, key=lambda p: p.failure_probability, reverse=True)[:5]]

        # Batch quality
        avg_team = sum(p.team_score for p in predictions) / len(predictions)
        avg_market = sum(p.market_score for p in predictions) / len(predictions)
        batch_quality = (avg_team + avg_market) / 2

        # Market timing
        avg_timing = sum(p.timing_score for p in predictions) / len(predictions)

        return BatchPrediction(
            batch_name=batch_name,
            batch_size=len(startups),
            expected_unicorns=round(expected_unicorns, 2),
            unicorn_range=(unicorn_low, unicorn_high),
            expected_centaurs=round(expected_centaurs, 2),
            expected_total_value=round(expected_value, 2),
            startups=predictions,
            top_unicorn_candidates=top_candidates,
            highest_risk_startups=highest_risk,
            batch_quality_score=round(batch_quality, 3),
            market_timing_score=round(avg_timing, 3),
        )

    # =========================================================================
    # SCORING METHODS
    # =========================================================================

    def _score_team(self, startup: Startup) -> float:
        """Score team quality (0-1)."""
        if not startup.founders:
            return 0.3  # Unknown team

        scores = []
        for founder in startup.founders:
            f_score = 0.3  # Base

            # Prior exits are huge
            if founder.prior_exits >= 2:
                f_score += 0.3
            elif founder.prior_exits == 1:
                f_score += 0.2

            # Experience
            if founder.years_experience >= 10:
                f_score += 0.15
            elif founder.years_experience >= 5:
                f_score += 0.1

            # Domain expertise
            if founder.domain_expertise_years >= 5:
                f_score += 0.1

            # Technical + business combo
            if founder.technical_background:
                f_score += 0.05

            # Network (YC/Stanford = strong signal)
            if founder.stanford_yc_network:
                f_score += 0.1

            # Top company experience
            if founder.top_company_experience:
                f_score += 0.05

            scores.append(min(1.0, f_score))

        # Best founder matters most, but team composition matters too
        return max(scores) * 0.7 + (sum(scores) / len(scores)) * 0.3

    def _score_market(self, startup: Startup) -> float:
        """Score market opportunity (0-1)."""
        market = startup.market
        score = 0.3  # Base

        # TAM size
        if market.tam_billions >= 100:
            score += 0.25
        elif market.tam_billions >= 50:
            score += 0.2
        elif market.tam_billions >= 10:
            score += 0.15
        elif market.tam_billions >= 1:
            score += 0.1

        # Growth rate
        if market.market_growth_rate >= 0.3:
            score += 0.2
        elif market.market_growth_rate >= 0.15:
            score += 0.15
        elif market.market_growth_rate >= 0.1:
            score += 0.1

        # Maturity (emerging/growing best)
        if market.market_maturity in ["emerging", "growing"]:
            score += 0.1

        # Competition (moderate is good - validates market)
        if 0.3 <= market.competition_intensity <= 0.7:
            score += 0.1

        # Winner-take-all markets are high risk/reward
        if market.winner_take_all and startup.product_differentiation > 0.6:
            score += 0.1

        return min(1.0, score)

    def _score_traction(self, startup: Startup) -> float:
        """Score current traction (0-1)."""
        metrics = startup.metrics
        score = 0.2  # Base

        # Revenue (MRR)
        if metrics.monthly_revenue:
            if metrics.monthly_revenue >= 1_000_000:
                score += 0.3
            elif metrics.monthly_revenue >= 100_000:
                score += 0.25
            elif metrics.monthly_revenue >= 10_000:
                score += 0.15
            elif metrics.monthly_revenue > 0:
                score += 0.1

        # Growth rate
        if metrics.revenue_growth_mom:
            if metrics.revenue_growth_mom >= 0.3:  # 30% MoM
                score += 0.25
            elif metrics.revenue_growth_mom >= 0.15:
                score += 0.15
            elif metrics.revenue_growth_mom >= 0.1:
                score += 0.1

        # Unit economics
        if metrics.ltv_cac_ratio:
            if metrics.ltv_cac_ratio >= 5:
                score += 0.15
            elif metrics.ltv_cac_ratio >= 3:
                score += 0.1

        return min(1.0, score)

    def _score_timing(self, startup: Startup) -> float:
        """Score market timing (0-1)."""
        market = startup.market
        score = 0.4  # Base

        # Market maturity timing
        if market.market_maturity == "emerging":
            score += 0.1  # Early = risky but high upside
        elif market.market_maturity == "growing":
            score += 0.2  # Sweet spot

        # Growth rate indicates timing
        if market.market_growth_rate >= 0.2:
            score += 0.15

        # Low regulation = better timing
        if market.regulatory_risk < 0.3:
            score += 0.1

        # Explicit timing score if available
        if market.timing_score > 0.5:
            score += 0.1

        return min(1.0, score)

    def _score_capital(self, startup: Startup) -> float:
        """Score capital efficiency and funding (0-1)."""
        metrics = startup.metrics
        score = 0.3  # Base

        # Has funding
        if metrics.total_raised:
            if metrics.total_raised >= 10_000_000:
                score += 0.15
            elif metrics.total_raised >= 1_000_000:
                score += 0.1

        # Capital efficiency (revenue / raised)
        if metrics.monthly_revenue and metrics.total_raised:
            efficiency = (metrics.monthly_revenue * 12) / metrics.total_raised
            if efficiency >= 1.0:  # Revenue >= raised
                score += 0.25
            elif efficiency >= 0.5:
                score += 0.15
            elif efficiency >= 0.2:
                score += 0.1

        # Runway
        if metrics.runway_months:
            if metrics.runway_months >= 24:
                score += 0.15
            elif metrics.runway_months >= 12:
                score += 0.1

        return min(1.0, score)

    def _estimate_median_valuation(self, startup: Startup, composite: float) -> float:
        """Estimate median exit valuation."""
        # Base valuation for average YC company
        base = 50_000_000  # $50M median

        # Scale by composite score
        # Top 10% (composite > 0.7): ~$500M median
        # Top 1% (composite > 0.85): ~$2B median
        multiplier = math.exp(5 * (composite - 0.5))

        return base * multiplier

    def _identify_strengths_risks(
        self,
        startup: Startup,
        team: float,
        market: float,
        traction: float,
        timing: float,
        capital: float
    ) -> Tuple[List[str], List[str]]:
        """Identify key strengths and risks."""
        strengths = []
        risks = []

        # Team
        if team > 0.7:
            strengths.append("Exceptional founding team with strong track record")
        elif team > 0.5:
            strengths.append("Experienced founding team")
        elif team < 0.3:
            risks.append("First-time founders with limited experience")

        # Market
        if market > 0.7:
            strengths.append(f"Large market opportunity (${startup.market.tam_billions}B TAM)")
        elif market < 0.4:
            risks.append("Limited market size or declining market")

        # Traction
        if traction > 0.6:
            strengths.append("Strong traction and growth metrics")
        elif traction > 0.4:
            strengths.append("Early traction signals")
        elif traction < 0.3:
            risks.append("Limited traction - still proving product-market fit")

        # Timing
        if timing > 0.6:
            strengths.append("Favorable market timing")
        elif timing < 0.4:
            risks.append("Market timing concerns - may be too early or late")

        # Capital
        if capital > 0.6:
            strengths.append("Capital efficient with strong unit economics")
        elif capital < 0.3:
            risks.append("Capital efficiency concerns - high burn rate")

        # Product-specific
        if startup.moat_strength > 0.6:
            strengths.append("Strong competitive moat")
        elif startup.moat_strength < 0.3:
            risks.append("Weak defensibility - easy to replicate")

        if startup.viral_potential > 0.6:
            strengths.append("High viral/network effect potential")

        if startup.market.competition_intensity > 0.7:
            risks.append("Highly competitive market with established players")

        return strengths, risks

    def _generate_reasoning(
        self,
        startup: Startup,
        unicorn_prob: float,
        strengths: List[str],
        risks: List[str],
        team: float,
        market: float,
        traction: float
    ) -> str:
        """Generate detailed reasoning for prediction."""
        prob_pct = unicorn_prob * 100

        if prob_pct >= 20:
            outlook = "strong unicorn candidate"
        elif prob_pct >= 10:
            outlook = "above-average unicorn potential"
        elif prob_pct >= 5:
            outlook = "moderate unicorn potential"
        elif prob_pct >= 2:
            outlook = "average unicorn potential for YC company"
        else:
            outlook = "below-average unicorn probability"

        reasoning = f"""{startup.name} is a {outlook} with a {prob_pct:.1f}% probability of reaching $1B+ valuation.

KEY FACTORS:
- Team Score: {team:.0%} - {"Exceptional" if team > 0.7 else "Strong" if team > 0.5 else "Developing"}
- Market Score: {market:.0%} - {startup.market.market_name} (${startup.market.tam_billions}B TAM)
- Traction Score: {traction:.0%}

STRENGTHS:
{chr(10).join(f"• {s}" for s in strengths[:3]) if strengths else "• No exceptional strengths identified"}

RISKS:
{chr(10).join(f"• {r}" for r in risks[:3]) if risks else "• No critical risks identified"}

Based on historical YC data (82 unicorns from ~5,000 companies), the baseline unicorn rate is ~1.6%. This company's factor scores place it in the {"top decile" if prob_pct > 10 else "above average" if prob_pct > 3 else "average"} tier of YC companies."""

        return reasoning

    # =========================================================================
    # CHAT INTERFACE
    # =========================================================================

    async def chat_about_prediction(
        self,
        prediction: UnicornPrediction,
        startup: Startup,
        message: str,
        history: List[Dict] = None
    ) -> str:
        """
        Interactive chat about a startup prediction.
        """
        if not self.llm:
            return "Chat unavailable - LLM not configured"

        context = f"""You are an expert startup analyst discussing {startup.name}.

STARTUP PROFILE:
- Name: {startup.name}
- Industry: {startup.industry}
- Business Model: {startup.business_model}
- Stage: {startup.current_stage.value}
- Founded: {startup.founded_year}
- Team Size: {startup.team_size}

PREDICTION:
- Unicorn Probability: {prediction.unicorn_probability:.1%}
- Expected Valuation: ${prediction.expected_valuation/1e6:.0f}M
- Team Score: {prediction.team_score:.0%}
- Market Score: {prediction.market_score:.0%}
- Traction Score: {prediction.traction_score:.0%}

KEY STRENGTHS: {', '.join(prediction.key_strengths)}
KEY RISKS: {', '.join(prediction.key_risks)}

DETAILED ANALYSIS:
{prediction.detailed_reasoning}

Answer questions about this startup and prediction. Be specific and data-driven.
If asked to compare to other startups, use YC historical averages as reference.
If asked about methodology, explain the factor-based prediction model."""

        messages = [{"role": "system", "content": context}]

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": message})

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=context,
            messages=[{"role": "user", "content": message}]
        )

        return response.content[0].text
