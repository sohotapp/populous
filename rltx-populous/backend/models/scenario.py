"""
Scenario models - defines the market environment.
This is what the Data Foundation (Layer 1) produces.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum


class MarketType(str, Enum):
    """Supported market types for simulation"""
    B2B_SAAS = "b2b_saas"
    ENTERPRISE = "enterprise"
    CONSUMER = "consumer"
    FINANCIAL = "financial"
    DEFENSE = "defense"


class Stakeholder(BaseModel):
    """A decision-maker archetype within a segment"""
    role: str  # "CFO", "End User", "IT Security", "Champion"
    influence_weight: float = Field(ge=0, le=1)
    priorities: Dict[str, float]  # feature -> importance (0-1)
    risk_tolerance: float = Field(ge=0, le=1)


class DecisionFramework(BaseModel):
    """
    How decisions happen in this segment.
    This is the Operational Ontology (Layer 2).
    """
    stages: List[str] = ["Unaware", "Aware", "Considering", "Evaluating", "Decided"]
    avg_cycle_days: int = 45
    stakeholders: List[Stakeholder]

    # What triggers stage transitions
    triggers: Dict[str, str] = {
        "Unaware->Aware": "Marketing touchpoint or peer mention",
        "Aware->Considering": "Problem recognition + solution awareness",
        "Considering->Evaluating": "Active research, demo request",
        "Evaluating->Decided": "Business case approved, vendor selected"
    }

    # What kills deals
    blockers: List[str] = [
        "Security concerns",
        "Budget freeze",
        "Champion leaves",
        "Competitor undercut"
    ]


class BehavioralProfile(BaseModel):
    """Statistical distribution of behavioral traits in a segment"""

    # Firmographics
    company_size_range: tuple[int, int] = (100, 1000)
    budget_range: tuple[int, int] = (10000, 100000)

    # Behavioral distributions (mean, std)
    risk_tolerance: tuple[float, float] = (0.5, 0.15)
    price_sensitivity: tuple[float, float] = (0.5, 0.15)
    decision_speed: tuple[float, float] = (0.5, 0.15)

    # Social
    influencer_susceptibility: float = 0.5
    network_density: float = 0.05  # % of segment connected


class Segment(BaseModel):
    """A market segment with its decision physics"""
    id: str
    name: str
    size_pct: float = Field(ge=0, le=1)  # % of TAM

    decision_framework: DecisionFramework
    behavioral_profile: BehavioralProfile


class Competitor(BaseModel):
    """A competitor in the market"""
    id: str
    name: str
    market_share: float = Field(ge=0, le=1)

    # Product attributes
    price_point: float = 1.0  # relative to market avg
    features: Dict[str, float]  # feature -> strength (0-1)
    brand_awareness: float = Field(ge=0, le=1)

    # Competitive behavior
    aggression: float = Field(ge=0, le=1, default=0.5)
    response_speed: float = Field(ge=0, le=1, default=0.5)


class Product(BaseModel):
    """Your product"""
    id: str
    name: str
    price_point: float = 1.0
    features: Dict[str, float]
    brand_awareness: float = Field(ge=0, le=1, default=0.1)


class Scenario(BaseModel):
    """
    Complete market scenario.
    This is what would come from the Data Foundation + Ontology layers.
    """
    id: str
    name: str
    description: str
    market_type: MarketType

    # Market structure
    total_addressable_market: int
    segments: List[Segment]

    # Competition
    competitors: List[Competitor]
    your_product: Product

    # Simulation parameters
    simulation_days: int = 90

    class Config:
        json_schema_extra = {
            "example": {
                "id": "saas_launch_2024",
                "name": "B2B SaaS Product Launch",
                "market_type": "b2b_saas",
                "total_addressable_market": 50000
            }
        }
