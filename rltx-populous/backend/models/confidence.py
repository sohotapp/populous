"""
Confidence Decomposition Models
Breaking down uncertainty into component sources
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import uuid


class UncertaintySource(str, Enum):
    """Categories of uncertainty sources"""
    DATA_QUALITY = "data_quality"           # Incomplete or stale data
    MODEL_ACCURACY = "model_accuracy"       # Model limitations
    MARKET_VOLATILITY = "market_volatility" # External market factors
    COMPETITOR_BEHAVIOR = "competitor_behavior"  # Unpredictable competitors
    CUSTOMER_RESPONSE = "customer_response"  # Customer behavior variance
    EXECUTION_RISK = "execution_risk"       # Implementation uncertainty
    TEMPORAL_DECAY = "temporal_decay"       # Further predictions less certain
    ASSUMPTION_SENSITIVITY = "assumption_sensitivity"  # Key assumptions


class ConfidenceLevel(str, Enum):
    """Confidence levels for interpretability"""
    VERY_HIGH = "very_high"    # 90-100%
    HIGH = "high"              # 75-89%
    MODERATE = "moderate"      # 50-74%
    LOW = "low"                # 25-49%
    VERY_LOW = "very_low"      # 0-24%


class UncertaintyComponent(BaseModel):
    """A single component of uncertainty"""
    id: str = Field(default_factory=lambda: f"unc_{uuid.uuid4().hex[:8]}")

    source: UncertaintySource
    name: str                          # Human-readable name
    description: str = ""              # What causes this uncertainty

    # Contribution to total uncertainty
    contribution: float = 0.0          # 0-1, how much this contributes
    variance_explained: float = 0.0    # Statistical variance explained

    # Can this be reduced?
    reducible: bool = True
    reduction_actions: List[str] = []  # Actions to reduce uncertainty
    reduction_potential: float = 0.0   # How much could be reduced (0-1)

    # Evidence
    evidence_strength: str = "moderate"  # weak, moderate, strong
    data_sources: List[str] = []

    # Sensitivity
    impact_if_wrong: str = "moderate"  # low, moderate, high, critical


class ConfidenceDecomposition(BaseModel):
    """Complete decomposition of confidence for a prediction"""
    id: str = Field(default_factory=lambda: f"conf_{uuid.uuid4().hex[:8]}")
    prediction_id: str = ""            # What prediction this is for
    created_at: datetime = Field(default_factory=datetime.now)

    # Overall confidence
    overall_confidence: float = 0.0    # 0-1
    confidence_level: ConfidenceLevel = ConfidenceLevel.MODERATE
    confidence_interval: tuple = (0.0, 1.0)  # Lower and upper bounds

    # Decomposition
    components: List[UncertaintyComponent] = []

    # Key insights
    primary_uncertainty: str = ""      # Biggest source
    most_reducible: str = ""          # Easiest to improve
    critical_assumptions: List[str] = []

    # Recommendations
    confidence_improvement_actions: List[str] = []
    accept_uncertainty_reasons: List[str] = []

    # For visualization
    breakdown_chart_data: Dict[str, Any] = {}


class SensitivityAnalysis(BaseModel):
    """Analysis of how sensitive predictions are to assumptions"""
    id: str = Field(default_factory=lambda: f"sens_{uuid.uuid4().hex[:8]}")
    prediction_id: str = ""

    # Key variables tested
    variables_tested: List[str] = []

    # Results
    sensitivities: Dict[str, Dict[str, Any]] = {}  # variable -> {impact, range}

    # Rankings
    most_sensitive_to: List[str] = []  # Ranked by impact
    least_sensitive_to: List[str] = []

    # Recommendations
    variables_to_monitor: List[str] = []
    robustness_score: float = 0.0      # 0-1, how robust to changes


class DataQualityAssessment(BaseModel):
    """Assessment of data quality for confidence calculation"""
    source: str
    freshness_days: int = 0            # How old is the data
    completeness: float = 1.0          # 0-1
    accuracy_estimate: float = 1.0     # 0-1
    reliability_score: float = 1.0     # 0-1

    issues: List[str] = []
    recommendations: List[str] = []


class ConfidenceReport(BaseModel):
    """Human-readable confidence report"""
    prediction_summary: str

    # Headline
    headline: str                      # e.g., "Moderate confidence (68%)"
    plain_english: str                 # Simple explanation

    # Breakdown
    confidence_value: float
    confidence_level: ConfidenceLevel

    # What's driving uncertainty
    main_uncertainties: List[Dict[str, Any]] = []

    # What you can do
    to_increase_confidence: List[str] = []
    to_reduce_risk: List[str] = []

    # Caveats
    key_assumptions: List[str] = []
    what_could_change: List[str] = []
