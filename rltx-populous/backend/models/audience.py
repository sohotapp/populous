"""
Audience models for the Populous platform.
"""

from pydantic import BaseModel
from typing import List, Optional, Tuple
from datetime import datetime
from enum import Enum


class AudiencePurpose(str, Enum):
    PRICING_ANALYSIS = "pricing_analysis"
    PRODUCT_LAUNCH = "product_launch"
    CONCEPT_TESTING = "concept_testing"
    POSITIONING = "positioning"
    MARKET_EXPANSION = "market_expansion"
    GENERAL_EXPLORATION = "general_exploration"


class IncomeLevel(str, Enum):
    LOW = "low"
    MIDDLE = "middle"
    UPPER_MIDDLE = "upper_middle"
    HIGH = "high"


class PrecisionLevel(str, Enum):
    GENERAL = "general"
    SPECIFIC = "specific"
    EXACT = "exact"


class AudienceProfile(BaseModel):
    """An individual synthetic persona in an audience"""

    id: str
    name: str
    age: int
    gender: str
    education: str
    occupation: str
    income: str
    location: str
    avatar_url: Optional[str] = None

    # Extended attributes for simulation
    risk_tolerance: float = 0.5
    price_sensitivity: float = 0.5
    decision_speed: float = 0.5


class GenderRatio(BaseModel):
    male: int
    female: int


class Audience(BaseModel):
    """A collection of synthetic personas for research"""

    id: str
    name: str
    description: str

    # Generation parameters
    purpose: AudiencePurpose
    age_range: Tuple[int, int]
    gender_ratio: GenderRatio
    income_level: IncomeLevel
    decision_factors: List[str] = []
    precision: PrecisionLevel = PrecisionLevel.GENERAL

    # Generated profiles
    profile_count: int = 0
    profiles: List[AudienceProfile] = []

    # Timestamps
    created_at: datetime = datetime.now()


class CreateAudienceRequest(BaseModel):
    """Request to create and generate an audience"""
    name: str
    description: str = ""
    purpose: AudiencePurpose
    age_min: int = 18
    age_max: int = 65
    gender_ratio_male: int = 50
    gender_ratio_female: int = 50
    income_level: IncomeLevel = IncomeLevel.MIDDLE
    decision_factors: List[str] = []
    precision: PrecisionLevel = PrecisionLevel.GENERAL
    profile_count: int = 100
