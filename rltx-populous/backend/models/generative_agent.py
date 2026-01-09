"""Agent: Stanford-architecture cognitive agent"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum


class Memory(BaseModel):
    """A single memory in the stream"""
    id: str
    timestamp: float  # Simulation time
    description: str
    importance: float  # 1-10
    type: str  # "observation", "action", "reflection"
    embedding: Optional[List[float]] = None


class Reflection(BaseModel):
    """A synthesized insight"""
    id: str
    timestamp: float
    content: str
    source_memory_ids: List[str]
    importance: float


class AgentBelief(BaseModel):
    """A probabilistic belief"""
    subject: str  # What the belief is about
    probability: float  # 0-1
    confidence: float  # How sure about the probability
    last_updated: float


class Relationship(BaseModel):
    """A social connection"""
    other_agent_id: str
    relationship_type: str  # "colleague", "friend", "family", "acquaintance"
    trust_level: float  # 0-1
    influence_weight: float  # How much they influence decisions


class AgentDecisionEvent(BaseModel):
    """A decision the agent made"""
    timestamp: float
    decision_type: str
    choice: str
    reasoning: str
    confidence: float
    factors: Dict[str, float]  # What influenced the decision


class AgentState(str, Enum):
    """Current state in decision journey"""
    UNAWARE = "unaware"
    AWARE = "aware"
    CONSIDERING = "considering"
    EVALUATING = "evaluating"
    DECIDED = "decided"
    CHURNED = "churned"
    RETAINED = "retained"


class GenerativeAgent(BaseModel):
    """A full cognitive agent with Stanford architecture"""
    id: str

    # Identity
    name: str
    age: int
    occupation: str
    income: float
    location: str
    education: str
    segment_id: str

    # Personality & Preferences
    personality: Dict[str, float]  # Big Five traits
    values: List[str]
    pain_points: List[str]
    goals: List[str]

    # Behavioral Parameters
    price_sensitivity: float  # 0-1
    brand_loyalty: float  # 0-1
    risk_tolerance: float  # 0-1
    social_influence: float  # 0-1, how much others affect them
    decision_style: str  # "analytical", "intuitive", "social", "habitual"

    # Utility Function Weights
    utility_weights: Dict[str, float]  # price, quality, convenience, status

    # Stanford Architecture
    memory_stream: List[Memory] = []
    reflections: List[Reflection] = []
    beliefs: Dict[str, AgentBelief] = {}
    current_plan: List[str] = []

    # Social Network
    relationships: List[Relationship] = []

    # State
    state: AgentState = AgentState.UNAWARE
    awareness: float = 0.0
    consideration_set: List[str] = []  # Product IDs being considered
    decision_events: List[AgentDecisionEvent] = []

    # Thresholds (for reflection triggering)
    reflection_threshold: float = 100.0
    accumulated_importance: float = 0.0

    class Config:
        use_enum_values = True
