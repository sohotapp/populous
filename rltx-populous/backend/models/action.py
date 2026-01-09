"""Action: Execution plans and recommendations"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date


class ActionItem(BaseModel):
    """A specific action to take"""
    id: str
    action: str
    description: str
    owner: str
    due_date: date
    phase: str
    dependencies: List[str] = []
    approval_required: bool = False
    approval_threshold: Optional[str] = None


class Contingency(BaseModel):
    """An if-then response plan"""
    id: str
    trigger: str  # What condition triggers this
    detection: str  # How we know it's happening
    response: str  # What to do
    escalation: str  # Who to notify
    timeframe: str  # How fast to respond


class ApprovalGate(BaseModel):
    """An approval requirement"""
    id: str
    condition: str
    approver: str
    threshold: Optional[str] = None


class Recommendation(BaseModel):
    """The complete recommendation"""
    decision_id: str
    recommended_option_id: str
    recommended_option_name: str
    confidence: float  # 0-1
    expected_outcome: Dict[str, float]

    # Why this option
    reasoning: str
    comparison_to_alternatives: List[Dict]

    # What to do
    execution_plan: List[ActionItem]
    contingencies: List[Contingency]
    approval_gates: List[ApprovalGate]

    # Risks and monitoring
    key_risks: List[str]
    monitoring_metrics: List[Dict]

    # Board-ready summary
    executive_summary: str
