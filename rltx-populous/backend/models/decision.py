"""Decision: The question being asked"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime


class DecisionStatus(str, Enum):
    DRAFT = "draft"
    CONFIGURED = "configured"
    SIMULATING = "simulating"
    COMPLETED = "completed"


class Option(BaseModel):
    """One possible choice"""
    id: str
    name: str
    description: str
    parameters: Dict  # e.g., {"price_increase": 0.10}


class Constraint(BaseModel):
    """A limit that must be respected"""
    id: str
    description: str
    metric: str  # e.g., "retention_rate"
    operator: str  # ">=", "<=", "=="
    value: float  # e.g., 0.90


class SuccessCriteria(BaseModel):
    """What does success look like?"""
    primary_metric: str  # e.g., "revenue"
    optimization: str  # "maximize" or "minimize"
    secondary_metrics: List[str] = []


class Decision(BaseModel):
    """The core decision being analyzed"""
    id: str
    title: str
    description: str
    options: List[Option]
    constraints: List[Constraint]
    success_criteria: SuccessCriteria
    status: DecisionStatus = DecisionStatus.DRAFT
    world_id: Optional[str] = None
    audience_id: Optional[str] = None
    simulation_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
