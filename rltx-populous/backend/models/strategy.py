"""
Strategy models - the intervention being tested.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class Messaging(BaseModel):
    """Positioning and messaging strategy"""
    value_proposition: str
    primary_claim: str
    feature_emphasis: Dict[str, float]  # feature -> emphasis weight
    tone: str = "enterprise"  # "enterprise", "innovative", "value", "technical"

    # Full pitch for LLM reasoning
    full_pitch: Optional[str] = None


class DiscountStrategy(BaseModel):
    """Discounting approach"""
    available: bool = False
    max_discount_pct: float = 0.0
    triggers: List[str] = []  # conditions to offer discount


class Pricing(BaseModel):
    """Pricing strategy"""
    base_price: float = 1.0  # relative to market
    model: str = "per_seat"  # "per_seat", "flat", "usage", "tiered"
    discount: Optional[DiscountStrategy] = None


class CompetitiveResponse(BaseModel):
    """How to respond if competitor acts"""
    trigger_conditions: List[str]
    response_actions: List[str]


class GoToMarket(BaseModel):
    """Go-to-market strategy"""

    # Channel allocation (should sum to ~1.0)
    channels: Dict[str, float] = {
        "paid_digital": 0.3,
        "content": 0.25,
        "events": 0.1,
        "outbound": 0.25,
        "partnerships": 0.1
    }

    intensity: float = Field(ge=0, le=1, default=0.5)
    target_segments: List[str] = []  # segment IDs to prioritize

    competitive_response: Optional[CompetitiveResponse] = None


class Strategy(BaseModel):
    """
    Complete strategy to test.
    This is the intervention injected into the simulation.
    """
    id: str
    name: str
    description: str

    messaging: Messaging
    pricing: Pricing
    gtm: GoToMarket

    launch_day: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "id": "value_play",
                "name": "Value Play",
                "description": "Lead with price and ease-of-use, target SMB"
            }
        }
