"""
Company Model
Represents a company profile from deep research
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class CompanySize(str, Enum):
    STARTUP = "1-10"
    SMALL = "11-50"
    MEDIUM = "51-200"
    LARGE = "201-1000"
    ENTERPRISE = "1001-5000"
    MEGA = "5000+"


class FundingStage(str, Enum):
    BOOTSTRAPPED = "bootstrapped"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    SERIES_D_PLUS = "series_d_plus"
    PUBLIC = "public"
    ACQUIRED = "acquired"


class Leader(BaseModel):
    """Key leadership member"""
    name: str
    role: str
    background: Optional[str] = None
    linkedin_url: Optional[str] = None
    notable_decisions: List[str] = []


class ProductTier(BaseModel):
    """A pricing tier for a product"""
    name: str
    price: Optional[float] = None
    price_unit: str = "month"  # month, year, user/month, etc.
    features: List[str] = []
    target_segment: Optional[str] = None


class CompanyProduct(BaseModel):
    """A product offered by the company"""
    id: str = Field(default_factory=lambda: f"prod_{datetime.now().timestamp()}")
    name: str
    description: str
    category: str
    positioning: str
    key_features: List[str] = []
    pricing_tiers: List[ProductTier] = []
    target_market: str = ""
    differentiators: List[str] = []
    weaknesses: List[str] = []


class NewsItem(BaseModel):
    """A news item about the company"""
    title: str
    summary: str
    date: Optional[str] = None
    source: str
    url: Optional[str] = None
    sentiment: str = "neutral"  # positive, negative, neutral
    relevance: float = 0.5  # 0-1 relevance score
    category: str = "general"  # pricing, product, leadership, funding, etc.


class MarketPosition(str, Enum):
    LEADER = "leader"
    CHALLENGER = "challenger"
    NICHE = "niche"
    EMERGING = "emerging"
    DECLINING = "declining"


class CompetitorRelation(BaseModel):
    """Relationship to a competitor"""
    competitor_id: str
    competitor_name: str
    relationship_type: str  # direct, indirect, adjacent
    overlap_areas: List[str] = []
    our_advantages: List[str] = []
    their_advantages: List[str] = []
    threat_level: float = 0.5  # 0-1


class Company(BaseModel):
    """
    Complete company profile from research.
    Used for both the target company and competitors.
    """
    id: str = Field(default_factory=lambda: f"company_{datetime.now().timestamp()}")

    # Basic info
    name: str
    description: str
    tagline: Optional[str] = None
    website: Optional[str] = None
    industry: str
    sub_industry: Optional[str] = None

    # Company details
    founded: Optional[int] = None
    headquarters: Optional[str] = None
    employee_count: Optional[CompanySize] = None
    employee_count_exact: Optional[int] = None

    # Financials
    funding_stage: Optional[FundingStage] = None
    total_funding: Optional[str] = None
    last_funding_date: Optional[str] = None
    last_funding_amount: Optional[str] = None
    revenue_estimate: Optional[str] = None
    is_profitable: Optional[bool] = None

    # Products
    products: List[CompanyProduct] = []
    primary_product: Optional[str] = None

    # Leadership
    leadership: List[Leader] = []
    ceo: Optional[str] = None
    founder: Optional[str] = None

    # Market position
    market_position: MarketPosition = MarketPosition.CHALLENGER
    market_share_estimate: Optional[float] = None
    customer_count_estimate: Optional[str] = None
    notable_customers: List[str] = []

    # SWOT-like analysis
    strengths: List[str] = []
    weaknesses: List[str] = []
    opportunities: List[str] = []
    threats: List[str] = []

    # Competitive landscape
    competitors: List[CompetitorRelation] = []
    direct_competitors: List[str] = []
    indirect_competitors: List[str] = []

    # Recent activity
    recent_news: List[NewsItem] = []
    recent_product_launches: List[str] = []
    recent_pricing_changes: List[str] = []

    # Strategy signals
    growth_strategy: Optional[str] = None
    pricing_strategy: Optional[str] = None
    go_to_market: Optional[str] = None

    # Research metadata
    research_sources: List[str] = []
    research_date: datetime = Field(default_factory=datetime.now)
    confidence_score: float = 0.7  # How confident we are in this research


class Market(BaseModel):
    """
    Market context for a company.
    """
    id: str = Field(default_factory=lambda: f"market_{datetime.now().timestamp()}")

    # Market definition
    name: str
    description: str
    category: str

    # Size and growth
    total_addressable_market: Optional[str] = None
    serviceable_addressable_market: Optional[str] = None
    growth_rate: Optional[float] = None
    growth_drivers: List[str] = []

    # Dynamics
    maturity: str = "growing"  # emerging, growing, mature, declining
    consolidation_trend: str = "fragmenting"  # consolidating, stable, fragmenting
    barriers_to_entry: List[str] = []
    key_success_factors: List[str] = []

    # Segments
    segments: List[Dict] = []
    largest_segment: Optional[str] = None
    fastest_growing_segment: Optional[str] = None

    # Trends
    major_trends: List[str] = []
    disruption_risks: List[str] = []
    regulatory_factors: List[str] = []

    # Competition
    market_leaders: List[str] = []
    emerging_players: List[str] = []
    concentration: str = "fragmented"  # concentrated, moderate, fragmented

    # Research metadata
    research_sources: List[str] = []
    research_date: datetime = Field(default_factory=datetime.now)


class ResearchResult(BaseModel):
    """
    Complete research result for a company query.
    """
    id: str = Field(default_factory=lambda: f"research_{datetime.now().timestamp()}")

    # Query
    query: str
    research_depth: str = "deep"  # quick, standard, deep

    # Results
    target_company: Company
    competitors: List[Company] = []
    market: Market

    # Metadata
    sources_consulted: int = 0
    research_duration_seconds: float = 0
    created_at: datetime = Field(default_factory=datetime.now)

    # Quality metrics
    overall_confidence: float = 0.7
    data_freshness: str = "recent"  # recent, dated, stale
    coverage_completeness: float = 0.8
