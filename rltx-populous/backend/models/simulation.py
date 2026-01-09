"""Simulation: Temporal multi-agent simulation"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class SimulationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SimEvent(BaseModel):
    """An event injected into simulation"""
    id: str
    day: int
    type: str  # "competitor_action", "market_shock", "product_update"
    description: str
    parameters: Dict


class DailySnapshot(BaseModel):
    """State of simulation at a point in time"""
    day: int
    metrics: Dict[str, float]  # retention, churn, awareness, etc.
    agent_states: Dict[str, int]  # state -> count
    segment_metrics: Dict[str, Dict[str, float]]  # segment -> metrics
    events_triggered: List[str]


class BranchResult(BaseModel):
    """Result of a single Monte Carlo branch"""
    branch_id: int
    seed: int
    final_metrics: Dict[str, float]
    daily_snapshots: List[DailySnapshot]
    key_events: List[Dict]
    outcome: str  # "success", "failure", "mixed"


class SimulationConfig(BaseModel):
    """Configuration for simulation run"""
    decision_id: str
    world_id: str
    audience_id: str
    option_id: str  # Which option is being tested
    duration_days: int = 90
    num_branches: int = 1000
    events: List[SimEvent] = []


class TemporalSimulation(BaseModel):
    """A complete simulation run"""
    id: str
    config: SimulationConfig
    status: SimulationStatus = SimulationStatus.PENDING
    progress: float = 0.0
    branch_results: List[BranchResult] = []
    aggregate_results: Optional[Dict] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
