"""
Results models - simulation outputs.
This is what the Prediction layer (Layer 5) produces.
"""

from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime


class DailySnapshot(BaseModel):
    """State of simulation at end of a day"""
    day: int

    # Funnel metrics
    unaware_count: int
    aware_count: int
    considering_count: int
    evaluating_count: int
    decided_count: int

    # Conversion
    converted_count: int  # chose your product
    competitor_count: int  # chose competitor
    no_purchase_count: int

    # Awareness
    avg_awareness: float

    # Events
    events: List[str] = []


class BranchResult(BaseModel):
    """Result of a single simulation branch"""
    branch_id: int
    seed: int

    # Outcomes
    conversion_rate: float
    final_awareness: float
    avg_decision_day: float

    # By segment
    segment_conversions: Dict[str, float]

    # Timeline
    timeline: List[DailySnapshot]

    # Key events
    competitor_responded: bool = False
    key_events: List[str] = []


class SegmentAnalysis(BaseModel):
    """Analysis for a specific segment"""
    segment_id: str
    segment_name: str

    conversion_rate: float
    conversion_std: float

    avg_decision_day: float
    top_conversion_drivers: List[str]
    top_blockers: List[str]


class DriverAnalysis(BaseModel):
    """What moved the needle"""
    factor: str
    impact: float  # positive = helped, negative = hurt
    description: str


class SimulationResults(BaseModel):
    """
    Aggregated results across all branches.
    This is what gets presented to the user.
    """
    id: str
    scenario_id: str
    strategy_id: str

    # Run metadata
    num_agents: int
    num_branches: int
    started_at: datetime
    completed_at: datetime

    # Aggregate statistics
    mean_conversion: float
    median_conversion: float
    std_conversion: float

    # Distribution
    p5: float   # 5th percentile
    p25: float  # 25th percentile
    p75: float  # 75th percentile
    p95: float  # 95th percentile

    # Segment breakdown
    segment_analysis: List[SegmentAnalysis]

    # Drivers
    top_drivers: List[DriverAnalysis]
    top_blockers: List[DriverAnalysis]

    # Raw branches (for detailed analysis)
    branches: List[BranchResult]

    # Natural language insight (LLM-generated)
    insight: Optional[str] = None

    # Failure/success analysis
    failure_branches: List[int] = []  # branch_ids in bottom 10%
    success_branches: List[int] = []  # branch_ids in top 10%

    class Config:
        json_schema_extra = {
            "example": {
                "id": "sim_20240101_120000",
                "scenario_id": "saas_launch_2024",
                "strategy_id": "value_play",
                "mean_conversion": 0.082,
                "p5": 0.051,
                "p95": 0.118
            }
        }
