"""
Scenario Branch Models
Branching futures and probability trees for decision exploration
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import uuid


class ScenarioOutcome(str, Enum):
    """Possible high-level outcomes"""
    FAVORABLE = "favorable"           # You win
    NEUTRAL = "neutral"               # Status quo maintained
    UNFAVORABLE = "unfavorable"       # Competitor wins
    MARKET_SHIFT = "market_shift"     # External disruption
    ESCALATION = "escalation"         # Competitive escalation


class BranchType(str, Enum):
    """Types of scenario branches"""
    YOUR_MOVE = "your_move"           # Decision point
    COMPETITOR_RESPONSE = "competitor_response"
    MARKET_EVENT = "market_event"
    CUSTOMER_REACTION = "customer_reaction"
    CHAIN_EFFECT = "chain_effect"


class ScenarioMetrics(BaseModel):
    """Metrics for a scenario state"""
    market_share: float = 0.0
    revenue_impact: float = 0.0       # Percentage change
    customer_retention: float = 0.0   # Retention rate
    competitive_position: float = 0.0  # -1 to 1
    risk_exposure: float = 0.0        # 0 to 1
    time_to_realize: int = 0          # Days


class ScenarioNode(BaseModel):
    """A node in the scenario tree"""
    id: str = Field(default_factory=lambda: f"node_{uuid.uuid4().hex[:8]}")

    # Position in tree
    parent_id: Optional[str] = None
    children_ids: List[str] = []
    depth: int = 0

    # Node content
    branch_type: BranchType
    actor: str = ""                   # Who takes action (you, competitor name, market)
    action: str = ""                  # What happens
    description: str = ""             # Human-readable description

    # Probabilities
    probability: float = 1.0          # P(this node | parent)
    cumulative_probability: float = 1.0  # P(reaching this node from root)

    # State at this node
    metrics: ScenarioMetrics = Field(default_factory=ScenarioMetrics)
    outcome: Optional[ScenarioOutcome] = None

    # Time
    time_offset_days: int = 0         # Days from decision

    # Analysis
    key_drivers: List[str] = []       # What caused this branch
    risks: List[str] = []
    opportunities: List[str] = []

    # For visualization
    x: float = 0.0
    y: float = 0.0
    expanded: bool = True


class ScenarioPath(BaseModel):
    """A complete path through the scenario tree"""
    id: str = Field(default_factory=lambda: f"path_{uuid.uuid4().hex[:8]}")
    node_ids: List[str] = []

    # Path characteristics
    total_probability: float = 0.0
    final_outcome: ScenarioOutcome = ScenarioOutcome.NEUTRAL
    final_metrics: ScenarioMetrics = Field(default_factory=ScenarioMetrics)

    # Summary
    narrative: str = ""               # Story of what happens
    key_events: List[str] = []
    critical_moments: List[str] = []  # Decision points that matter most

    # Recommendations for this path
    mitigations: List[str] = []       # If unfavorable
    accelerators: List[str] = []      # If favorable


class ScenarioCluster(BaseModel):
    """A cluster of similar outcomes"""
    id: str = Field(default_factory=lambda: f"cluster_{uuid.uuid4().hex[:8]}")
    name: str = ""
    description: str = ""

    outcome: ScenarioOutcome
    path_ids: List[str] = []

    # Aggregate stats
    total_probability: float = 0.0
    avg_metrics: ScenarioMetrics = Field(default_factory=ScenarioMetrics)

    # Representative narrative
    typical_narrative: str = ""

    # Distinguishing factors
    defining_characteristics: List[str] = []


class ScenarioTree(BaseModel):
    """Complete scenario tree for a decision"""
    id: str = Field(default_factory=lambda: f"tree_{uuid.uuid4().hex[:8]}")
    decision_id: str
    created_at: datetime = Field(default_factory=datetime.now)

    # Tree structure
    root_id: str = ""
    nodes: Dict[str, ScenarioNode] = {}

    # Computed paths and clusters
    paths: List[ScenarioPath] = []
    clusters: List[ScenarioCluster] = []

    # High-level analysis
    outcome_probabilities: Dict[str, float] = {}  # outcome -> probability
    expected_metrics: ScenarioMetrics = Field(default_factory=ScenarioMetrics)

    # Key insights
    dominant_scenarios: List[str] = []  # Most likely path IDs
    critical_uncertainties: List[str] = []
    recommended_hedges: List[str] = []

    # Metadata
    max_depth: int = 0
    total_nodes: int = 0
    total_paths: int = 0
    simulation_runs: int = 0

    def get_node(self, node_id: str) -> Optional[ScenarioNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_children(self, node_id: str) -> List[ScenarioNode]:
        """Get all children of a node."""
        node = self.nodes.get(node_id)
        if not node:
            return []
        return [self.nodes[cid] for cid in node.children_ids if cid in self.nodes]

    def get_path_to_node(self, node_id: str) -> List[ScenarioNode]:
        """Get the path from root to a node."""
        path = []
        current_id = node_id
        while current_id:
            node = self.nodes.get(current_id)
            if node:
                path.insert(0, node)
                current_id = node.parent_id
            else:
                break
        return path


class ScenarioBranchInput(BaseModel):
    """Input for generating scenario branches"""
    decision_id: str
    your_move: Dict[str, Any]

    # Context
    company_name: str
    competitor_names: List[str] = []
    market_context: str = ""

    # Parameters
    max_depth: int = 4
    branch_factor: int = 3           # Max children per node
    time_horizon_days: int = 90
    include_market_events: bool = True

    # Monte Carlo
    num_simulations: int = 100


class ScenarioSummary(BaseModel):
    """Human-readable scenario summary"""
    tree_id: str
    decision_title: str

    # Headline stats
    headline: str                     # e.g., "73% chance of favorable outcome"

    # Outcome breakdown
    outcomes: List[Dict[str, Any]] = []  # [{outcome, probability, description}]

    # Key scenarios
    best_case: Dict[str, Any] = {}
    worst_case: Dict[str, Any] = {}
    most_likely: Dict[str, Any] = {}

    # Actionable insights
    key_risks: List[str] = []
    key_opportunities: List[str] = []
    recommended_actions: List[str] = []

    # For UI
    tree_visualization_data: Dict[str, Any] = {}
