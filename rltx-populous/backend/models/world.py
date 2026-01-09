"""World: The market and competitive context"""

from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime


class Segment(BaseModel):
    """A market segment"""
    id: str
    name: str
    description: str
    size_percent: float  # Portion of TAM
    characteristics: Dict  # Behavioral attributes
    decision_cycle_days: int
    price_sensitivity: float  # 0-1
    brand_loyalty: float  # 0-1
    risk_tolerance: float  # 0-1


class Competitor(BaseModel):
    """A market competitor"""
    id: str
    name: str
    market_share: float
    positioning: str
    price_point: float
    strengths: List[str]
    weaknesses: List[str]
    response_speed: str  # "fast", "medium", "slow"
    aggression: float  # 0-1, how likely to respond


class Product(BaseModel):
    """Your product"""
    id: str
    name: str
    current_price: float
    features: Dict[str, float]  # feature -> score 0-1
    positioning: str
    strengths: List[str]
    weaknesses: List[str]


class World(BaseModel):
    """The complete market context"""
    id: str
    name: str
    description: str
    total_addressable_market: int  # Number of potential customers
    market_growth_rate: float
    segments: List[Segment]
    competitors: List[Competitor]
    your_product: Product
    your_market_share: float
    created_at: datetime
