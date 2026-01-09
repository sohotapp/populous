# RLTX POPULOUS: Surgical Build Plan
## Complete End-to-End Production Architecture

---

# OVERVIEW

## What We're Building
A complete Decision Intelligence platform with:
- 8 core screens (full user journey)
- Stanford generative agents (memory + reflection + planning)
- Temporal multi-agent simulation with network effects
- Causal trace analysis
- Interactive agent interviews
- Actionable execution plans

## Architecture Summary
```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Next.js)                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │Decision │ │ World   │ │Audience │ │Simulation│ │ Insight │           │
│  │ Canvas  │ │ Builder │ │ Studio  │ │ Center  │ │Explorer │           │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘           │
│       │           │           │           │           │                 │
│  ┌────┴────┐ ┌────┴────┐ ┌────┴────┐                                   │
│  │  Trace  │ │  Agent  │ │ Action  │                                   │
│  │ Viewer  │ │Interview│ │ Planner │                                   │
│  └────┬────┘ └────┬────┘ └────┬────┘                                   │
│       └───────────┴───────────┴─────────────┐                          │
│                                             ▼                          │
│                              ┌──────────────────────┐                  │
│                              │    API Client        │                  │
│                              │  (React Query)       │                  │
│                              └──────────┬───────────┘                  │
└─────────────────────────────────────────┼───────────────────────────────┘
                                          │ REST + WebSocket
                                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (FastAPI)                             │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         API Layer                                │   │
│  │  /decisions  /worlds  /audiences  /simulations  /predictions    │   │
│  │  /traces     /agents/{id}/chat   /actions                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│  ┌─────────────────────────────────┴───────────────────────────────┐   │
│  │                       Engine Layer                               │   │
│  │                                                                  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                 │   │
│  │  │  Agent     │  │ Simulation │  │  Decision  │                 │   │
│  │  │  Engine    │  │  Engine    │  │  Engine    │                 │   │
│  │  │            │  │            │  │            │                 │   │
│  │  │ • Memory   │  │ • Temporal │  │ • Traces   │                 │   │
│  │  │ • Reflect  │  │ • Monte C. │  │ • Actions  │                 │   │
│  │  │ • Plan     │  │ • Network  │  │ • Explain  │                 │   │
│  │  │ • Decide   │  │ • Events   │  │            │                 │   │
│  │  └────────────┘  └────────────┘  └────────────┘                 │   │
│  │                                                                  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                 │   │
│  │  │ Prediction │  │   Chat     │  │   Bias     │                 │   │
│  │  │  Engine    │  │  Engine    │  │  Engine    │                 │   │
│  │  └────────────┘  └────────────┘  └────────────┘                 │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│  ┌─────────────────────────────────┴───────────────────────────────┐   │
│  │                       Data Layer                                 │   │
│  │  Models: Decision, World, Agent, Memory, Simulation, Trace      │   │
│  │  Storage: SQLite (demo) → PostgreSQL (production)               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
└────────────────────────────────────┼────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                               │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │  Anthropic      │  │  (Future)       │  │  (Future)       │         │
│  │  Claude API     │  │  Neo4j          │  │  Redis          │         │
│  │                 │  │  Knowledge Graph│  │  Caching        │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# PART 1: DATA MODELS (Foundation)

Every component depends on these. Build first.

## 1.1 Core Models

### File: `backend/models/decision.py`
```python
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
```

### File: `backend/models/world.py`
```python
"""World: The market and competitive context"""

from pydantic import BaseModel
from typing import List, Optional, Dict

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
```

### File: `backend/models/agent.py`
```python
"""Agent: Stanford-architecture cognitive agent"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
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

class Belief(BaseModel):
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

class DecisionEvent(BaseModel):
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

class Agent(BaseModel):
    """A full cognitive agent"""
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
    beliefs: Dict[str, Belief] = {}
    current_plan: List[str] = []

    # Social Network
    relationships: List[Relationship] = []

    # State
    state: AgentState = AgentState.UNAWARE
    awareness: float = 0.0
    consideration_set: List[str] = []  # Product IDs being considered
    decision_events: List[DecisionEvent] = []

    # Thresholds (for reflection triggering)
    reflection_threshold: float = 100.0
    accumulated_importance: float = 0.0
```

### File: `backend/models/simulation.py`
```python
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

class Event(BaseModel):
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
    events: List[Event] = []

class Simulation(BaseModel):
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
```

### File: `backend/models/trace.py`
```python
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
```

### File: `backend/models/action.py`
```python
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
```

---

# PART 2: BACKEND ENGINES

## 2.1 Agent Engine (Stanford Architecture)

### File: `backend/engine/agent_engine.py`
```python
"""
Stanford Generative Agent Implementation
Memory Stream + Reflection + Planning
"""

from anthropic import Anthropic
from typing import List, Dict, Optional
import json
from datetime import datetime

from backend.models.agent import Agent, Memory, Reflection, Belief, DecisionEvent

class AgentEngine:
    """Engine for managing Stanford-architecture agents"""

    def __init__(self, llm_client: Anthropic):
        self.llm = llm_client

    # ==================== MEMORY ====================

    def perceive(self, agent: Agent, observation: str, sim_time: float) -> Agent:
        """Add an observation to the agent's memory stream"""
        # Rate importance
        importance = self._rate_importance(agent, observation)

        # Create memory
        memory = Memory(
            id=f"mem_{len(agent.memory_stream)}",
            timestamp=sim_time,
            description=observation,
            importance=importance,
            type="observation"
        )

        # Add to stream
        agent.memory_stream.append(memory)
        agent.accumulated_importance += importance

        # Check if reflection needed
        if agent.accumulated_importance >= agent.reflection_threshold:
            agent = self._reflect(agent, sim_time)
            agent.accumulated_importance = 0

        return agent

    def _rate_importance(self, agent: Agent, observation: str) -> float:
        """LLM rates importance 1-10"""
        prompt = f"""Rate the importance of this observation for {agent.name},
a {agent.occupation} who is {agent.decision_style} in their decision-making.

Their values: {', '.join(agent.values)}
Their pain points: {', '.join(agent.pain_points)}

Observation: {observation}

Rate 1-10 where:
1 = Completely mundane, routine
5 = Moderately important, worth noting
10 = Critical, requires immediate attention

Return only the number."""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            return float(response.content[0].text.strip())
        except:
            return 5.0  # Default to moderate importance

    # ==================== REFLECTION ====================

    def _reflect(self, agent: Agent, sim_time: float) -> Agent:
        """Generate higher-level insights from recent memories"""
        recent_memories = agent.memory_stream[-50:]

        prompt = f"""You are {agent.name}, a {agent.age}-year-old {agent.occupation}.

Your personality: {json.dumps(agent.personality)}
Your values: {', '.join(agent.values)}

Recent experiences:
{chr(10).join([f"- {m.description} (importance: {m.importance})" for m in recent_memories])}

Based on these experiences, what are the 3 most important high-level insights
or realizations you would have? These should be synthesized conclusions, not
just repetitions of what happened.

Format: One insight per line, starting with "I realize..." or "I've noticed..." """

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        insights = response.content[0].text.strip().split('\n')

        for insight in insights:
            if insight.strip():
                reflection = Reflection(
                    id=f"ref_{len(agent.reflections)}",
                    timestamp=sim_time,
                    content=insight.strip(),
                    source_memory_ids=[m.id for m in recent_memories[-20:]],
                    importance=8.0  # Reflections are inherently important
                )
                agent.reflections.append(reflection)

                # Reflections become memories too (recursive)
                reflection_memory = Memory(
                    id=f"mem_{len(agent.memory_stream)}",
                    timestamp=sim_time,
                    description=f"[Reflection] {insight.strip()}",
                    importance=8.0,
                    type="reflection"
                )
                agent.memory_stream.append(reflection_memory)

        return agent

    # ==================== MEMORY RETRIEVAL ====================

    def retrieve_relevant_memories(
        self,
        agent: Agent,
        query: str,
        sim_time: float,
        k: int = 20
    ) -> List[Memory]:
        """Retrieve memories by recency + importance + relevance"""
        scored_memories = []

        for mem in agent.memory_stream:
            # Recency score (exponential decay)
            time_diff = sim_time - mem.timestamp
            recency_score = 0.99 ** time_diff

            # Importance score (normalized)
            importance_score = mem.importance / 10.0

            # Relevance score (simple keyword matching for now)
            # In production: use embeddings
            query_words = set(query.lower().split())
            mem_words = set(mem.description.lower().split())
            overlap = len(query_words & mem_words)
            relevance_score = min(overlap / max(len(query_words), 1), 1.0)

            # Combined score
            total_score = (
                0.3 * recency_score +
                0.3 * importance_score +
                0.4 * relevance_score
            )

            scored_memories.append((total_score, mem))

        # Sort and return top k
        scored_memories.sort(reverse=True, key=lambda x: x[0])
        return [mem for _, mem in scored_memories[:k]]

    # ==================== PLANNING ====================

    def plan(self, agent: Agent, goal: str, sim_time: float) -> List[str]:
        """Generate action plan for a goal"""
        relevant_memories = self.retrieve_relevant_memories(agent, goal, sim_time)
        recent_reflections = agent.reflections[-10:]

        prompt = f"""You are {agent.name}, a {agent.age}-year-old {agent.occupation}.

Your goal: {goal}

What you optimize for (utility function weights):
{json.dumps(agent.utility_weights)}

Your constraints and considerations:
- Price sensitivity: {agent.price_sensitivity} (0=insensitive, 1=very sensitive)
- Brand loyalty: {agent.brand_loyalty} (0=none, 1=very loyal)
- Risk tolerance: {agent.risk_tolerance} (0=risk-averse, 1=risk-seeking)

Relevant memories:
{chr(10).join([f"- {m.description}" for m in relevant_memories])}

Recent reflections:
{chr(10).join([f"- {r.content}" for r in recent_reflections])}

Generate a step-by-step action plan. Be specific and realistic for someone
with your profile. Format as numbered steps."""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        plan = response.content[0].text.strip().split('\n')
        agent.current_plan = [step.strip() for step in plan if step.strip()]

        return agent.current_plan

    # ==================== DECISION ====================

    def decide(
        self,
        agent: Agent,
        options: List[Dict],
        context: str,
        sim_time: float
    ) -> DecisionEvent:
        """Make a decision given options"""
        relevant_memories = self.retrieve_relevant_memories(agent, context, sim_time)

        prompt = f"""You are {agent.name}, a {agent.age}-year-old {agent.occupation}.

You need to make a decision.

Context: {context}

Options:
{json.dumps(options, indent=2)}

Your utility function (what you optimize for):
{json.dumps(agent.utility_weights)}

Your current beliefs:
{json.dumps({k: {"probability": v.probability, "confidence": v.confidence}
             for k, v in agent.beliefs.items()})}

Your decision style: {agent.decision_style}

Relevant past experiences:
{chr(10).join([f"- {m.description}" for m in relevant_memories])}

Make your decision. Explain your reasoning, then state your choice.

Format:
REASONING: [Your thought process]
CHOICE: [Option ID]
CONFIDENCE: [0.0 to 1.0]
KEY_FACTORS: [factor1: weight, factor2: weight, ...]"""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        result = self._parse_decision_response(response.content[0].text, options)

        decision_event = DecisionEvent(
            timestamp=sim_time,
            decision_type=context,
            choice=result["choice"],
            reasoning=result["reasoning"],
            confidence=result["confidence"],
            factors=result["factors"]
        )

        agent.decision_events.append(decision_event)

        return decision_event

    def _parse_decision_response(self, text: str, options: List[Dict]) -> Dict:
        """Parse LLM decision response"""
        # Simple parsing - could be more robust
        lines = text.strip().split('\n')
        result = {
            "reasoning": "",
            "choice": options[0]["id"] if options else "",
            "confidence": 0.5,
            "factors": {}
        }

        for line in lines:
            if line.startswith("REASONING:"):
                result["reasoning"] = line.replace("REASONING:", "").strip()
            elif line.startswith("CHOICE:"):
                result["choice"] = line.replace("CHOICE:", "").strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    result["confidence"] = float(line.replace("CONFIDENCE:", "").strip())
                except:
                    pass
            elif line.startswith("KEY_FACTORS:"):
                # Parse factors
                factors_str = line.replace("KEY_FACTORS:", "").strip()
                # Simple parsing
                for factor in factors_str.split(","):
                    if ":" in factor:
                        k, v = factor.split(":")
                        try:
                            result["factors"][k.strip()] = float(v.strip())
                        except:
                            pass

        return result

    # ==================== BELIEF UPDATE ====================

    def update_beliefs(self, agent: Agent, evidence: Dict, sim_time: float) -> Agent:
        """Bayesian update on beliefs given evidence"""
        for subject, new_info in evidence.items():
            if subject in agent.beliefs:
                belief = agent.beliefs[subject]
                # Simple Bayesian-ish update
                prior = belief.probability
                likelihood = new_info.get("likelihood", 0.5)

                # Update probability
                posterior = (prior * likelihood) / (
                    prior * likelihood + (1 - prior) * (1 - likelihood)
                )

                belief.probability = posterior
                belief.confidence = min(belief.confidence + 0.1, 1.0)
                belief.last_updated = sim_time
            else:
                # New belief
                agent.beliefs[subject] = Belief(
                    subject=subject,
                    probability=new_info.get("probability", 0.5),
                    confidence=new_info.get("confidence", 0.3),
                    last_updated=sim_time
                )

        return agent
```

## 2.2 Simulation Engine

### File: `backend/engine/simulation_engine.py`
```python
"""
Temporal Multi-Agent Simulation Engine
Monte Carlo + Network Effects + Event Injection
"""

import numpy as np
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Optional
import copy
from datetime import datetime

from backend.models.simulation import (
    Simulation, SimulationConfig, BranchResult,
    DailySnapshot, Event, SimulationStatus
)
from backend.models.agent import Agent, AgentState
from backend.models.world import World
from backend.engine.agent_engine import AgentEngine
from backend.engine.network_engine import NetworkEngine

class SimulationEngine:
    """Engine for running temporal multi-agent simulations"""

    def __init__(self, agent_engine: AgentEngine, network_engine: NetworkEngine):
        self.agent_engine = agent_engine
        self.network_engine = network_engine

    def run_simulation(
        self,
        config: SimulationConfig,
        agents: List[Agent],
        world: World,
        option: Dict,
        progress_callback=None
    ) -> Simulation:
        """Run complete Monte Carlo simulation"""

        simulation = Simulation(
            id=f"sim_{datetime.now().timestamp()}",
            config=config,
            status=SimulationStatus.RUNNING,
            started_at=datetime.now()
        )

        # Run branches in parallel
        branch_results = []

        with ProcessPoolExecutor(max_workers=8) as executor:
            futures = []
            for branch_id in range(config.num_branches):
                future = executor.submit(
                    self._run_branch,
                    branch_id=branch_id,
                    agents=copy.deepcopy(agents),
                    world=world,
                    option=option,
                    config=config
                )
                futures.append(future)

            # Collect results
            for i, future in enumerate(futures):
                result = future.result()
                branch_results.append(result)

                if progress_callback:
                    progress_callback((i + 1) / config.num_branches)

        simulation.branch_results = branch_results
        simulation.aggregate_results = self._aggregate_results(branch_results)
        simulation.status = SimulationStatus.COMPLETED
        simulation.completed_at = datetime.now()
        simulation.progress = 1.0

        return simulation

    def _run_branch(
        self,
        branch_id: int,
        agents: List[Agent],
        world: World,
        option: Dict,
        config: SimulationConfig
    ) -> BranchResult:
        """Run a single simulation branch"""

        # Set random seed for reproducibility
        np.random.seed(branch_id)

        daily_snapshots = []
        key_events = []

        # Apply the option/intervention at day 0
        self._apply_intervention(agents, option, world, day=0)
        key_events.append({
            "day": 0,
            "event": f"Intervention applied: {option.get('name', 'Unknown')}"
        })

        # Run simulation day by day
        for day in range(config.duration_days):
            # Check for scheduled events
            for event in config.events:
                if event.day == day:
                    self._inject_event(agents, event, world)
                    key_events.append({
                        "day": day,
                        "event": event.description
                    })

            # Process each agent
            for agent in agents:
                self._process_agent_day(agent, world, option, day)

            # Process network effects (social influence)
            self.network_engine.propagate_influence(agents, day)

            # Take snapshot
            snapshot = self._take_snapshot(agents, day)
            daily_snapshots.append(snapshot)

            # Check for competitive response
            if self._should_competitor_respond(world, agents, day):
                self._trigger_competitor_response(agents, world, day)
                key_events.append({
                    "day": day,
                    "event": "Competitor response triggered"
                })

        # Calculate final metrics
        final_metrics = self._calculate_final_metrics(agents, world)

        return BranchResult(
            branch_id=branch_id,
            seed=branch_id,
            final_metrics=final_metrics,
            daily_snapshots=daily_snapshots,
            key_events=key_events,
            outcome=self._classify_outcome(final_metrics, config)
        )

    def _process_agent_day(
        self,
        agent: Agent,
        world: World,
        option: Dict,
        day: int
    ):
        """Process one day for one agent"""

        # Generate daily observations based on state
        observations = self._generate_daily_observations(agent, world, option, day)

        for obs in observations:
            self.agent_engine.perceive(agent, obs, sim_time=day)

        # State transitions based on accumulated experience
        self._update_agent_state(agent, world, option, day)

    def _generate_daily_observations(
        self,
        agent: Agent,
        world: World,
        option: Dict,
        day: int
    ) -> List[str]:
        """Generate observations an agent would have on a given day"""
        observations = []

        # Awareness phase observations
        if agent.state == AgentState.UNAWARE:
            # Random chance of becoming aware
            if np.random.random() < 0.1:  # Base awareness rate
                observations.append(
                    f"Heard about {world.your_product.name} changing their pricing"
                )

        # Active consideration observations
        elif agent.state in [AgentState.AWARE, AgentState.CONSIDERING]:
            # Research activities
            if np.random.random() < 0.3:
                observations.append(
                    f"Looked up {world.your_product.name} reviews online"
                )
            if np.random.random() < 0.2:
                competitor = np.random.choice(world.competitors)
                observations.append(
                    f"Compared pricing with {competitor.name}"
                )

        # Social observations (from network)
        if agent.relationships and np.random.random() < 0.15:
            observations.append(
                "Colleague mentioned their experience with the product"
            )

        return observations

    def _update_agent_state(
        self,
        agent: Agent,
        world: World,
        option: Dict,
        day: int
    ):
        """Update agent state based on accumulated experience"""

        # Calculate current sentiment from recent memories
        recent_memories = agent.memory_stream[-20:]
        sentiment = self._calculate_sentiment(recent_memories)

        # Calculate product score
        product_score = self._calculate_product_score(agent, world, option)

        # State machine transitions
        if agent.state == AgentState.UNAWARE:
            if agent.awareness > 0.25:
                agent.state = AgentState.AWARE

        elif agent.state == AgentState.AWARE:
            if agent.awareness > 0.50:
                agent.state = AgentState.CONSIDERING

        elif agent.state == AgentState.CONSIDERING:
            if agent.awareness > 0.70:
                agent.state = AgentState.EVALUATING

        elif agent.state == AgentState.EVALUATING:
            # Make purchase/churn decision
            decision_threshold = 0.55
            if product_score > decision_threshold:
                agent.state = AgentState.RETAINED
            elif product_score < (1 - decision_threshold):
                agent.state = AgentState.CHURNED
            # else: stay evaluating

        # Update awareness (increases over time with observations)
        awareness_gain = len([m for m in recent_memories if "product" in m.description.lower()]) * 0.05
        agent.awareness = min(agent.awareness + awareness_gain, 1.0)

    def _calculate_product_score(
        self,
        agent: Agent,
        world: World,
        option: Dict
    ) -> float:
        """Calculate how favorably agent views the product"""

        # Feature fit (40%)
        feature_score = sum(
            world.your_product.features.values()
        ) / max(len(world.your_product.features), 1)

        # Price fit (30%) - inverted for price increases
        price_change = option.get("parameters", {}).get("price_increase", 0)
        price_score = 1 - (price_change * agent.price_sensitivity)

        # Brand fit (20%)
        brand_score = agent.brand_loyalty

        # Awareness bonus (10%)
        awareness_score = agent.awareness

        total_score = (
            0.40 * feature_score +
            0.30 * price_score +
            0.20 * brand_score +
            0.10 * awareness_score
        )

        return total_score

    def _calculate_sentiment(self, memories: List) -> float:
        """Calculate sentiment from memories (simple version)"""
        if not memories:
            return 0.5

        positive_words = ["good", "great", "excellent", "love", "happy", "satisfied"]
        negative_words = ["bad", "poor", "terrible", "hate", "angry", "frustrated"]

        positive_count = sum(
            1 for m in memories
            for word in positive_words
            if word in m.description.lower()
        )
        negative_count = sum(
            1 for m in memories
            for word in negative_words
            if word in m.description.lower()
        )

        total = positive_count + negative_count
        if total == 0:
            return 0.5

        return positive_count / total

    def _should_competitor_respond(
        self,
        world: World,
        agents: List[Agent],
        day: int
    ) -> bool:
        """Check if competitors should respond"""
        # Simple heuristic: respond if significant market shift
        churned_count = sum(1 for a in agents if a.state == AgentState.CHURNED)
        churn_rate = churned_count / len(agents)

        for competitor in world.competitors:
            if churn_rate > 0.05 and np.random.random() < competitor.aggression:
                return True

        return False

    def _trigger_competitor_response(
        self,
        agents: List[Agent],
        world: World,
        day: int
    ):
        """Trigger a competitor response"""
        # Competitors launch promotion
        for agent in agents:
            if agent.state in [AgentState.CONSIDERING, AgentState.EVALUATING]:
                self.agent_engine.perceive(
                    agent,
                    f"Saw competitor promotion: 'Switch & Save - 3 months free'",
                    sim_time=day
                )

    def _inject_event(
        self,
        agents: List[Agent],
        event: Event,
        world: World
    ):
        """Inject an external event into the simulation"""
        for agent in agents:
            self.agent_engine.perceive(
                agent,
                event.description,
                sim_time=event.day
            )

    def _apply_intervention(
        self,
        agents: List[Agent],
        option: Dict,
        world: World,
        day: int
    ):
        """Apply the decision option as an intervention"""
        # Notify all agents of the change
        intervention_desc = option.get("description", "Change announced")
        for agent in agents:
            self.agent_engine.perceive(agent, intervention_desc, sim_time=day)

    def _take_snapshot(self, agents: List[Agent], day: int) -> DailySnapshot:
        """Take a snapshot of simulation state"""
        state_counts = {}
        for state in AgentState:
            state_counts[state.value] = sum(1 for a in agents if a.state == state)

        retained = state_counts.get(AgentState.RETAINED.value, 0)
        churned = state_counts.get(AgentState.CHURNED.value, 0)
        total = len(agents)

        return DailySnapshot(
            day=day,
            metrics={
                "retention_rate": retained / total if total > 0 else 0,
                "churn_rate": churned / total if total > 0 else 0,
                "awareness_avg": sum(a.awareness for a in agents) / total if total > 0 else 0
            },
            agent_states=state_counts,
            segment_metrics={},  # TODO: Add segment breakdown
            events_triggered=[]
        )

    def _calculate_final_metrics(
        self,
        agents: List[Agent],
        world: World
    ) -> Dict[str, float]:
        """Calculate final simulation metrics"""
        total = len(agents)
        retained = sum(1 for a in agents if a.state == AgentState.RETAINED)
        churned = sum(1 for a in agents if a.state == AgentState.CHURNED)

        return {
            "retention_rate": retained / total if total > 0 else 0,
            "churn_rate": churned / total if total > 0 else 0,
            "net_promoter_estimate": (retained - churned) / total if total > 0 else 0
        }

    def _classify_outcome(
        self,
        metrics: Dict[str, float],
        config: SimulationConfig
    ) -> str:
        """Classify the outcome as success/failure/mixed"""
        retention = metrics.get("retention_rate", 0)

        if retention > 0.90:
            return "success"
        elif retention < 0.80:
            return "failure"
        else:
            return "mixed"

    def _aggregate_results(self, branch_results: List[BranchResult]) -> Dict:
        """Aggregate results across all Monte Carlo branches"""
        if not branch_results:
            return {}

        # Collect all final metrics
        retention_rates = [b.final_metrics["retention_rate"] for b in branch_results]
        churn_rates = [b.final_metrics["churn_rate"] for b in branch_results]

        return {
            "retention": {
                "mean": np.mean(retention_rates),
                "std": np.std(retention_rates),
                "p5": np.percentile(retention_rates, 5),
                "p25": np.percentile(retention_rates, 25),
                "p50": np.percentile(retention_rates, 50),
                "p75": np.percentile(retention_rates, 75),
                "p95": np.percentile(retention_rates, 95)
            },
            "churn": {
                "mean": np.mean(churn_rates),
                "std": np.std(churn_rates),
                "p5": np.percentile(churn_rates, 5),
                "p95": np.percentile(churn_rates, 95)
            },
            "outcome_distribution": {
                "success": sum(1 for b in branch_results if b.outcome == "success") / len(branch_results),
                "mixed": sum(1 for b in branch_results if b.outcome == "mixed") / len(branch_results),
                "failure": sum(1 for b in branch_results if b.outcome == "failure") / len(branch_results)
            },
            "confidence": 1 - np.std(retention_rates)  # Higher std = lower confidence
        }
```

### File: `backend/engine/network_engine.py`
```python
"""
Social Network Effects Engine
Word-of-mouth, influence propagation, cascades
"""

import numpy as np
from typing import List, Dict
from backend.models.agent import Agent, AgentState

class NetworkEngine:
    """Engine for social network effects"""

    def build_network(self, agents: List[Agent], connectivity: float = 0.05):
        """Build social network connections between agents"""
        n = len(agents)

        for i, agent in enumerate(agents):
            # Each agent connects to ~5% of others (configurable)
            num_connections = int(n * connectivity)
            connection_indices = np.random.choice(
                [j for j in range(n) if j != i],
                size=min(num_connections, n - 1),
                replace=False
            )

            for j in connection_indices:
                other = agents[j]
                # Stronger connections within same segment
                same_segment = agent.segment_id == other.segment_id
                trust = np.random.uniform(0.5, 0.9) if same_segment else np.random.uniform(0.2, 0.5)

                from backend.models.agent import Relationship
                agent.relationships.append(Relationship(
                    other_agent_id=other.id,
                    relationship_type="colleague" if same_segment else "acquaintance",
                    trust_level=trust,
                    influence_weight=trust * agent.social_influence
                ))

    def propagate_influence(self, agents: List[Agent], day: int):
        """Propagate social influence through network"""
        agent_map = {a.id: a for a in agents}

        for agent in agents:
            if not agent.relationships:
                continue

            # Check if any connections have churned/retained
            for rel in agent.relationships:
                other = agent_map.get(rel.other_agent_id)
                if not other:
                    continue

                # Word of mouth from churned connections
                if other.state == AgentState.CHURNED:
                    if np.random.random() < rel.influence_weight * 0.3:
                        # Influence towards churning
                        agent.awareness += 0.1
                        if agent.state == AgentState.CONSIDERING:
                            # Record this influence
                            from backend.models.agent import Memory
                            mem = Memory(
                                id=f"mem_{len(agent.memory_stream)}",
                                timestamp=day,
                                description=f"Heard that {other.name} left for competitor",
                                importance=7.0,
                                type="social"
                            )
                            agent.memory_stream.append(mem)

                # Word of mouth from retained connections
                elif other.state == AgentState.RETAINED:
                    if np.random.random() < rel.influence_weight * 0.2:
                        # Influence towards retention
                        agent.brand_loyalty += 0.05

    def identify_influencers(self, agents: List[Agent]) -> List[Agent]:
        """Identify high-influence agents in the network"""
        # Agents with most connections and highest trust
        influence_scores = []

        for agent in agents:
            total_influence = sum(r.influence_weight for r in agent.relationships)
            influence_scores.append((agent, total_influence))

        influence_scores.sort(key=lambda x: x[1], reverse=True)

        # Return top 10%
        top_n = max(1, len(agents) // 10)
        return [agent for agent, _ in influence_scores[:top_n]]

    def simulate_cascade(
        self,
        agents: List[Agent],
        trigger_agent_ids: List[str],
        cascade_type: str  # "churn" or "adoption"
    ) -> Dict:
        """Simulate a cascade effect from trigger agents"""
        agent_map = {a.id: a for a in agents}
        affected = set(trigger_agent_ids)
        wave = 0
        cascade_log = []

        current_wave = set(trigger_agent_ids)

        while current_wave:
            next_wave = set()
            wave += 1

            for agent_id in current_wave:
                agent = agent_map.get(agent_id)
                if not agent:
                    continue

                for rel in agent.relationships:
                    if rel.other_agent_id in affected:
                        continue

                    other = agent_map.get(rel.other_agent_id)
                    if not other:
                        continue

                    # Probability of cascade
                    cascade_prob = rel.influence_weight * other.social_influence

                    if np.random.random() < cascade_prob:
                        next_wave.add(rel.other_agent_id)
                        affected.add(rel.other_agent_id)

            cascade_log.append({
                "wave": wave,
                "new_affected": len(next_wave),
                "total_affected": len(affected)
            })

            current_wave = next_wave

            # Safety limit
            if wave > 10:
                break

        return {
            "total_affected": len(affected),
            "waves": wave,
            "cascade_log": cascade_log,
            "multiplier": len(affected) / max(len(trigger_agent_ids), 1)
        }
```

I need to continue with the rest of the engines and then the API layer and frontend. Let me continue in the next part.
