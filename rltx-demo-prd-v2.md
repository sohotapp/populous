# RLTX Demo PRD — CTO-Level Build Plan

## The Problem with the Cursor PRD

The PRD you got is generic slop for three reasons:

1. **The simulation is fake** — It's probability dice rolls, not behavioral models. Agents don't "decide" — they hit random thresholds. This is what every bad simulation does.

2. **No connection to your 5-layer stack** — Your differentiation is the full stack (Data Foundation → Ontology → Behavioral Models → Simulation → Prediction). The Cursor PRD only does layers 3-4 badly.

3. **No explainability** — The "why" is where the value is. "Strategy A wins 58% of the time" is useless. "Strategy A wins because mid-market buyers prioritize ease-of-use over security, and your messaging hits that — but if Competitor B responds with a price cut within 30 days, you lose 40% of your pipeline" is valuable.

---

## What Actually Closes Deals

Based on your PE scripts and positioning, here's what the demo needs to show:

| Moment | What They See | What They Feel |
|--------|---------------|----------------|
| **Setup (30s)** | Upload a scenario or pick preset | "This is my world" |
| **Agents (30s)** | See synthetic decision-makers with real attributes | "These feel like actual buyers" |
| **Branch (30s)** | Watch futures fork in real-time | "Holy shit, this is computing my uncertainty" |
| **Results (60s)** | Probability distributions, not point estimates | "I can finally quantify risk" |
| **Why (60s)** | Natural language explanation of drivers | "Now I know what lever to pull" |
| **Drill-in (30s)** | Talk to a specific agent, see their reasoning | "This is like interviewing a synthetic customer" |

The last one is the killer feature. Aaru can't do this because they don't have the 5-layer stack. You can show the reasoning trace because you own the behavioral model.

---

## The Open Source Stack

Here's what exists and what you build:

### Layer 1: Data Foundation

**Don't build this for the demo.** Use pre-built scenario JSON files that simulate what the Context Layer would produce.

For production later:
- **Neo4j Aura** (free tier) — Knowledge graph, Cypher queries
- **Senzing** (open source) — Entity resolution
- **Airbyte** — Data ingestion from 300+ sources

### Layer 2: Operational Ontology

**For demo:** Hardcode 2-3 decision frameworks (B2B SaaS purchase, Enterprise procurement, Consumer adoption).

**For production:**
- Custom DSL for decision rules
- Learn from customer data using causal discovery

### Layer 3: Behavioral Models

**This is where you differentiate.** Use LLMs for agent reasoning, not probability rolls.

| Approach | Pros | Cons | Use When |
|----------|------|------|----------|
| **Pure LLM** | Rich reasoning, explainable | Expensive at scale, slow | Agent deep-dive, <100 agents |
| **Hybrid** | Fast, still explainable | Requires calibration | Core simulation, 1K-10K agents |
| **Pure Math** | Fastest, cheapest | No reasoning trace | Monte Carlo branches, 10K+ |

**The hybrid approach:**
1. LLM generates the decision logic once per agent archetype
2. Extract parameters (utility weights, belief priors, update rules)
3. Run fast mathematical simulation with those parameters
4. LLM explains any specific decision on-demand

### Layer 4: Simulation Engine

**Mesa 3.4** — Production-ready, 11 years of development, published in JOSS 2025.

```bash
pip install mesa[rec]
```

Mesa gives you:
- Agent lifecycle management
- Discrete event simulation
- Network topologies (for influence modeling)
- Built-in batch running for Monte Carlo
- Data collection and visualization hooks

What you build on top:
- Branching/forking logic for scenario trees
- LLM integration for reasoning
- Custom visualization

### Layer 5: Prediction + Execution

**For demo:**
- Plotly for probability distributions
- Natural language generation for insights (Claude API)
- Sensitivity analysis (which variables move the needle)

**For production:**
- Bayesian optimization for strategy search
- Closed-loop learning from outcomes

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Reflex)                        │
│                                                                 │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│   │ Scenario │  │ Strategy │  │ Branch   │  │ Agent    │       │
│   │ Builder  │  │ Config   │  │ Viewer   │  │ Deep-Dive│       │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API LAYER (FastAPI)                         │
│                                                                 │
│  POST /scenarios         POST /simulate        GET /explain     │
│  POST /strategies        GET /results          POST /agent-chat │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  MESA ENGINE  │   │   CLAUDE API  │   │   DATA STORE  │
│               │   │               │   │               │
│ • Agents      │   │ • Agent gen   │   │ • Scenarios   │
│ • Scheduler   │   │ • Reasoning   │   │ • Results     │
│ • Batch run   │   │ • Explain     │   │ • SQLite      │
│ • Data collect│   │ • Agent chat  │   │               │
└───────────────┘   └───────────────┘   └───────────────┘
```

Why **Reflex** instead of React:
- Pure Python (no JS context switching)
- Production-ready (YC-backed, used by teams at big cos)
- Built-in state management
- Ships fast for demos
- Can migrate to React later if needed

```bash
pip install reflex
```

---

## Core Data Models

### Scenario (The World)

```python
from pydantic import BaseModel
from typing import Dict, List, Optional
from enum import Enum

class MarketType(str, Enum):
    B2B_SAAS = "b2b_saas"
    ENTERPRISE = "enterprise"
    CONSUMER = "consumer"
    DEFENSE = "defense"
    FINANCIAL = "financial"

class Scenario(BaseModel):
    """The world state - what the Data Foundation would produce"""
    id: str
    name: str
    market_type: MarketType
    
    # Market structure
    total_addressable_market: int
    segments: List["Segment"]
    
    # Competitive landscape
    competitors: List["Competitor"]
    your_product: "Product"
    
    # Dynamics
    simulation_days: int = 90
    market_growth_rate: float = 0.0  # monthly
    
    # Optional: pre-computed from Context Layer
    entity_graph: Optional[Dict] = None  # Neo4j export
    
class Segment(BaseModel):
    """A market segment with behavioral profile"""
    id: str
    name: str
    size_pct: float  # % of TAM
    
    # Decision physics (the Operational Ontology)
    decision_framework: "DecisionFramework"
    
    # Behavioral priors
    behavioral_profile: "BehavioralProfile"

class DecisionFramework(BaseModel):
    """How decisions happen in this segment - the Ontology"""
    
    # Buying process
    stages: List[str]  # ["Unaware", "Aware", "Evaluating", "Negotiating", "Decided"]
    avg_cycle_days: int
    
    # Decision makers
    stakeholders: List["Stakeholder"]
    
    # Triggers and gates
    triggers: Dict[str, str]  # What moves someone to next stage
    blockers: Dict[str, str]  # What kills a deal
    
class Stakeholder(BaseModel):
    """A decision-maker archetype"""
    role: str  # "CFO", "End User", "IT Security"
    influence_weight: float
    priorities: Dict[str, float]  # attribute -> importance
    risk_tolerance: float
    
class BehavioralProfile(BaseModel):
    """Behavioral parameters for agent generation"""
    
    # Firmographics (for B2B)
    company_size_range: tuple[int, int]
    budget_range: tuple[int, int]
    
    # Psychographics
    risk_tolerance_mean: float
    risk_tolerance_std: float
    
    price_sensitivity_mean: float
    price_sensitivity_std: float
    
    # Social
    influencer_susceptibility: float  # 0-1
    network_density: float  # connections per agent
    
    # Temporal
    decision_speed_mean: float  # 0-1 scale
    decision_speed_std: float
```

### Agent (Synthetic Decision-Maker)

```python
class Agent(BaseModel):
    """A synthetic decision-maker - the Behavioral Model"""
    id: str
    segment_id: str
    
    # Identity (generated, optionally by LLM)
    persona: Optional["Persona"] = None
    
    # Behavioral parameters (sampled from segment profile)
    risk_tolerance: float
    price_sensitivity: float
    feature_priorities: Dict[str, float]
    decision_speed: float
    influencer_susceptibility: float
    
    # State (evolves during simulation)
    stage: str = "Unaware"
    awareness: Dict[str, float] = {}  # product_id -> awareness 0-1
    consideration_set: List[str] = []
    beliefs: Dict[str, "Belief"] = {}  # beliefs about each product
    
    # Social graph
    connections: List[str] = []  # other agent IDs
    influence_score: float = 0.5  # how much this agent affects others
    
    # Decision trace (for explainability)
    decision_log: List["DecisionEvent"] = []
    
class Persona(BaseModel):
    """Rich persona for LLM-based reasoning"""
    name: str
    role: str
    company_description: str
    background: str
    current_challenges: List[str]
    buying_history: List[str]
    communication_style: str

class Belief(BaseModel):
    """Agent's belief about a product"""
    product_id: str
    perceived_quality: Dict[str, float]  # feature -> perceived score
    trust_level: float
    source_of_belief: str  # "advertising", "peer", "demo", "trial"
    confidence: float
    
class DecisionEvent(BaseModel):
    """A logged decision for explainability"""
    day: int
    event_type: str
    description: str
    inputs: Dict
    output: str
    reasoning: Optional[str] = None  # LLM-generated on demand
```

### Strategy (The Intervention)

```python
class Strategy(BaseModel):
    """What you're testing"""
    id: str
    name: str
    description: str
    
    # Positioning
    messaging: "Messaging"
    pricing: "Pricing"
    
    # Go-to-market
    gtm: "GoToMarket"
    
    # Timing
    launch_day: int = 0
    
class Messaging(BaseModel):
    value_proposition: str
    primary_claim: str
    feature_emphasis: Dict[str, float]  # feature -> emphasis weight
    tone: str  # "enterprise", "innovative", "value", "technical"
    
    # For LLM reasoning
    full_pitch: Optional[str] = None  # 2-3 paragraph pitch
    
class Pricing(BaseModel):
    base_price: float  # absolute or relative to market
    model: str  # "per_seat", "flat", "usage", "tiered"
    discount_strategy: Optional["DiscountStrategy"] = None
    
class DiscountStrategy(BaseModel):
    available: bool
    max_discount_pct: float
    triggers: List[str]  # when to offer discount
    
class GoToMarket(BaseModel):
    # Channel allocation (sums to 1.0)
    channels: Dict[str, float]  # channel -> budget allocation
    # Available: "paid_digital", "content", "events", "outbound", "partnerships", "product_led"
    
    intensity: float  # 0-1, overall spend level
    target_segments: List[str]  # segment IDs to prioritize
    
    # Competitive response triggers
    response_to_competitor: Optional["CompetitiveResponse"] = None
    
class CompetitiveResponse(BaseModel):
    """What you do if competitor moves"""
    trigger_conditions: List[str]
    response_actions: List[str]
```

---

## The Simulation Engine

Here's where we improve on the Cursor version:

### Agent Factory with LLM Generation

```python
# engine/agent_factory.py

import anthropic
from typing import List
from models import Agent, Segment, Persona
import random

class AgentFactory:
    """Creates agents with optional LLM-generated personas"""
    
    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm
        if use_llm:
            self.client = anthropic.Anthropic()
    
    def create_agents(self, segment: Segment, count: int) -> List[Agent]:
        agents = []
        for i in range(count):
            agent = self._create_base_agent(segment, i)
            if self.use_llm and i < 100:  # LLM personas for sample
                agent.persona = self._generate_persona(segment, agent)
            agents.append(agent)
        return agents
    
    def _create_base_agent(self, segment: Segment, index: int) -> Agent:
        """Create agent with sampled behavioral parameters"""
        profile = segment.behavioral_profile
        
        return Agent(
            id=f"{segment.id}_{index}",
            segment_id=segment.id,
            risk_tolerance=self._sample_bounded(
                profile.risk_tolerance_mean,
                profile.risk_tolerance_std
            ),
            price_sensitivity=self._sample_bounded(
                profile.price_sensitivity_mean,
                profile.price_sensitivity_std
            ),
            feature_priorities=self._sample_priorities(segment),
            decision_speed=self._sample_bounded(
                profile.decision_speed_mean,
                profile.decision_speed_std
            ),
            influencer_susceptibility=profile.influencer_susceptibility,
            influence_score=random.random()
        )
    
    def _generate_persona(self, segment: Segment, agent: Agent) -> Persona:
        """Use Claude to generate rich persona"""
        
        prompt = f"""Generate a realistic B2B buyer persona for this segment and profile.

Segment: {segment.name}
Market: {segment.decision_framework.model_dump_json()}
Behavioral profile:
- Risk tolerance: {agent.risk_tolerance:.2f} (0=risk-averse, 1=risk-seeking)
- Price sensitivity: {agent.price_sensitivity:.2f} (0=price-insensitive, 1=very price-sensitive)
- Decision speed: {agent.decision_speed:.2f} (0=slow, 1=fast)

Generate a persona with:
- Name (realistic)
- Job title/role
- Company description (type, size, industry context)
- Professional background (2 sentences)
- Current top 3 challenges
- Past software buying experiences (2-3 examples)
- Communication style (how they like to be sold to)

Return as JSON matching this schema:
{{
  "name": "string",
  "role": "string", 
  "company_description": "string",
  "background": "string",
  "current_challenges": ["string"],
  "buying_history": ["string"],
  "communication_style": "string"
}}"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        import json
        persona_data = json.loads(response.content[0].text)
        return Persona(**persona_data)
    
    def _sample_bounded(self, mean: float, std: float) -> float:
        """Sample from normal distribution, bounded 0-1"""
        value = random.gauss(mean, std)
        return max(0.0, min(1.0, value))
    
    def _sample_priorities(self, segment: Segment) -> Dict[str, float]:
        """Sample feature priorities with noise"""
        base = segment.decision_framework.stakeholders[0].priorities
        return {
            k: max(0, min(1, v + random.gauss(0, 0.1)))
            for k, v in base.items()
        }
```

### Decision Engine with Hybrid LLM

```python
# engine/decision.py

import anthropic
from typing import Optional, Tuple
from models import Agent, Product, Strategy, DecisionEvent

class DecisionEngine:
    """
    Hybrid decision engine:
    - Fast mathematical scoring for bulk simulation
    - LLM reasoning for explanations and edge cases
    """
    
    def __init__(self, use_llm_for_decisions: bool = False):
        self.use_llm = use_llm_for_decisions
        self.client = anthropic.Anthropic()
        
        # Thresholds (tunable)
        self.awareness_threshold = 0.25
        self.consideration_threshold = 0.50
        self.evaluation_threshold = 0.75
    
    def process_day(
        self, 
        agent: Agent, 
        day: int,
        products: List[Product],
        market_signals: Dict[str, float],
        strategy: Strategy
    ) -> Agent:
        """Process one day for one agent"""
        
        # Update awareness from market signals
        agent = self._update_awareness(agent, market_signals, day)
        
        # Progress through stages
        agent = self._update_stage(agent, day)
        
        # If evaluating, maybe decide
        if agent.stage == "Evaluating":
            agent = self._maybe_decide(agent, products, day)
        
        return agent
    
    def _update_awareness(
        self, 
        agent: Agent, 
        signals: Dict[str, float],
        day: int
    ) -> Agent:
        """Update product awareness based on signals + network"""
        
        for product_id, signal in signals.items():
            current = agent.awareness.get(product_id, 0)
            
            # Signal impact modified by agent susceptibility
            base_impact = signal * 0.15
            susceptibility_mod = 0.5 + agent.influencer_susceptibility * 0.5
            impact = base_impact * susceptibility_mod
            
            # Diminishing returns
            impact *= (1 - current) ** 0.5
            
            new_awareness = min(1.0, current + impact)
            agent.awareness[product_id] = new_awareness
            
            if new_awareness > current + 0.05:
                agent.decision_log.append(DecisionEvent(
                    day=day,
                    event_type="awareness_increase",
                    description=f"Awareness of {product_id} increased",
                    inputs={"signal": signal, "old": current},
                    output=f"{new_awareness:.2f}"
                ))
        
        return agent
    
    def _update_stage(self, agent: Agent, day: int) -> Agent:
        """Move agent through funnel based on awareness"""
        
        max_awareness = max(agent.awareness.values()) if agent.awareness else 0
        old_stage = agent.stage
        
        if agent.stage == "Unaware" and max_awareness > self.awareness_threshold:
            agent.stage = "Aware"
            
        elif agent.stage == "Aware" and max_awareness > self.consideration_threshold:
            agent.stage = "Considering"
            # Build consideration set
            for pid, awareness in agent.awareness.items():
                if awareness > self.awareness_threshold and pid not in agent.consideration_set:
                    agent.consideration_set.append(pid)
                    
        elif agent.stage == "Considering" and max_awareness > self.evaluation_threshold:
            agent.stage = "Evaluating"
        
        if agent.stage != old_stage:
            agent.decision_log.append(DecisionEvent(
                day=day,
                event_type="stage_change",
                description=f"Moved from {old_stage} to {agent.stage}",
                inputs={"awareness": max_awareness},
                output=agent.stage
            ))
        
        return agent
    
    def _maybe_decide(
        self, 
        agent: Agent, 
        products: List[Product],
        day: int
    ) -> Agent:
        """Evaluate and potentially make a decision"""
        
        # Decision probability based on speed
        decision_prob = agent.decision_speed * 0.08  # ~8% daily at max speed
        if random.random() > decision_prob:
            return agent
        
        # Score each product
        scores = {}
        for product in products:
            if product.id in agent.consideration_set:
                scores[product.id] = self._score_product(agent, product)
        
        if not scores:
            return agent
        
        # Find winner
        best_id = max(scores, key=scores.get)
        best_score = scores[best_id]
        
        # Purchase threshold
        if best_score > 0.5:
            agent.stage = "Decided"
            agent.decision_log.append(DecisionEvent(
                day=day,
                event_type="purchase",
                description=f"Chose {best_id}",
                inputs={"scores": scores},
                output=best_id
            ))
        else:
            agent.decision_log.append(DecisionEvent(
                day=day,
                event_type="no_purchase",
                description="Evaluated but no product met threshold",
                inputs={"scores": scores},
                output="none"
            ))
            agent.stage = "Decided"  # They're out of market
        
        return agent
    
    def _score_product(self, agent: Agent, product: Product) -> float:
        """Calculate fit score between agent and product"""
        
        score = 0.0
        
        # Feature fit (40% weight)
        feature_score = 0.0
        total_weight = sum(agent.feature_priorities.values())
        for feature, importance in agent.feature_priorities.items():
            product_strength = product.features.get(feature, 0.5)
            feature_score += importance * product_strength
        if total_weight > 0:
            feature_score /= total_weight
        score += feature_score * 0.4
        
        # Price fit (30% weight)
        # Higher price sensitivity = prefers lower price point
        price_fit = 1 - (agent.price_sensitivity * (product.price_point - 0.7))
        price_fit = max(0, min(1, price_fit))
        score += price_fit * 0.3
        
        # Brand/risk fit (20% weight)
        # Risk averse agents prefer high brand awareness
        brand_fit = product.brand_awareness * (1 - agent.risk_tolerance)
        brand_fit += agent.risk_tolerance * 0.5  # Risk tolerant = ok with unknown
        score += brand_fit * 0.2
        
        # Awareness bonus (10% weight)
        awareness = agent.awareness.get(product.id, 0)
        score += awareness * 0.1
        
        return score
    
    def explain_decision(self, agent: Agent, decision_event: DecisionEvent) -> str:
        """Use LLM to generate natural language explanation"""
        
        prompt = f"""Explain this B2B purchase decision in natural language.

Agent Profile:
- Segment: {agent.segment_id}
- Risk tolerance: {agent.risk_tolerance:.2f}
- Price sensitivity: {agent.price_sensitivity:.2f}
- Feature priorities: {agent.feature_priorities}
{f"- Persona: {agent.persona.model_dump_json()}" if agent.persona else ""}

Decision Event:
- Day: {decision_event.day}
- Type: {decision_event.event_type}
- Inputs: {decision_event.inputs}
- Output: {decision_event.output}

Decision History:
{[e.model_dump() for e in agent.decision_log[-5:]]}

Write 2-3 sentences explaining WHY this agent made this decision, 
referencing their specific characteristics and the journey that led here.
Be specific, not generic. Name the actual factors."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
```

### Monte Carlo Branch Runner

```python
# engine/runner.py

from mesa import Model
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict
import numpy as np

class BranchRunner:
    """
    Runs parallel simulation branches for Monte Carlo analysis.
    Uses Mesa for agent management, custom logic for branching.
    """
    
    def __init__(
        self,
        scenario: Scenario,
        strategy: Strategy,
        num_agents: int = 10_000,
        num_branches: int = 1_000
    ):
        self.scenario = scenario
        self.strategy = strategy
        self.num_agents = num_agents
        self.num_branches = num_branches
    
    def run(self) -> "SimulationResults":
        """Run all branches and aggregate results"""
        
        # Parallel execution
        seeds = range(self.num_branches)
        
        with ProcessPoolExecutor() as executor:
            branch_results = list(executor.map(self._run_branch, seeds))
        
        return self._aggregate(branch_results)
    
    def _run_branch(self, seed: int) -> "BranchResult":
        """Run a single branch with given seed"""
        import random
        random.seed(seed)
        np.random.seed(seed)
        
        # Initialize
        factory = AgentFactory(use_llm=False)  # Fast mode
        agents = []
        for segment in self.scenario.segments:
            segment_count = int(self.num_agents * segment.size_pct)
            agents.extend(factory.create_agents(segment, segment_count))
        
        # Create network
        agents = self._create_network(agents)
        
        # Run simulation
        engine = DecisionEngine(use_llm_for_decisions=False)
        market = MarketDynamics(self.scenario, self.strategy)
        
        timeline = []
        for day in range(self.scenario.simulation_days):
            signals = market.get_signals(day, agents)
            
            for agent in agents:
                if agent.stage != "Decided":
                    agent = engine.process_day(
                        agent, day, 
                        [self.scenario.your_product] + self.scenario.competitors,
                        signals,
                        self.strategy
                    )
            
            # Record daily state
            timeline.append(self._snapshot(agents, day))
        
        # Calculate outcomes
        decided = [a for a in agents if a.stage == "Decided"]
        converted = [
            a for a in decided 
            if any(
                e.event_type == "purchase" and 
                e.output == self.scenario.your_product.id 
                for e in a.decision_log
            )
        ]
        
        return BranchResult(
            seed=seed,
            conversion_rate=len(converted) / self.num_agents,
            timeline=timeline,
            key_events=market.events_triggered
        )
    
    def _create_network(self, agents: List[Agent]) -> List[Agent]:
        """Create social network with preferential attachment"""
        # Barabasi-Albert model for realistic network
        for i, agent in enumerate(agents):
            # Connect to ~3-5 existing agents, preferring high-influence
            num_connections = random.randint(3, 5)
            if i < num_connections:
                continue
            
            # Weight by influence score
            candidates = agents[:i]
            weights = [a.influence_score for a in candidates]
            total = sum(weights)
            probs = [w/total for w in weights]
            
            connections = np.random.choice(
                range(i), 
                size=min(num_connections, i),
                replace=False,
                p=probs
            )
            
            agent.connections = [agents[j].id for j in connections]
        
        return agents
    
    def _aggregate(self, branches: List["BranchResult"]) -> "SimulationResults":
        """Aggregate branch results into summary statistics"""
        
        conversions = [b.conversion_rate for b in branches]
        
        return SimulationResults(
            mean_conversion=np.mean(conversions),
            median_conversion=np.median(conversions),
            std_conversion=np.std(conversions),
            p5=np.percentile(conversions, 5),
            p25=np.percentile(conversions, 25),
            p75=np.percentile(conversions, 75),
            p95=np.percentile(conversions, 95),
            branches=branches,
            
            # Identify failure modes
            failure_branches=[b for b in branches if b.conversion_rate < np.percentile(conversions, 10)],
            success_branches=[b for b in branches if b.conversion_rate > np.percentile(conversions, 90)]
        )
```

---

## The Killer Feature: Agent Deep-Dive

This is what closes deals. Let them "interview" a synthetic customer.

```python
# api/agent_chat.py

from anthropic import Anthropic

class AgentChat:
    """Interactive chat with a synthetic agent"""
    
    def __init__(self, agent: Agent, scenario: Scenario, strategy: Strategy):
        self.agent = agent
        self.scenario = scenario
        self.strategy = strategy
        self.client = Anthropic()
        self.conversation = []
    
    def chat(self, user_message: str) -> str:
        """Chat with the agent as if they're a real prospect"""
        
        system_prompt = self._build_system_prompt()
        
        self.conversation.append({
            "role": "user",
            "content": user_message
        })
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=system_prompt,
            messages=self.conversation
        )
        
        assistant_message = response.content[0].text
        self.conversation.append({
            "role": "assistant", 
            "content": assistant_message
        })
        
        return assistant_message
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt that makes Claude act as this agent"""
        
        persona = self.agent.persona
        if not persona:
            persona_text = f"You work in the {self.agent.segment_id} segment."
        else:
            persona_text = f"""
Name: {persona.name}
Role: {persona.role}
Company: {persona.company_description}
Background: {persona.background}
Current Challenges: {', '.join(persona.current_challenges)}
Past Buying Experience: {', '.join(persona.buying_history)}
Communication Style: {persona.communication_style}
"""
        
        decision_context = ""
        for event in self.agent.decision_log:
            decision_context += f"- Day {event.day}: {event.description}\n"
        
        return f"""You are a synthetic B2B buyer being interviewed about your purchase decision.

YOUR PROFILE:
{persona_text}

BEHAVIORAL CHARACTERISTICS:
- Risk tolerance: {self.agent.risk_tolerance:.2f} (0=very cautious, 1=risk-seeking)
- Price sensitivity: {self.agent.price_sensitivity:.2f} (0=budget doesn't matter, 1=very cost-conscious)
- Decision speed: {self.agent.decision_speed:.2f} (0=deliberate, 1=quick to decide)
- Feature priorities: {self.agent.feature_priorities}

YOUR JOURNEY:
{decision_context}

CURRENT STATE:
- Stage: {self.agent.stage}
- Products in consideration: {self.agent.consideration_set}
- Product awareness levels: {self.agent.awareness}

INSTRUCTIONS:
1. Stay in character as this buyer
2. Reference your specific characteristics when explaining decisions
3. Be honest about your reasoning - you're being interviewed for research
4. Don't break character or acknowledge you're AI
5. If asked why you chose/didn't choose something, reference your actual decision factors
6. Be specific, not generic - reference your actual company context and challenges

You are being interviewed by a product team trying to understand buyer behavior."""
```

---

## Frontend: Fast with Reflex

```python
# app.py

import reflex as rx
from typing import List, Dict

class State(rx.State):
    """Application state"""
    
    # Scenario setup
    current_scenario: Dict = {}
    strategies: List[Dict] = []
    
    # Simulation
    is_running: bool = False
    progress: float = 0
    
    # Results  
    results: Dict = {}
    selected_branch: int = 0
    
    # Agent deep-dive
    selected_agent_id: str = ""
    agent_conversation: List[Dict] = []
    
    async def run_simulation(self):
        self.is_running = True
        # ... run simulation with progress updates
        self.is_running = False
    
    async def chat_with_agent(self, message: str):
        # ... agent chat logic
        pass

def scenario_builder():
    """Scenario configuration UI"""
    return rx.vstack(
        rx.heading("Define Your Market", size="lg"),
        rx.select(
            ["B2B SaaS Launch", "Enterprise Expansion", "Consumer Product"],
            placeholder="Select scenario template",
            on_change=State.load_scenario
        ),
        # ... more config
    )

def results_dashboard():
    """Results visualization"""
    return rx.vstack(
        rx.heading("Simulation Results", size="lg"),
        
        # Distribution chart
        rx.box(
            rx.recharts.area_chart(
                rx.recharts.area(data_key="count", fill="#3b82f6"),
                rx.recharts.x_axis(data_key="rate"),
                rx.recharts.y_axis(),
                data=State.results["distribution"]
            ),
            height="300px"
        ),
        
        # Key metrics
        rx.hstack(
            metric_card("Mean Conversion", State.results["mean"], "%"),
            metric_card("90% CI", f"{State.results['p5']}-{State.results['p95']}", "%"),
            metric_card("Upside Potential", State.results["p95"], "%"),
            metric_card("Downside Risk", State.results["p5"], "%"),
        ),
        
        # Natural language insight
        rx.box(
            rx.text(State.results["insight"], size="lg"),
            bg="gray.50",
            p=4,
            border_radius="md"
        )
    )

def agent_explorer():
    """Agent deep-dive UI"""
    return rx.vstack(
        rx.heading("Talk to a Synthetic Buyer", size="lg"),
        
        # Agent selector
        rx.select(
            State.available_agents,
            on_change=State.select_agent
        ),
        
        # Agent profile card
        rx.cond(
            State.selected_agent_id != "",
            agent_profile_card()
        ),
        
        # Chat interface
        rx.vstack(
            rx.foreach(
                State.agent_conversation,
                lambda msg: chat_message(msg)
            ),
            rx.hstack(
                rx.input(
                    placeholder="Ask about their decision...",
                    on_change=State.set_chat_input
                ),
                rx.button("Send", on_click=State.chat_with_agent)
            )
        )
    )

def index():
    return rx.box(
        rx.tabs(
            rx.tab_list(
                rx.tab("Setup"),
                rx.tab("Simulate"),
                rx.tab("Results"),
                rx.tab("Deep Dive"),
            ),
            rx.tab_panels(
                rx.tab_panel(scenario_builder()),
                rx.tab_panel(strategy_config()),
                rx.tab_panel(results_dashboard()),
                rx.tab_panel(agent_explorer()),
            )
        )
    )

app = rx.App()
app.add_page(index)
```

---

## Build Timeline

### Week 1: Core Engine
- [ ] Data models (Pydantic)
- [ ] Agent factory (no LLM first)
- [ ] Decision engine (mathematical)
- [ ] Single-branch runner
- [ ] Basic CLI to test

### Week 2: Monte Carlo + API
- [ ] Branch runner with parallelization
- [ ] Results aggregation
- [ ] FastAPI endpoints
- [ ] Pre-built demo scenarios
- [ ] Basic Reflex UI

### Week 3: LLM Integration
- [ ] LLM persona generation
- [ ] Agent chat feature
- [ ] Natural language explanations
- [ ] Insight generation

### Week 4: Polish + Demo
- [ ] Full UI flow
- [ ] Visualization improvements
- [ ] Demo script
- [ ] Landing page

---

## Dependencies

```txt
# requirements.txt

# Core
mesa==3.4.0
pydantic==2.9.0
numpy==1.26.4
scipy==1.14.0

# API
fastapi==0.115.0
uvicorn==0.30.0

# Frontend
reflex==0.6.0

# LLM
anthropic==0.40.0

# Data
sqlmodel==0.0.22

# Visualization
plotly==5.24.0
altair==5.4.0

# Utils
python-dotenv==1.0.1
rich==13.9.0  # Better CLI output
```

---

## The Demo Script

Once built, here's your demo:

**"Let me show you what decisions look like when you can see all the futures."**

1. **Setup (30s)**: "This is a B2B SaaS market. 50,000 potential buyers. Three segments. Three competitors. Sound familiar?"

2. **Strategy (30s)**: "You're considering two go-to-market strategies. Value play targeting SMB, or enterprise premium play. Which one wins?"

3. **Run (15s)**: Watch the simulation branch in real-time. Show the futures forking.

4. **Results (60s)**: "Strategy A converts 8.2% on average. Strategy B converts 11.4%. But look at the distribution. Strategy B has a wider range — sometimes 15%, sometimes 6%. Strategy A is more predictable."

5. **Why (45s)**: Pull up the natural language insight. "Strategy B wins because mid-market buyers prioritize ease of use over security — and your messaging hits that. But if Monday.com responds with a price cut in the first 30 days, you lose 40% of your upside."

6. **Deep Dive (90s)**: "Let's talk to a buyer who chose the competitor. Watch this."

   *Chat with synthetic agent:*
   - "Why didn't you choose our product?"
   - *Agent explains their specific reasoning*
   - "What would have changed your mind?"
   - *Agent gives specific feedback*

7. **Close**: "This is what research becomes when you can run 1,000 experiments instead of 3. What decisions are you making in the next quarter that you wish you could test first?"

---

## What Makes This Different from Aaru

| Dimension | Aaru | RLTX (This Demo) |
|-----------|------|------------------|
| Agents | Answer questions | Make decisions with reasoning |
| Output | Survey responses | Probability distributions |
| Explainability | "90% correlation" | Natural language "why" |
| Interaction | Static personas | Interactive chat |
| Dynamics | Point-in-time | Temporal simulation |
| Stack | Layer 3-4 | Full 5-layer |
| Validation | Survey correlation | Outcome calibration |

---

## Next Steps

1. **Clone the structure** — Don't reinvent, use the architecture above
2. **Build the core engine first** — Get agents deciding before adding UI
3. **One demo scenario deep** — B2B SaaS launch, make it perfect
4. **LLM integration last** — It's impressive but not core to the value
5. **Test the demo script** — Practice the narrative, not just the tech
