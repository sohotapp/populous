"""
Node Schemas - Typed data contracts for the Decision Intelligence Graph

Every node has:
- Typed inputs (what it needs from upstream)
- Typed outputs (what it produces for downstream)
- Dependencies (which nodes must run first)

Data flows through the graph, accumulating in GraphState.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class DataConfidence(str, Enum):
    HIGH = "high"       # Multiple corroborating sources, recent data
    MEDIUM = "medium"   # Single source or inferred
    LOW = "low"         # Estimated or old data
    UNKNOWN = "unknown" # No data available


class MarketPhase(str, Enum):
    NASCENT = "nascent"
    EMERGING = "emerging"
    GROWTH = "growth"
    MATURE = "mature"
    DECLINING = "declining"


class Recommendation(str, Enum):
    STRONG_INVEST = "STRONG_INVEST"
    INVEST = "INVEST"
    MONITOR = "MONITOR"
    PASS = "PASS"


class ExitType(str, Enum):
    IPO = "ipo"
    STRATEGIC_ACQUISITION = "strategic_acquisition"
    ACQUI_HIRE = "acqui_hire"
    PE_BUYOUT = "pe_buyout"
    FAILURE = "failure"


# =============================================================================
# CORE DATA TYPES (Shared across nodes)
# =============================================================================

class DataPoint(BaseModel):
    """A single data point with confidence and source tracking"""
    value: Any
    confidence: DataConfidence = DataConfidence.UNKNOWN
    source: str = ""
    source_url: Optional[str] = None
    extracted_at: datetime = Field(default_factory=datetime.now)
    raw_text: Optional[str] = None  # Evidence quote


class Founder(BaseModel):
    """Founder profile"""
    name: str
    role: str = ""
    linkedin_url: Optional[str] = None
    prior_companies: List[str] = []
    prior_exits: int = 0
    prior_exit_value_usd: float = 0
    years_experience: int = 0
    years_domain_experience: int = 0
    education: str = ""
    education_tier: int = 3  # 1=top, 2=good, 3=other
    linkedin_connections: int = 0
    confidence: DataConfidence = DataConfidence.UNKNOWN


class FundingRound(BaseModel):
    """Single funding round"""
    round_type: str  # seed, series_a, etc.
    amount_usd: float = 0
    date: Optional[str] = None
    valuation_usd: float = 0
    lead_investor: str = ""
    investors: List[str] = []
    confidence: DataConfidence = DataConfidence.UNKNOWN


class Competitor(BaseModel):
    """Competitor profile"""
    name: str
    funding_total_usd: float = 0
    employee_count: int = 0
    market_position: str = ""  # leader, challenger, niche
    threat_level: str = "medium"  # high, medium, low
    differentiators: List[str] = []


# =============================================================================
# NODE INPUT SCHEMAS
# =============================================================================

class BatchInput(BaseModel):
    """Input for batch analysis node"""
    batch_code: str  # e.g., "W24"
    max_companies: int = 10
    accelerator: str = "YC"


class ResearchInput(BaseModel):
    """Input for deep research node"""
    company_name: str
    batch_context: Optional[str] = None
    existing_data: Dict[str, Any] = {}  # Data from previous nodes


class MarketScannerInput(BaseModel):
    """Input for market intelligence node"""
    sector: str
    companies: List[str] = []
    time_window_days: int = 90


class AlternativeDataInput(BaseModel):
    """Input for alternative signals node"""
    company_name: str
    company_website: Optional[str] = None
    github_org: Optional[str] = None


class FinancialSignalsInput(BaseModel):
    """Input for financial benchmarks node"""
    sector: str
    stage: str = "seed"
    geography: str = "US"
    current_revenue: Optional[float] = None


class NetworkGraphInput(BaseModel):
    """Input for relationship mapping node"""
    companies: List[str]
    founders: List[Founder] = []
    investors: List[str] = []


class PredictionInput(BaseModel):
    """Input for prediction node - receives accumulated state"""
    company_name: str

    # From research
    founders: List[Founder] = []
    funding_rounds: List[FundingRound] = []
    revenue_estimate: Optional[float] = None
    employee_count: Optional[int] = None
    founded_year: Optional[int] = None

    # From market_scanner
    market_phase: MarketPhase = MarketPhase.GROWTH
    market_sentiment: float = 0.5
    sector_funding_velocity: float = 0.0

    # From alternative_data
    github_stars: int = 0
    github_contributors: int = 0
    hiring_velocity: str = "unknown"
    open_positions: int = 0
    web_traffic_monthly: int = 0

    # From financial_signals
    revenue_multiple_benchmark: float = 10.0
    median_seed_valuation: float = 12000000
    sector_benchmarks: Dict[str, float] = {}

    # From network_graph
    investor_tier_avg: float = 0.5
    network_density: float = 0.0
    common_investor_count: int = 0

    # From historical_outcomes (calibration)
    base_unicorn_rate: float = 0.016
    base_success_rate: float = 0.15
    factor_correlations: Dict[str, float] = {}


class MonteCarloInput(BaseModel):
    """Input for Monte Carlo simulation"""
    prediction_scores: Dict[str, float]  # team, market, traction, timing, capital
    expected_valuation: float
    unicorn_probability: float
    factor_uncertainties: Dict[str, float] = {}
    simulations: int = 10000


class SensitivityInput(BaseModel):
    """Input for sensitivity analysis"""
    prediction_scores: Dict[str, float]
    base_unicorn_probability: float
    range_pct: float = 0.20


# =============================================================================
# NODE OUTPUT SCHEMAS
# =============================================================================

class BatchOutput(BaseModel):
    """Output from batch node"""
    batch_name: str
    companies: List[str]
    batch_size: int
    batch_theme: str = ""
    accelerator: str = "YC"


class ResearchOutput(BaseModel):
    """Output from research node - comprehensive company data"""
    company_name: str
    description: str = ""
    website: Optional[str] = None
    industry: str = ""
    founded_year: Optional[int] = None
    headquarters: str = ""
    employee_count: Optional[int] = None

    # Team
    founders: List[Founder] = []
    team_size: int = 0

    # Funding
    funding_rounds: List[FundingRound] = []
    total_raised: float = 0
    last_valuation: float = 0
    last_round_date: Optional[str] = None

    # Traction
    revenue_estimate: Optional[float] = None
    revenue_confidence: DataConfidence = DataConfidence.UNKNOWN
    users_estimate: Optional[int] = None
    growth_rate: Optional[float] = None

    # Product
    product_signals: List[str] = []  # PMF indicators
    tech_stack: List[str] = []

    # Sources
    source_count: int = 0
    data_quality: DataConfidence = DataConfidence.UNKNOWN


class MarketScannerOutput(BaseModel):
    """Output from market scanner"""
    sector: str
    market_phase: MarketPhase
    market_sentiment: float  # 0-1
    sector_funding_velocity: float  # % change
    recent_deals: List[Dict[str, Any]] = []
    key_trends: List[str] = []
    competitor_moves: List[Dict[str, Any]] = []
    timing_score_adjustment: float = 0.0  # How much to adjust timing factor


class AlternativeDataOutput(BaseModel):
    """Output from alternative data node"""
    company_name: str

    # GitHub signals
    github_repos: int = 0
    github_stars: int = 0
    github_contributors: int = 0
    github_commit_velocity: float = 0  # commits/week
    github_star_growth: float = 0  # % growth

    # Hiring signals
    open_positions: int = 0
    engineering_roles: int = 0
    growth_roles: int = 0
    hiring_velocity: str = "unknown"  # accelerating, stable, slowing

    # Social signals
    twitter_followers: int = 0
    linkedin_followers: int = 0
    social_sentiment: float = 0.5

    # Traffic
    web_traffic_monthly: int = 0
    traffic_growth: float = 0

    # Derived adjustments
    traction_score_adjustment: float = 0.0  # How much to adjust traction factor


class FinancialSignalsOutput(BaseModel):
    """Output from financial signals node"""
    sector: str

    # Public comps
    public_comps: List[Dict[str, Any]] = []
    median_revenue_multiple: float = 10.0
    median_arr_multiple: float = 12.0

    # M&A benchmarks
    recent_acquisitions: List[Dict[str, Any]] = []
    median_acquisition_multiple: float = 5.0

    # Stage benchmarks
    median_seed_valuation: float = 12000000
    median_series_a_valuation: float = 50000000
    capital_efficiency_benchmark: float = 0.8

    # Derived adjustments
    valuation_adjustment_factor: float = 1.0


class NetworkGraphOutput(BaseModel):
    """Output from network graph node"""
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    # Analysis
    investor_tier_avg: float = 0.5  # Avg tier of investors (1=best)
    network_density: float = 0.0  # How connected
    common_investor_clusters: List[Dict[str, Any]] = []
    influence_scores: Dict[str, float] = {}

    # Derived adjustments
    team_score_adjustment: float = 0.0  # From investor quality
    capital_score_adjustment: float = 0.0


class HistoricalOutcomesOutput(BaseModel):
    """Output from historical calibration node"""
    # Base rates
    base_unicorn_rate: float = 0.016
    base_centaur_rate: float = 0.05
    base_success_rate: float = 0.15
    base_failure_rate: float = 0.30

    # Factor correlations (from backtest)
    factor_correlations: Dict[str, float] = {}

    # Vintage data
    vintage_performance: Dict[str, Dict[str, float]] = {}

    # Calibration parameters
    calibration_intercept: float = 0.0
    calibration_slope: float = 4.0  # For logistic transform

    # Model accuracy
    brier_score: Optional[float] = None
    roc_auc: Optional[float] = None


class PredictionOutput(BaseModel):
    """Output from prediction node"""
    company_name: str
    startup_id: str

    # Core prediction
    unicorn_probability: float
    centaur_probability: float
    success_probability: float
    failure_probability: float

    # Valuation
    expected_valuation: float
    valuation_p10: float
    valuation_p50: float
    valuation_p90: float

    # Factor scores (0-1)
    team_score: float
    market_score: float
    traction_score: float
    timing_score: float
    capital_score: float

    # Factor breakdowns
    factor_details: Dict[str, Dict[str, Any]] = {}

    # Insights
    key_strengths: List[str] = []
    key_risks: List[str] = []
    detailed_reasoning: str = ""

    # Confidence
    prediction_confidence: float
    data_quality: DataConfidence
    source_count: int = 0

    # Timeline
    years_to_unicorn: Optional[float] = None
    years_to_exit: float = 7.0


class MonteCarloOutput(BaseModel):
    """Output from Monte Carlo simulation"""
    simulations_run: int

    # Unicorn probability distribution
    unicorn_prob_mean: float
    unicorn_prob_std: float
    unicorn_prob_p5: float
    unicorn_prob_p25: float
    unicorn_prob_p50: float
    unicorn_prob_p75: float
    unicorn_prob_p95: float

    # Valuation distribution
    valuation_mean: float
    valuation_p10: float
    valuation_p50: float
    valuation_p90: float

    # Scenario paths
    scenario_paths: List[Dict[str, Any]] = []

    # Confidence interval
    confidence_interval_90: tuple = (0.0, 0.0)


class SensitivityOutput(BaseModel):
    """Output from sensitivity analysis"""
    base_probability: float
    sensitivity_matrix: Dict[str, Dict[str, Any]] = {}
    factor_importance: List[Dict[str, Any]] = []
    most_impactful_factor: str = ""
    inflection_points: List[Dict[str, Any]] = []
    recommendation: str = ""


class DecisionBriefOutput(BaseModel):
    """Output from decision brief generator"""
    company_name: str
    recommendation: Recommendation
    confidence: float

    # Executive summary
    summary: str
    rationale: str

    # Key metrics
    key_metrics: List[Dict[str, Any]] = []

    # Analysis
    key_strengths: List[str] = []
    key_risks: List[str] = []

    # Actions
    next_steps: List[str] = []
    questions_for_founders: List[str] = []

    # Comparison to benchmarks
    vs_yc_average: str = ""
    percentile_rank: int = 50


# =============================================================================
# GRAPH STATE - Accumulates all node outputs
# =============================================================================

class GraphState(BaseModel):
    """
    The accumulated state of the graph execution.
    Each node reads from and writes to this state.
    """
    # Metadata
    execution_id: str = ""
    started_at: datetime = Field(default_factory=datetime.now)
    completed_nodes: List[str] = []

    # Input
    batch_input: Optional[BatchInput] = None
    target_companies: List[str] = []

    # Layer 1: Data Collection
    batch: Optional[BatchOutput] = None
    research: Dict[str, ResearchOutput] = {}  # company_name -> research
    market_scanner: Optional[MarketScannerOutput] = None
    alternative_data: Dict[str, AlternativeDataOutput] = {}  # company_name -> alt data
    financial_signals: Optional[FinancialSignalsOutput] = None
    network_graph: Optional[NetworkGraphOutput] = None
    historical_outcomes: Optional[HistoricalOutcomesOutput] = None

    # Layer 2: Analysis
    predictions: Dict[str, PredictionOutput] = {}  # company_name -> prediction
    monte_carlo: Dict[str, MonteCarloOutput] = {}  # company_name -> mc result
    sensitivity: Dict[str, SensitivityOutput] = {}  # company_name -> sensitivity

    # Layer 3: Simulation (per company)
    trajectories: Dict[str, Dict] = {}
    exit_models: Dict[str, Dict] = {}
    funding_scenarios: Dict[str, Dict] = {}

    # Layer 4: Outputs
    decision_briefs: Dict[str, DecisionBriefOutput] = {}
    portfolio_analysis: Optional[Dict] = None
    comparison_matrix: Optional[Dict] = None

    # Aggregates
    batch_summary: Optional[Dict] = None

    def get_company_context(self, company_name: str) -> Dict[str, Any]:
        """Get all accumulated data for a specific company"""
        return {
            "research": self.research.get(company_name),
            "alternative_data": self.alternative_data.get(company_name),
            "prediction": self.predictions.get(company_name),
            "monte_carlo": self.monte_carlo.get(company_name),
            "sensitivity": self.sensitivity.get(company_name),
            "trajectory": self.trajectories.get(company_name),
            "exit_model": self.exit_models.get(company_name),
            "decision_brief": self.decision_briefs.get(company_name),
            # Shared context
            "market": self.market_scanner,
            "financial": self.financial_signals,
            "network": self.network_graph,
            "calibration": self.historical_outcomes,
        }


# =============================================================================
# NODE DEFINITIONS
# =============================================================================

class NodeDefinition(BaseModel):
    """Definition of a node in the graph"""
    name: str
    category: Literal["input", "analysis", "simulation", "output"]
    dependencies: List[str] = []  # Node names that must run first
    input_schema: str  # Name of input schema class
    output_schema: str  # Name of output schema class
    description: str = ""


# Node registry
NODE_DEFINITIONS = {
    # Input layer
    "batch": NodeDefinition(
        name="batch",
        category="input",
        dependencies=[],
        input_schema="BatchInput",
        output_schema="BatchOutput",
        description="Loads companies from a batch (e.g., YC W24)"
    ),
    "research": NodeDefinition(
        name="research",
        category="input",
        dependencies=["batch"],
        input_schema="ResearchInput",
        output_schema="ResearchOutput",
        description="Deep multi-source research on each company"
    ),
    "market_scanner": NodeDefinition(
        name="market_scanner",
        category="input",
        dependencies=["batch"],
        input_schema="MarketScannerInput",
        output_schema="MarketScannerOutput",
        description="Real-time market intelligence for the sector"
    ),
    "alternative_data": NodeDefinition(
        name="alternative_data",
        category="input",
        dependencies=["research"],
        input_schema="AlternativeDataInput",
        output_schema="AlternativeDataOutput",
        description="GitHub, hiring, social signals for each company"
    ),
    "financial_signals": NodeDefinition(
        name="financial_signals",
        category="input",
        dependencies=["batch"],
        input_schema="FinancialSignalsInput",
        output_schema="FinancialSignalsOutput",
        description="Public comps, M&A benchmarks, valuation multiples"
    ),
    "network_graph": NodeDefinition(
        name="network_graph",
        category="input",
        dependencies=["research"],
        input_schema="NetworkGraphInput",
        output_schema="NetworkGraphOutput",
        description="Investor and founder relationship mapping"
    ),
    "historical_outcomes": NodeDefinition(
        name="historical_outcomes",
        category="input",
        dependencies=[],
        input_schema="BatchInput",  # Just needs accelerator
        output_schema="HistoricalOutcomesOutput",
        description="Historical calibration data for probability estimates"
    ),

    # Analysis layer
    "prediction": NodeDefinition(
        name="prediction",
        category="analysis",
        dependencies=["research", "market_scanner", "alternative_data", "financial_signals", "network_graph", "historical_outcomes"],
        input_schema="PredictionInput",
        output_schema="PredictionOutput",
        description="5-factor prediction model with full context"
    ),
    "monte_carlo": NodeDefinition(
        name="monte_carlo",
        category="analysis",
        dependencies=["prediction"],
        input_schema="MonteCarloInput",
        output_schema="MonteCarloOutput",
        description="10,000 simulations for uncertainty quantification"
    ),
    "sensitivity": NodeDefinition(
        name="sensitivity",
        category="analysis",
        dependencies=["prediction"],
        input_schema="SensitivityInput",
        output_schema="SensitivityOutput",
        description="Which factors matter most for this company?"
    ),

    # Simulation layer
    "trajectory_sim": NodeDefinition(
        name="trajectory_sim",
        category="simulation",
        dependencies=["prediction", "monte_carlo"],
        input_schema="Dict",
        output_schema="Dict",
        description="7-year growth trajectory simulation"
    ),
    "exit_modeler": NodeDefinition(
        name="exit_modeler",
        category="simulation",
        dependencies=["prediction", "financial_signals"],
        input_schema="Dict",
        output_schema="Dict",
        description="IPO, M&A, failure probability modeling"
    ),
    "funding_scenarios": NodeDefinition(
        name="funding_scenarios",
        category="simulation",
        dependencies=["prediction", "trajectory_sim"],
        input_schema="Dict",
        output_schema="Dict",
        description="Future rounds and dilution modeling"
    ),

    # Output layer
    "decision_brief": NodeDefinition(
        name="decision_brief",
        category="output",
        dependencies=["prediction", "monte_carlo", "sensitivity", "trajectory_sim", "exit_modeler"],
        input_schema="Dict",
        output_schema="DecisionBriefOutput",
        description="Executive-ready investment decision brief"
    ),
    "comparison_matrix": NodeDefinition(
        name="comparison_matrix",
        category="output",
        dependencies=["prediction"],
        input_schema="Dict",
        output_schema="Dict",
        description="Side-by-side company comparison"
    ),
    "portfolio_optimizer": NodeDefinition(
        name="portfolio_optimizer",
        category="output",
        dependencies=["prediction", "monte_carlo"],
        input_schema="Dict",
        output_schema="Dict",
        description="Optimal allocation across companies"
    ),
}


def get_execution_order() -> List[str]:
    """
    Returns nodes in topological order (respecting dependencies).
    """
    # Simple topological sort
    visited = set()
    order = []

    def visit(node_name: str):
        if node_name in visited:
            return
        visited.add(node_name)
        node_def = NODE_DEFINITIONS.get(node_name)
        if node_def:
            for dep in node_def.dependencies:
                visit(dep)
            order.append(node_name)

    for node_name in NODE_DEFINITIONS:
        visit(node_name)

    return order
