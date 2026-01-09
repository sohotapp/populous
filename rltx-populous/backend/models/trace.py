"""Trace: Causal chain analysis"""

from pydantic import BaseModel
from typing import List, Optional, Dict


class TraceNode(BaseModel):
    """A node in the causal chain"""
    id: str
    type: str  # "event", "decision", "outcome", "factor"
    description: str
    timestamp: Optional[float] = None
    metrics: Dict[str, float] = {}
    agent_count: Optional[int] = None


class TraceEdge(BaseModel):
    """A causal link between nodes"""
    source_id: str
    target_id: str
    weight: float  # Causal strength 0-1
    description: str


class Counterfactual(BaseModel):
    """A what-if analysis"""
    id: str
    description: str
    changed_factor: str
    original_value: float
    counterfactual_value: float
    outcome_change: Dict[str, float]  # metric -> delta


class Sensitivity(BaseModel):
    """Sensitivity analysis for a factor"""
    factor: str
    importance: float  # 0-1
    direction: str  # "positive", "negative"
    description: str


class Trace(BaseModel):
    """Complete causal trace for a simulation"""
    id: str
    simulation_id: str
    option_id: str
    nodes: List[TraceNode]
    edges: List[TraceEdge]
    root_causes: List[str]  # IDs of root cause nodes
    key_drivers: List[Sensitivity]
    counterfactuals: List[Counterfactual]
