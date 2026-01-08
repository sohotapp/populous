# RLTX POPULOUS — COMPLETE BUILD GUIDE

## For Claude: Build This End-to-End

This document contains everything needed to build a working RLTX Populous demo. Follow the steps in order. Each section builds on the previous.

---

# PART 1: PROJECT SETUP

## 1.1 Create Project Structure

```bash
mkdir rltx-populous
cd rltx-populous

# Create directory structure
mkdir -p backend/{models,engine,api,data/presets}
mkdir -p frontend/src/{components,pages,api}
mkdir -p scripts
mkdir -p tests

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## 1.2 Install Dependencies

Create `requirements.txt`:

```txt
# Core simulation
mesa==3.4.0
pydantic==2.9.2
numpy==1.26.4
scipy==1.14.1

# API
fastapi==0.115.0
uvicorn[standard]==0.31.0

# LLM
anthropic==0.39.0

# Database
sqlmodel==0.0.22
aiosqlite==0.20.0

# Data processing
pandas==2.2.3

# Visualization (for API responses)
plotly==5.24.1

# Utilities
python-dotenv==1.0.1
rich==13.9.2
httpx==0.27.2

# Testing
pytest==8.3.3
pytest-asyncio==0.24.0
```

Install:
```bash
pip install -r requirements.txt
```

## 1.3 Environment Setup

Create `.env`:
```env
ANTHROPIC_API_KEY=your_key_here
DATABASE_URL=sqlite:///./rltx.db
DEBUG=true
```

---

# PART 2: DATA MODELS

## 2.1 Core Models

Create `backend/models/__init__.py`:
```python
from .scenario import *
from .agent import *
from .strategy import *
from .results import *
```

Create `backend/models/scenario.py`:

```python
"""
Scenario models - defines the market environment.
This is what the Data Foundation (Layer 1) produces.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum


class MarketType(str, Enum):
    B2B_SAAS = "b2b_saas"
    ENTERPRISE = "enterprise"
    CONSUMER = "consumer"
    FINANCIAL = "financial"
    DEFENSE = "defense"


class Stakeholder(BaseModel):
    """A decision-maker archetype within a segment"""
    role: str  # "CFO", "End User", "IT Security", "Champion"
    influence_weight: float = Field(ge=0, le=1)
    priorities: Dict[str, float]  # feature -> importance (0-1)
    risk_tolerance: float = Field(ge=0, le=1)
    
    
class DecisionFramework(BaseModel):
    """
    How decisions happen in this segment.
    This is the Operational Ontology (Layer 2).
    """
    stages: List[str] = ["Unaware", "Aware", "Considering", "Evaluating", "Decided"]
    avg_cycle_days: int = 45
    stakeholders: List[Stakeholder]
    
    # What triggers stage transitions
    triggers: Dict[str, str] = {
        "Unaware->Aware": "Marketing touchpoint or peer mention",
        "Aware->Considering": "Problem recognition + solution awareness",
        "Considering->Evaluating": "Active research, demo request",
        "Evaluating->Decided": "Business case approved, vendor selected"
    }
    
    # What kills deals
    blockers: List[str] = [
        "Security concerns",
        "Budget freeze",
        "Champion leaves",
        "Competitor undercut"
    ]


class BehavioralProfile(BaseModel):
    """Statistical distribution of behavioral traits in a segment"""
    
    # Firmographics
    company_size_range: tuple[int, int] = (100, 1000)
    budget_range: tuple[int, int] = (10000, 100000)
    
    # Behavioral distributions (mean, std)
    risk_tolerance: tuple[float, float] = (0.5, 0.15)
    price_sensitivity: tuple[float, float] = (0.5, 0.15)
    decision_speed: tuple[float, float] = (0.5, 0.15)
    
    # Social
    influencer_susceptibility: float = 0.5
    network_density: float = 0.05  # % of segment connected


class Segment(BaseModel):
    """A market segment with its decision physics"""
    id: str
    name: str
    size_pct: float = Field(ge=0, le=1)  # % of TAM
    
    decision_framework: DecisionFramework
    behavioral_profile: BehavioralProfile


class Competitor(BaseModel):
    """A competitor in the market"""
    id: str
    name: str
    market_share: float = Field(ge=0, le=1)
    
    # Product attributes
    price_point: float = 1.0  # relative to market avg
    features: Dict[str, float]  # feature -> strength (0-1)
    brand_awareness: float = Field(ge=0, le=1)
    
    # Competitive behavior
    aggression: float = Field(ge=0, le=1, default=0.5)
    response_speed: float = Field(ge=0, le=1, default=0.5)


class Product(BaseModel):
    """Your product"""
    id: str
    name: str
    price_point: float = 1.0
    features: Dict[str, float]
    brand_awareness: float = Field(ge=0, le=1, default=0.1)


class Scenario(BaseModel):
    """
    Complete market scenario.
    This is what would come from the Data Foundation + Ontology layers.
    """
    id: str
    name: str
    description: str
    market_type: MarketType
    
    # Market structure
    total_addressable_market: int
    segments: List[Segment]
    
    # Competition
    competitors: List[Competitor]
    your_product: Product
    
    # Simulation parameters
    simulation_days: int = 90
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "saas_launch_2024",
                "name": "B2B SaaS Product Launch",
                "market_type": "b2b_saas",
                "total_addressable_market": 50000
            }
        }
```

Create `backend/models/agent.py`:

```python
"""
Agent models - synthetic decision-makers.
This is the Behavioral Model (Layer 3).
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class Persona(BaseModel):
    """Rich persona generated by LLM for deep-dive interactions"""
    name: str
    role: str
    company_name: str
    company_description: str
    background: str
    current_challenges: List[str]
    buying_history: List[str]
    communication_style: str


class Belief(BaseModel):
    """Agent's belief about a product"""
    product_id: str
    perceived_quality: Dict[str, float]  # feature -> perceived score
    trust_level: float = Field(ge=0, le=1)
    source: str  # "advertising", "peer", "demo", "trial"
    confidence: float = Field(ge=0, le=1)


class DecisionEvent(BaseModel):
    """A logged event in the agent's decision journey"""
    day: int
    event_type: str  # "awareness", "stage_change", "touchpoint", "decision"
    description: str
    inputs: Dict
    output: str
    reasoning: Optional[str] = None  # LLM-generated on demand


class Agent(BaseModel):
    """
    A synthetic decision-maker.
    Core behavioral model that makes decisions during simulation.
    """
    id: str
    segment_id: str
    
    # Identity (optional, for deep-dive)
    persona: Optional[Persona] = None
    
    # Firmographics
    company_size: int = 100
    budget: int = 50000
    
    # Behavioral parameters (sampled from segment profile)
    risk_tolerance: float = Field(ge=0, le=1)
    price_sensitivity: float = Field(ge=0, le=1)
    feature_priorities: Dict[str, float]
    decision_speed: float = Field(ge=0, le=1)
    influencer_susceptibility: float = Field(ge=0, le=1)
    
    # Current state
    stage: str = "Unaware"
    awareness: Dict[str, float] = {}  # product_id -> awareness level
    consideration_set: List[str] = []
    beliefs: Dict[str, Belief] = {}
    
    # Social graph
    connections: List[str] = []  # other agent IDs
    influence_score: float = 0.5
    
    # Decision trace (for explainability)
    decision_log: List[DecisionEvent] = []
    
    # Final decision
    final_decision: Optional[str] = None  # product_id or None
    decision_day: Optional[int] = None
    
    def add_event(self, day: int, event_type: str, description: str, 
                  inputs: Dict, output: str):
        """Add event to decision log"""
        self.decision_log.append(DecisionEvent(
            day=day,
            event_type=event_type,
            description=description,
            inputs=inputs,
            output=output
        ))
```

Create `backend/models/strategy.py`:

```python
"""
Strategy models - the intervention being tested.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class Messaging(BaseModel):
    """Positioning and messaging strategy"""
    value_proposition: str
    primary_claim: str
    feature_emphasis: Dict[str, float]  # feature -> emphasis weight
    tone: str = "enterprise"  # "enterprise", "innovative", "value", "technical"
    
    # Full pitch for LLM reasoning
    full_pitch: Optional[str] = None


class DiscountStrategy(BaseModel):
    """Discounting approach"""
    available: bool = False
    max_discount_pct: float = 0.0
    triggers: List[str] = []  # conditions to offer discount


class Pricing(BaseModel):
    """Pricing strategy"""
    base_price: float = 1.0  # relative to market
    model: str = "per_seat"  # "per_seat", "flat", "usage", "tiered"
    discount: Optional[DiscountStrategy] = None


class CompetitiveResponse(BaseModel):
    """How to respond if competitor acts"""
    trigger_conditions: List[str]
    response_actions: List[str]


class GoToMarket(BaseModel):
    """Go-to-market strategy"""
    
    # Channel allocation (should sum to ~1.0)
    channels: Dict[str, float] = {
        "paid_digital": 0.3,
        "content": 0.25,
        "events": 0.1,
        "outbound": 0.25,
        "partnerships": 0.1
    }
    
    intensity: float = Field(ge=0, le=1, default=0.5)
    target_segments: List[str] = []  # segment IDs to prioritize
    
    competitive_response: Optional[CompetitiveResponse] = None


class Strategy(BaseModel):
    """
    Complete strategy to test.
    This is the intervention injected into the simulation.
    """
    id: str
    name: str
    description: str
    
    messaging: Messaging
    pricing: Pricing
    gtm: GoToMarket
    
    launch_day: int = 0
```

Create `backend/models/results.py`:

```python
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
```

---

# PART 3: SIMULATION ENGINE

## 3.1 Agent Factory

Create `backend/engine/__init__.py`:
```python
from .agent_factory import AgentFactory
from .decision_engine import DecisionEngine
from .market_dynamics import MarketDynamics
from .runner import SimulationRunner
```

Create `backend/engine/agent_factory.py`:

```python
"""
Agent Factory - creates synthetic decision-makers.
Uses optional LLM for rich persona generation.
"""

import random
import numpy as np
from typing import List, Optional
import anthropic
import json

from backend.models import Agent, Segment, Persona, Belief


class AgentFactory:
    """Creates agents with behavioral parameters sampled from segment profiles"""
    
    def __init__(self, use_llm: bool = False, llm_sample_size: int = 50):
        """
        Args:
            use_llm: Whether to generate LLM personas
            llm_sample_size: How many agents per segment get LLM personas
        """
        self.use_llm = use_llm
        self.llm_sample_size = llm_sample_size
        
        if use_llm:
            self.client = anthropic.Anthropic()
    
    def create_population(
        self, 
        segments: List[Segment], 
        total_agents: int
    ) -> List[Agent]:
        """Create full agent population across all segments"""
        
        agents = []
        
        for segment in segments:
            segment_count = int(total_agents * segment.size_pct)
            segment_agents = self._create_segment_agents(segment, segment_count)
            agents.extend(segment_agents)
        
        # Create social network
        agents = self._create_network(agents)
        
        return agents
    
    def _create_segment_agents(
        self, 
        segment: Segment, 
        count: int
    ) -> List[Agent]:
        """Create agents for a specific segment"""
        
        agents = []
        profile = segment.behavioral_profile
        
        for i in range(count):
            agent = Agent(
                id=f"{segment.id}_{i}",
                segment_id=segment.id,
                
                # Sample firmographics
                company_size=random.randint(*profile.company_size_range),
                budget=random.randint(*profile.budget_range),
                
                # Sample behavioral parameters
                risk_tolerance=self._sample_bounded(*profile.risk_tolerance),
                price_sensitivity=self._sample_bounded(*profile.price_sensitivity),
                decision_speed=self._sample_bounded(*profile.decision_speed),
                influencer_susceptibility=profile.influencer_susceptibility,
                
                # Sample feature priorities from stakeholders
                feature_priorities=self._sample_priorities(segment),
                
                # Initialize state
                stage="Unaware",
                awareness={},
                consideration_set=[],
                beliefs={},
                connections=[],
                influence_score=random.random(),
                decision_log=[]
            )
            
            # Generate LLM persona for sample
            if self.use_llm and i < self.llm_sample_size:
                agent.persona = self._generate_persona(segment, agent)
            
            agents.append(agent)
        
        return agents
    
    def _sample_bounded(self, mean: float, std: float) -> float:
        """Sample from normal distribution, bounded [0, 1]"""
        value = random.gauss(mean, std)
        return max(0.0, min(1.0, value))
    
    def _sample_priorities(self, segment: Segment) -> dict[str, float]:
        """Sample feature priorities with noise from segment's stakeholder mix"""
        
        # Weighted average of stakeholder priorities
        priorities = {}
        total_weight = sum(s.influence_weight for s in segment.decision_framework.stakeholders)
        
        for stakeholder in segment.decision_framework.stakeholders:
            weight = stakeholder.influence_weight / total_weight
            for feature, importance in stakeholder.priorities.items():
                if feature not in priorities:
                    priorities[feature] = 0
                priorities[feature] += importance * weight
        
        # Add noise
        return {
            k: max(0, min(1, v + random.gauss(0, 0.1)))
            for k, v in priorities.items()
        }
    
    def _create_network(self, agents: List[Agent]) -> List[Agent]:
        """Create social network using preferential attachment"""
        
        # Group by segment
        by_segment = {}
        for agent in agents:
            if agent.segment_id not in by_segment:
                by_segment[agent.segment_id] = []
            by_segment[agent.segment_id].append(agent)
        
        # Connect within segments (preferential attachment)
        for segment_id, segment_agents in by_segment.items():
            n = len(segment_agents)
            if n < 5:
                continue
            
            for i, agent in enumerate(segment_agents):
                if i < 3:
                    continue
                
                # Number of connections based on network density
                num_connections = min(random.randint(2, 5), i)
                
                # Weight by influence score (preferential attachment)
                candidates = segment_agents[:i]
                weights = np.array([a.influence_score for a in candidates])
                weights = weights / weights.sum()
                
                # Sample connections
                indices = np.random.choice(
                    len(candidates),
                    size=num_connections,
                    replace=False,
                    p=weights
                )
                
                agent.connections = [candidates[j].id for j in indices]
        
        return agents
    
    def _generate_persona(self, segment: Segment, agent: Agent) -> Persona:
        """Use Claude to generate a rich persona"""
        
        prompt = f"""Generate a realistic B2B buyer persona.

SEGMENT: {segment.name}
DECISION FRAMEWORK:
- Average sales cycle: {segment.decision_framework.avg_cycle_days} days
- Key stakeholders: {[s.role for s in segment.decision_framework.stakeholders]}
- Common blockers: {segment.decision_framework.blockers}

AGENT BEHAVIORAL PROFILE:
- Company size: {agent.company_size} employees
- Budget: ${agent.budget:,}
- Risk tolerance: {agent.risk_tolerance:.2f} (0=very cautious, 1=risk-seeking)
- Price sensitivity: {agent.price_sensitivity:.2f} (0=budget doesn't matter, 1=very cost-conscious)
- Decision speed: {agent.decision_speed:.2f} (0=very deliberate, 1=quick decision maker)
- Feature priorities: {agent.feature_priorities}

Generate a persona with:
1. A realistic name
2. Job title that matches the segment
3. Company name and brief description
4. 2-sentence professional background
5. Top 3 current business challenges
6. 2-3 past software purchasing experiences
7. Their communication/buying style preference

Return ONLY valid JSON:
{{
    "name": "string",
    "role": "string",
    "company_name": "string",
    "company_description": "string",
    "background": "string",
    "current_challenges": ["string", "string", "string"],
    "buying_history": ["string", "string"],
    "communication_style": "string"
}}"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse JSON from response
            text = response.content[0].text
            # Handle potential markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            data = json.loads(text.strip())
            return Persona(**data)
            
        except Exception as e:
            # Fallback persona
            return Persona(
                name=f"Contact {agent.id}",
                role="Decision Maker",
                company_name=f"Company {agent.company_size}",
                company_description=f"A {agent.company_size}-person company",
                background="Experienced professional in the industry.",
                current_challenges=["Efficiency", "Growth", "Competition"],
                buying_history=["Previous software purchase"],
                communication_style="Professional and direct"
            )
```

## 3.2 Decision Engine

Create `backend/engine/decision_engine.py`:

```python
"""
Decision Engine - how agents make purchase decisions.
Hybrid approach: fast math for simulation, LLM for explanations.
"""

import random
from typing import List, Dict, Optional, Tuple
import anthropic

from backend.models import Agent, Product, Competitor, Strategy, DecisionEvent


class DecisionEngine:
    """
    Processes agent decisions each simulation step.
    
    The decision model:
    1. Awareness updates from market signals
    2. Stage progression based on awareness thresholds
    3. Product scoring based on fit
    4. Final decision with threshold
    """
    
    def __init__(
        self, 
        awareness_threshold: float = 0.25,
        consideration_threshold: float = 0.50,
        evaluation_threshold: float = 0.70,
        purchase_threshold: float = 0.55
    ):
        self.awareness_threshold = awareness_threshold
        self.consideration_threshold = consideration_threshold
        self.evaluation_threshold = evaluation_threshold
        self.purchase_threshold = purchase_threshold
        
        self.client = anthropic.Anthropic()
    
    def process_agent_day(
        self,
        agent: Agent,
        day: int,
        your_product: Product,
        competitors: List[Competitor],
        market_signals: Dict[str, float],
        strategy: Strategy
    ) -> Agent:
        """Process one day for one agent"""
        
        if agent.stage == "Decided":
            return agent
        
        # 1. Update awareness from signals
        agent = self._update_awareness(agent, market_signals, day)
        
        # 2. Progress through stages
        agent = self._update_stage(agent, your_product, competitors, day)
        
        # 3. If evaluating, maybe make decision
        if agent.stage == "Evaluating":
            agent = self._maybe_decide(
                agent, day, your_product, competitors, strategy
            )
        
        return agent
    
    def _update_awareness(
        self,
        agent: Agent,
        signals: Dict[str, float],
        day: int
    ) -> Agent:
        """Update product awareness based on market signals"""
        
        for product_id, signal_strength in signals.items():
            current = agent.awareness.get(product_id, 0.0)
            
            # Base impact from signal
            base_impact = signal_strength * 0.12
            
            # Modify by agent's susceptibility
            susceptibility_mod = 0.6 + agent.influencer_susceptibility * 0.4
            impact = base_impact * susceptibility_mod
            
            # Diminishing returns at high awareness
            impact *= (1 - current) ** 0.7
            
            new_awareness = min(1.0, current + impact)
            
            # Log significant changes
            if new_awareness - current > 0.05:
                agent.add_event(
                    day=day,
                    event_type="awareness",
                    description=f"Awareness of {product_id} increased",
                    inputs={"signal": signal_strength, "previous": round(current, 3)},
                    output=f"{new_awareness:.3f}"
                )
            
            agent.awareness[product_id] = new_awareness
        
        return agent
    
    def _update_stage(
        self,
        agent: Agent,
        your_product: Product,
        competitors: List[Competitor],
        day: int
    ) -> Agent:
        """Progress agent through funnel stages"""
        
        max_awareness = max(agent.awareness.values()) if agent.awareness else 0
        old_stage = agent.stage
        
        if agent.stage == "Unaware":
            if max_awareness >= self.awareness_threshold:
                agent.stage = "Aware"
                
        elif agent.stage == "Aware":
            if max_awareness >= self.consideration_threshold:
                agent.stage = "Considering"
                # Build consideration set
                all_products = [your_product.id] + [c.id for c in competitors]
                for pid in all_products:
                    awareness = agent.awareness.get(pid, 0)
                    if awareness >= self.awareness_threshold:
                        if pid not in agent.consideration_set:
                            agent.consideration_set.append(pid)
                            
        elif agent.stage == "Considering":
            if max_awareness >= self.evaluation_threshold:
                agent.stage = "Evaluating"
        
        # Log stage changes
        if agent.stage != old_stage:
            agent.add_event(
                day=day,
                event_type="stage_change",
                description=f"Progressed from {old_stage} to {agent.stage}",
                inputs={"max_awareness": round(max_awareness, 3)},
                output=agent.stage
            )
        
        return agent
    
    def _maybe_decide(
        self,
        agent: Agent,
        day: int,
        your_product: Product,
        competitors: List[Competitor],
        strategy: Strategy
    ) -> Agent:
        """Evaluate products and potentially make a decision"""
        
        # Decision probability based on speed + time in stage
        base_prob = agent.decision_speed * 0.06
        time_pressure = min(0.04, day * 0.0005)  # Increases over time
        decision_prob = base_prob + time_pressure
        
        if random.random() > decision_prob:
            return agent
        
        # Score each product in consideration set
        all_products = {your_product.id: your_product}
        for c in competitors:
            all_products[c.id] = c
        
        scores = {}
        for pid in agent.consideration_set:
            if pid in all_products:
                product = all_products[pid]
                scores[pid] = self._score_product(agent, product, strategy)
        
        if not scores:
            agent.stage = "Decided"
            agent.final_decision = None
            agent.decision_day = day
            agent.add_event(
                day=day,
                event_type="decision",
                description="No products in consideration - no purchase",
                inputs={},
                output="no_purchase"
            )
            return agent
        
        # Find best option
        best_id = max(scores, key=scores.get)
        best_score = scores[best_id]
        
        # Apply purchase threshold
        if best_score >= self.purchase_threshold:
            agent.final_decision = best_id
            agent.add_event(
                day=day,
                event_type="decision",
                description=f"Selected {best_id}",
                inputs={"scores": {k: round(v, 3) for k, v in scores.items()}},
                output=best_id
            )
        else:
            agent.final_decision = None
            agent.add_event(
                day=day,
                event_type="decision",
                description="No product met requirements",
                inputs={"scores": {k: round(v, 3) for k, v in scores.items()}},
                output="no_purchase"
            )
        
        agent.stage = "Decided"
        agent.decision_day = day
        
        return agent
    
    def _score_product(
        self,
        agent: Agent,
        product,  # Product or Competitor
        strategy: Strategy
    ) -> float:
        """
        Calculate fit score between agent and product.
        
        Score components:
        - Feature fit (40%): How well features match priorities
        - Price fit (30%): Price vs. price sensitivity
        - Brand fit (20%): Brand awareness vs. risk tolerance
        - Awareness (10%): Familiarity bonus
        """
        
        score = 0.0
        
        # Feature fit (40%)
        feature_score = 0.0
        total_weight = sum(agent.feature_priorities.values()) or 1
        
        for feature, importance in agent.feature_priorities.items():
            product_strength = product.features.get(feature, 0.5)
            feature_score += importance * product_strength
        
        feature_score /= total_weight
        score += feature_score * 0.40
        
        # Price fit (30%)
        # Price sensitivity affects how much price matters
        # Lower price = better fit for price-sensitive buyers
        price_penalty = agent.price_sensitivity * (product.price_point - 0.7)
        price_fit = 1.0 - max(0, min(0.5, price_penalty))
        score += price_fit * 0.30
        
        # Brand/risk fit (20%)
        # Risk-averse buyers prefer high brand awareness
        # Risk-tolerant buyers are ok with unknowns
        brand_fit = (
            product.brand_awareness * (1 - agent.risk_tolerance) +
            agent.risk_tolerance * 0.6  # Risk tolerant = ok with unknown
        )
        score += brand_fit * 0.20
        
        # Awareness bonus (10%)
        awareness = agent.awareness.get(product.id, 0)
        score += awareness * 0.10
        
        return score
    
    def explain_decision(self, agent: Agent) -> str:
        """Generate natural language explanation of agent's decision"""
        
        # Build context from decision log
        journey = "\n".join([
            f"Day {e.day}: {e.description} (inputs: {e.inputs}, output: {e.output})"
            for e in agent.decision_log[-10:]  # Last 10 events
        ])
        
        persona_context = ""
        if agent.persona:
            persona_context = f"""
PERSONA:
- Name: {agent.persona.name}
- Role: {agent.persona.role}
- Company: {agent.persona.company_description}
- Challenges: {', '.join(agent.persona.current_challenges)}
- Buying style: {agent.persona.communication_style}
"""
        
        prompt = f"""Explain this B2B buyer's decision journey in 3-4 sentences.

{persona_context}
BEHAVIORAL PROFILE:
- Risk tolerance: {agent.risk_tolerance:.2f} (0=very cautious, 1=risk-seeking)
- Price sensitivity: {agent.price_sensitivity:.2f} (0=budget flexible, 1=cost-conscious)
- Decision speed: {agent.decision_speed:.2f} (0=deliberate, 1=fast)
- Feature priorities: {agent.feature_priorities}

DECISION JOURNEY:
{journey}

FINAL DECISION: {agent.final_decision or 'No purchase'}

Write a clear explanation of WHY they made this decision, referencing their 
specific characteristics. Be specific, not generic. Explain the key factors."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
```

## 3.3 Market Dynamics

Create `backend/engine/market_dynamics.py`:

```python
"""
Market Dynamics - external forces affecting agents.
Handles GTM activities, competitive response, network effects.
"""

import random
from typing import List, Dict
from backend.models import Scenario, Strategy, Agent, Competitor


class MarketDynamics:
    """
    Manages market-level effects each simulation day.
    """
    
    def __init__(self, scenario: Scenario, strategy: Strategy):
        self.scenario = scenario
        self.strategy = strategy
        
        # Track competitive responses
        self.competitor_responses: Dict[str, int] = {}  # competitor_id -> response_day
        
        # Track key events
        self.events_triggered: List[str] = []
    
    def get_signals(
        self,
        day: int,
        agents: List[Agent]
    ) -> Dict[str, float]:
        """
        Calculate market signals for all products on a given day.
        Returns product_id -> signal_strength mapping.
        """
        
        signals = {}
        
        # Your product signal from GTM
        signals[self.scenario.your_product.id] = self._calculate_gtm_signal(day)
        
        # Competitor signals
        for competitor in self.scenario.competitors:
            signals[competitor.id] = self._calculate_competitor_signal(
                competitor, day
            )
        
        # Network effects (word of mouth)
        network_boost = self._calculate_network_effects(agents)
        for product_id, boost in network_boost.items():
            signals[product_id] = signals.get(product_id, 0) + boost
        
        return signals
    
    def _calculate_gtm_signal(self, day: int) -> float:
        """Calculate signal strength from your GTM activities"""
        
        # Not active before launch
        if day < self.strategy.launch_day:
            return 0.0
        
        days_since_launch = day - self.strategy.launch_day
        
        # Base signal from intensity
        base = self.strategy.gtm.intensity
        
        # Channel effectiveness curve
        # Ramp up over first 2 weeks, sustain, then gradual decay
        if days_since_launch < 14:
            time_factor = 0.5 + (days_since_launch / 14) * 0.5
        elif days_since_launch < 60:
            time_factor = 1.0
        else:
            time_factor = max(0.4, 1.0 - (days_since_launch - 60) * 0.008)
        
        # Channel mix effect (more channels = better coverage)
        active_channels = sum(1 for v in self.strategy.gtm.channels.values() if v > 0.1)
        channel_bonus = 1.0 + (active_channels - 3) * 0.05
        
        return base * time_factor * channel_bonus
    
    def _calculate_competitor_signal(
        self,
        competitor: Competitor,
        day: int
    ) -> float:
        """Calculate competitor's market signal"""
        
        # Base signal from existing presence
        base = competitor.market_share * competitor.brand_awareness * 0.4
        
        # Check for competitive response
        if competitor.id not in self.competitor_responses:
            if self._should_respond(competitor, day):
                self.competitor_responses[competitor.id] = day
                self.events_triggered.append(
                    f"Day {day}: {competitor.name} launched competitive response"
                )
        
        # Response boost
        if competitor.id in self.competitor_responses:
            response_day = self.competitor_responses[competitor.id]
            days_responding = day - response_day
            
            if 0 <= days_responding < 30:
                # Strong response for first 30 days
                response_boost = competitor.aggression * 0.4
                base += response_boost
        
        return base
    
    def _should_respond(self, competitor: Competitor, day: int) -> bool:
        """Determine if competitor triggers a response"""
        
        # Only respond after your launch + some delay
        min_response_day = self.strategy.launch_day + 14
        if day < min_response_day:
            return False
        
        # Daily probability based on aggression
        daily_prob = competitor.aggression * 0.04
        
        # Higher probability if you're doing well
        if self.strategy.gtm.intensity > 0.7:
            daily_prob *= 1.3
        
        return random.random() < daily_prob
    
    def _calculate_network_effects(
        self,
        agents: List[Agent]
    ) -> Dict[str, float]:
        """Word of mouth from decided agents"""
        
        boost = {}
        
        decided_agents = [
            a for a in agents 
            if a.stage == "Decided" and a.final_decision
        ]
        
        # Count influence by product
        for agent in decided_agents:
            product_id = agent.final_decision
            # Agent's influence spreads to their network
            spread = agent.influence_score * 0.008 * len(agent.connections)
            boost[product_id] = boost.get(product_id, 0) + spread
        
        return boost
```

## 3.4 Simulation Runner

Create `backend/engine/runner.py`:

```python
"""
Simulation Runner - Monte Carlo execution across branches.
"""

import random
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import copy

from backend.models import (
    Scenario, Strategy, Agent, 
    SimulationResults, BranchResult, DailySnapshot,
    SegmentAnalysis, DriverAnalysis
)
from backend.engine.agent_factory import AgentFactory
from backend.engine.decision_engine import DecisionEngine
from backend.engine.market_dynamics import MarketDynamics


class SimulationRunner:
    """
    Runs parallel Monte Carlo simulation branches.
    """
    
    def __init__(
        self,
        scenario: Scenario,
        strategy: Strategy,
        num_agents: int = 10000,
        num_branches: int = 500,
        use_llm_personas: bool = False,
        parallel: bool = True
    ):
        self.scenario = scenario
        self.strategy = strategy
        self.num_agents = num_agents
        self.num_branches = num_branches
        self.use_llm_personas = use_llm_personas
        self.parallel = parallel
    
    def run(self) -> SimulationResults:
        """Execute full simulation and return aggregated results"""
        
        started_at = datetime.now()
        
        # Run branches
        if self.parallel and self.num_branches > 10:
            branch_results = self._run_parallel()
        else:
            branch_results = self._run_sequential()
        
        # Aggregate results
        results = self._aggregate_results(branch_results, started_at)
        
        return results
    
    def _run_parallel(self) -> List[BranchResult]:
        """Run branches in parallel using ProcessPoolExecutor"""
        
        results = []
        
        # Note: For multiprocessing, we pass serializable data
        # and reconstruct objects in worker
        scenario_dict = self.scenario.model_dump()
        strategy_dict = self.strategy.model_dump()
        
        with ProcessPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(
                    _run_branch_worker,
                    seed,
                    scenario_dict,
                    strategy_dict,
                    self.num_agents,
                    self.use_llm_personas
                ): seed
                for seed in range(self.num_branches)
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Branch failed: {e}")
        
        return results
    
    def _run_sequential(self) -> List[BranchResult]:
        """Run branches sequentially (for debugging)"""
        
        results = []
        for seed in range(self.num_branches):
            result = self._run_single_branch(seed)
            results.append(result)
        return results
    
    def _run_single_branch(self, seed: int) -> BranchResult:
        """Run a single simulation branch"""
        
        # Set random seeds for reproducibility
        random.seed(seed)
        np.random.seed(seed)
        
        # Create agents
        factory = AgentFactory(
            use_llm=self.use_llm_personas and seed == 0,  # LLM only for first branch
            llm_sample_size=20 if self.use_llm_personas else 0
        )
        agents = factory.create_population(
            self.scenario.segments,
            self.num_agents
        )
        
        # Create index for fast lookup
        agent_index = {a.id: i for i, a in enumerate(agents)}
        
        # Initialize dynamics
        market = MarketDynamics(self.scenario, self.strategy)
        engine = DecisionEngine()
        
        # Run simulation
        timeline = []
        
        for day in range(self.scenario.simulation_days):
            # Get market signals
            signals = market.get_signals(day, agents)
            
            # Process each agent
            for i, agent in enumerate(agents):
                if agent.stage != "Decided":
                    agents[i] = engine.process_agent_day(
                        agent,
                        day,
                        self.scenario.your_product,
                        self.scenario.competitors,
                        signals,
                        self.strategy
                    )
            
            # Record snapshot
            timeline.append(self._create_snapshot(agents, day, market))
        
        # Calculate final metrics
        return self._create_branch_result(
            seed, agents, timeline, market
        )
    
    def _create_snapshot(
        self,
        agents: List[Agent],
        day: int,
        market: MarketDynamics
    ) -> DailySnapshot:
        """Create daily snapshot of simulation state"""
        
        your_product_id = self.scenario.your_product.id
        competitor_ids = [c.id for c in self.scenario.competitors]
        
        # Count by stage
        stages = {"Unaware": 0, "Aware": 0, "Considering": 0, "Evaluating": 0, "Decided": 0}
        converted = 0
        competitor_converted = 0
        no_purchase = 0
        total_awareness = 0
        
        for agent in agents:
            stages[agent.stage] += 1
            total_awareness += agent.awareness.get(your_product_id, 0)
            
            if agent.stage == "Decided":
                if agent.final_decision == your_product_id:
                    converted += 1
                elif agent.final_decision in competitor_ids:
                    competitor_converted += 1
                else:
                    no_purchase += 1
        
        return DailySnapshot(
            day=day,
            unaware_count=stages["Unaware"],
            aware_count=stages["Aware"],
            considering_count=stages["Considering"],
            evaluating_count=stages["Evaluating"],
            decided_count=stages["Decided"],
            converted_count=converted,
            competitor_count=competitor_converted,
            no_purchase_count=no_purchase,
            avg_awareness=total_awareness / len(agents) if agents else 0,
            events=list(market.events_triggered)
        )
    
    def _create_branch_result(
        self,
        seed: int,
        agents: List[Agent],
        timeline: List[DailySnapshot],
        market: MarketDynamics
    ) -> BranchResult:
        """Create result object for a branch"""
        
        your_product_id = self.scenario.your_product.id
        
        # Count conversions
        converted = [a for a in agents if a.final_decision == your_product_id]
        decided = [a for a in agents if a.stage == "Decided"]
        
        conversion_rate = len(converted) / len(agents) if agents else 0
        
        # Awareness
        avg_awareness = np.mean([
            a.awareness.get(your_product_id, 0) for a in agents
        ])
        
        # Average decision day for those who decided
        decision_days = [a.decision_day for a in decided if a.decision_day]
        avg_decision_day = np.mean(decision_days) if decision_days else 0
        
        # By segment
        segment_conversions = {}
        for segment in self.scenario.segments:
            segment_agents = [a for a in agents if a.segment_id == segment.id]
            segment_converted = [a for a in segment_agents if a.final_decision == your_product_id]
            if segment_agents:
                segment_conversions[segment.id] = len(segment_converted) / len(segment_agents)
        
        return BranchResult(
            branch_id=seed,
            seed=seed,
            conversion_rate=conversion_rate,
            final_awareness=avg_awareness,
            avg_decision_day=avg_decision_day,
            segment_conversions=segment_conversions,
            timeline=timeline,
            competitor_responded=bool(market.competitor_responses),
            key_events=market.events_triggered
        )
    
    def _aggregate_results(
        self,
        branches: List[BranchResult],
        started_at: datetime
    ) -> SimulationResults:
        """Aggregate branch results into summary statistics"""
        
        conversions = [b.conversion_rate for b in branches]
        
        # Basic stats
        mean = np.mean(conversions)
        median = np.median(conversions)
        std = np.std(conversions)
        
        # Percentiles
        p5 = np.percentile(conversions, 5)
        p25 = np.percentile(conversions, 25)
        p75 = np.percentile(conversions, 75)
        p95 = np.percentile(conversions, 95)
        
        # Segment analysis
        segment_analysis = []
        for segment in self.scenario.segments:
            seg_conversions = [
                b.segment_conversions.get(segment.id, 0) for b in branches
            ]
            segment_analysis.append(SegmentAnalysis(
                segment_id=segment.id,
                segment_name=segment.name,
                conversion_rate=np.mean(seg_conversions),
                conversion_std=np.std(seg_conversions),
                avg_decision_day=0,  # TODO: calculate
                top_conversion_drivers=[],
                top_blockers=[]
            ))
        
        # Identify failure/success branches
        failure_threshold = np.percentile(conversions, 10)
        success_threshold = np.percentile(conversions, 90)
        
        failure_branches = [b.branch_id for b in branches if b.conversion_rate <= failure_threshold]
        success_branches = [b.branch_id for b in branches if b.conversion_rate >= success_threshold]
        
        # Analyze drivers
        top_drivers = self._analyze_drivers(branches, success_branches)
        top_blockers = self._analyze_blockers(branches, failure_branches)
        
        return SimulationResults(
            id=f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            scenario_id=self.scenario.id,
            strategy_id=self.strategy.id,
            num_agents=self.num_agents,
            num_branches=self.num_branches,
            started_at=started_at,
            completed_at=datetime.now(),
            mean_conversion=mean,
            median_conversion=median,
            std_conversion=std,
            p5=p5,
            p25=p25,
            p75=p75,
            p95=p95,
            segment_analysis=segment_analysis,
            top_drivers=top_drivers,
            top_blockers=top_blockers,
            branches=branches,
            failure_branches=failure_branches,
            success_branches=success_branches
        )
    
    def _analyze_drivers(
        self,
        branches: List[BranchResult],
        success_ids: List[int]
    ) -> List[DriverAnalysis]:
        """Analyze what drove success in top branches"""
        
        drivers = []
        
        # Check competitive response correlation
        success_branches = [b for b in branches if b.branch_id in success_ids]
        all_no_response = sum(1 for b in branches if not b.competitor_responded)
        success_no_response = sum(1 for b in success_branches if not b.competitor_responded)
        
        if all_no_response > 0:
            no_response_rate = success_no_response / len(success_branches) if success_branches else 0
            baseline_rate = all_no_response / len(branches) if branches else 0
            
            if no_response_rate > baseline_rate + 0.1:
                drivers.append(DriverAnalysis(
                    factor="No competitive response",
                    impact=no_response_rate - baseline_rate,
                    description="Success branches more likely when competitors didn't respond"
                ))
        
        # Segment performance
        for segment in self.scenario.segments:
            success_seg_conv = np.mean([
                b.segment_conversions.get(segment.id, 0) for b in success_branches
            ]) if success_branches else 0
            
            all_seg_conv = np.mean([
                b.segment_conversions.get(segment.id, 0) for b in branches
            ])
            
            if success_seg_conv > all_seg_conv + 0.02:
                drivers.append(DriverAnalysis(
                    factor=f"{segment.name} segment conversion",
                    impact=success_seg_conv - all_seg_conv,
                    description=f"Strong {segment.name} performance drove success"
                ))
        
        return sorted(drivers, key=lambda d: -d.impact)[:5]
    
    def _analyze_blockers(
        self,
        branches: List[BranchResult],
        failure_ids: List[int]
    ) -> List[DriverAnalysis]:
        """Analyze what blocked success in bottom branches"""
        
        blockers = []
        
        failure_branches = [b for b in branches if b.branch_id in failure_ids]
        
        # Competitive response correlation
        all_responded = sum(1 for b in branches if b.competitor_responded)
        failure_responded = sum(1 for b in failure_branches if b.competitor_responded)
        
        if failure_branches:
            failure_response_rate = failure_responded / len(failure_branches)
            baseline_rate = all_responded / len(branches) if branches else 0
            
            if failure_response_rate > baseline_rate + 0.1:
                blockers.append(DriverAnalysis(
                    factor="Competitive response",
                    impact=-(failure_response_rate - baseline_rate),
                    description="Failure branches more likely when competitors responded aggressively"
                ))
        
        return sorted(blockers, key=lambda d: d.impact)[:5]


# Worker function for multiprocessing
def _run_branch_worker(
    seed: int,
    scenario_dict: dict,
    strategy_dict: dict,
    num_agents: int,
    use_llm_personas: bool
) -> BranchResult:
    """Standalone worker function for parallel execution"""
    
    from backend.models import Scenario, Strategy
    
    scenario = Scenario(**scenario_dict)
    strategy = Strategy(**strategy_dict)
    
    runner = SimulationRunner(
        scenario=scenario,
        strategy=strategy,
        num_agents=num_agents,
        num_branches=1,
        use_llm_personas=use_llm_personas,
        parallel=False
    )
    
    return runner._run_single_branch(seed)
```

---

# PART 4: DEMO SCENARIO DATA

Create `backend/data/presets/b2b_saas.py`:

```python
"""
Pre-built B2B SaaS Launch scenario for demos.
"""

from backend.models import (
    Scenario, Segment, DecisionFramework, BehavioralProfile,
    Stakeholder, Competitor, Product, Strategy,
    Messaging, Pricing, GoToMarket, DiscountStrategy
)


def get_saas_launch_scenario() -> Scenario:
    """Create the demo B2B SaaS launch scenario"""
    
    return Scenario(
        id="saas_launch_2024",
        name="B2B SaaS Product Launch",
        description="Launch a project management tool into a competitive market",
        market_type="b2b_saas",
        total_addressable_market=50000,
        
        segments=[
            # Enterprise segment (15%)
            Segment(
                id="enterprise",
                name="Enterprise",
                size_pct=0.15,
                decision_framework=DecisionFramework(
                    stages=["Unaware", "Aware", "Considering", "Evaluating", "Decided"],
                    avg_cycle_days=90,
                    stakeholders=[
                        Stakeholder(
                            role="IT Director",
                            influence_weight=0.35,
                            priorities={
                                "security": 0.9,
                                "integrations": 0.8,
                                "scalability": 0.85,
                                "compliance": 0.9,
                                "ease_of_use": 0.5
                            },
                            risk_tolerance=0.2
                        ),
                        Stakeholder(
                            role="CFO/Finance",
                            influence_weight=0.25,
                            priorities={
                                "security": 0.7,
                                "integrations": 0.6,
                                "scalability": 0.7,
                                "compliance": 0.8,
                                "ease_of_use": 0.4
                            },
                            risk_tolerance=0.15
                        ),
                        Stakeholder(
                            role="End Users",
                            influence_weight=0.2,
                            priorities={
                                "security": 0.4,
                                "integrations": 0.7,
                                "scalability": 0.5,
                                "compliance": 0.3,
                                "ease_of_use": 0.95
                            },
                            risk_tolerance=0.5
                        ),
                        Stakeholder(
                            role="Procurement",
                            influence_weight=0.2,
                            priorities={
                                "security": 0.6,
                                "integrations": 0.5,
                                "scalability": 0.5,
                                "compliance": 0.85,
                                "ease_of_use": 0.3
                            },
                            risk_tolerance=0.1
                        )
                    ],
                    triggers={
                        "Unaware->Aware": "Industry event, peer reference, or analyst report",
                        "Aware->Considering": "Active pain point, budget cycle alignment",
                        "Considering->Evaluating": "Demo, security review initiated",
                        "Evaluating->Decided": "Legal/procurement approval, final pricing"
                    },
                    blockers=[
                        "Security audit failure",
                        "Budget reallocation",
                        "Stakeholder departure",
                        "Competitor enterprise agreement"
                    ]
                ),
                behavioral_profile=BehavioralProfile(
                    company_size_range=(1000, 50000),
                    budget_range=(100000, 500000),
                    risk_tolerance=(0.25, 0.1),
                    price_sensitivity=(0.35, 0.1),
                    decision_speed=(0.25, 0.08),
                    influencer_susceptibility=0.4,
                    network_density=0.03
                )
            ),
            
            # Mid-Market segment (35%)
            Segment(
                id="mid_market",
                name="Mid-Market",
                size_pct=0.35,
                decision_framework=DecisionFramework(
                    stages=["Unaware", "Aware", "Considering", "Evaluating", "Decided"],
                    avg_cycle_days=45,
                    stakeholders=[
                        Stakeholder(
                            role="VP Operations",
                            influence_weight=0.4,
                            priorities={
                                "security": 0.6,
                                "integrations": 0.75,
                                "scalability": 0.65,
                                "compliance": 0.5,
                                "ease_of_use": 0.8
                            },
                            risk_tolerance=0.4
                        ),
                        Stakeholder(
                            role="Team Leads",
                            influence_weight=0.35,
                            priorities={
                                "security": 0.4,
                                "integrations": 0.7,
                                "scalability": 0.5,
                                "compliance": 0.3,
                                "ease_of_use": 0.9
                            },
                            risk_tolerance=0.5
                        ),
                        Stakeholder(
                            role="Finance",
                            influence_weight=0.25,
                            priorities={
                                "security": 0.5,
                                "integrations": 0.5,
                                "scalability": 0.6,
                                "compliance": 0.6,
                                "ease_of_use": 0.4
                            },
                            risk_tolerance=0.3
                        )
                    ],
                    triggers={
                        "Unaware->Aware": "Content marketing, webinar, or peer mention",
                        "Aware->Considering": "Growth pain, tool consolidation initiative",
                        "Considering->Evaluating": "Free trial, sales call",
                        "Evaluating->Decided": "Team buy-in, pricing approved"
                    },
                    blockers=[
                        "Integration complexity",
                        "Budget constraints",
                        "Team resistance to change",
                        "Existing contract lock-in"
                    ]
                ),
                behavioral_profile=BehavioralProfile(
                    company_size_range=(100, 999),
                    budget_range=(20000, 100000),
                    risk_tolerance=(0.45, 0.12),
                    price_sensitivity=(0.55, 0.12),
                    decision_speed=(0.45, 0.1),
                    influencer_susceptibility=0.6,
                    network_density=0.05
                )
            ),
            
            # SMB segment (50%)
            Segment(
                id="smb",
                name="SMB",
                size_pct=0.50,
                decision_framework=DecisionFramework(
                    stages=["Unaware", "Aware", "Considering", "Evaluating", "Decided"],
                    avg_cycle_days=21,
                    stakeholders=[
                        Stakeholder(
                            role="Founder/CEO",
                            influence_weight=0.6,
                            priorities={
                                "security": 0.4,
                                "integrations": 0.6,
                                "scalability": 0.4,
                                "compliance": 0.3,
                                "ease_of_use": 0.9
                            },
                            risk_tolerance=0.6
                        ),
                        Stakeholder(
                            role="Team",
                            influence_weight=0.4,
                            priorities={
                                "security": 0.3,
                                "integrations": 0.5,
                                "scalability": 0.3,
                                "compliance": 0.2,
                                "ease_of_use": 0.95
                            },
                            risk_tolerance=0.65
                        )
                    ],
                    triggers={
                        "Unaware->Aware": "Social media, review site, word of mouth",
                        "Aware->Considering": "Immediate need, free trial offer",
                        "Considering->Evaluating": "Self-serve trial, quick demo",
                        "Evaluating->Decided": "Team likes it, price works"
                    },
                    blockers=[
                        "Price too high",
                        "Too complex",
                        "No immediate need",
                        "Competitor's free tier"
                    ]
                ),
                behavioral_profile=BehavioralProfile(
                    company_size_range=(5, 99),
                    budget_range=(1000, 20000),
                    risk_tolerance=(0.6, 0.15),
                    price_sensitivity=(0.75, 0.1),
                    decision_speed=(0.7, 0.12),
                    influencer_susceptibility=0.7,
                    network_density=0.08
                )
            )
        ],
        
        competitors=[
            Competitor(
                id="monday",
                name="Monday.com",
                market_share=0.30,
                price_point=1.0,
                features={
                    "security": 0.7,
                    "integrations": 0.9,
                    "scalability": 0.8,
                    "compliance": 0.7,
                    "ease_of_use": 0.85
                },
                brand_awareness=0.85,
                aggression=0.7,
                response_speed=0.6
            ),
            Competitor(
                id="asana",
                name="Asana",
                market_share=0.25,
                price_point=0.9,
                features={
                    "security": 0.65,
                    "integrations": 0.85,
                    "scalability": 0.75,
                    "compliance": 0.65,
                    "ease_of_use": 0.9
                },
                brand_awareness=0.80,
                aggression=0.5,
                response_speed=0.5
            ),
            Competitor(
                id="jira",
                name="Jira",
                market_share=0.20,
                price_point=1.1,
                features={
                    "security": 0.9,
                    "integrations": 0.9,
                    "scalability": 0.95,
                    "compliance": 0.9,
                    "ease_of_use": 0.45
                },
                brand_awareness=0.75,
                aggression=0.3,
                response_speed=0.3
            )
        ],
        
        your_product=Product(
            id="nexus",
            name="Nexus",
            price_point=0.85,
            features={
                "security": 0.8,
                "integrations": 0.65,
                "scalability": 0.7,
                "compliance": 0.75,
                "ease_of_use": 0.9
            },
            brand_awareness=0.05
        ),
        
        simulation_days=90
    )


def get_demo_strategies() -> list[Strategy]:
    """Create demo strategies for comparison"""
    
    return [
        # Strategy 1: Value Play (SMB-focused)
        Strategy(
            id="value_play",
            name="Value Play",
            description="Lead with price and ease-of-use, target SMB",
            messaging=Messaging(
                value_proposition="Finally, project management that doesn't break the bank",
                primary_claim="Easiest PM tool to adopt, half the price of competitors",
                feature_emphasis={
                    "ease_of_use": 0.9,
                    "integrations": 0.5,
                    "security": 0.3,
                    "scalability": 0.3,
                    "compliance": 0.2
                },
                tone="value",
                full_pitch="""
Tired of paying enterprise prices for basic project management? 
Nexus gives your team everything they need—without the complexity or cost.

Get started in minutes, not months. No training required.
Your team will actually use it because it just works.
"""
            ),
            pricing=Pricing(
                base_price=0.7,
                model="per_seat",
                discount=DiscountStrategy(
                    available=True,
                    max_discount_pct=0.20,
                    triggers=["Annual commitment", "Startup program", "Team size > 20"]
                )
            ),
            gtm=GoToMarket(
                channels={
                    "paid_digital": 0.4,
                    "content": 0.3,
                    "events": 0.05,
                    "outbound": 0.15,
                    "partnerships": 0.1
                },
                intensity=0.65,
                target_segments=["smb", "mid_market"]
            ),
            launch_day=0
        ),
        
        # Strategy 2: Enterprise Premium
        Strategy(
            id="enterprise_premium",
            name="Enterprise Premium",
            description="Lead with security and compliance, target Enterprise",
            messaging=Messaging(
                value_proposition="Enterprise-grade project management with white-glove support",
                primary_claim="Built for companies that can't afford to compromise on security",
                feature_emphasis={
                    "security": 0.9,
                    "compliance": 0.85,
                    "scalability": 0.8,
                    "integrations": 0.7,
                    "ease_of_use": 0.5
                },
                tone="enterprise",
                full_pitch="""
Your company runs critical operations. Your PM tool should be just as serious.

Nexus delivers SOC 2 Type II certified security, GDPR compliance out of the box,
and 99.99% uptime SLA. Backed by dedicated success managers who know your business.

This is project management built for enterprises.
"""
            ),
            pricing=Pricing(
                base_price=1.15,
                model="flat",
                discount=DiscountStrategy(
                    available=False,
                    max_discount_pct=0.0,
                    triggers=[]
                )
            ),
            gtm=GoToMarket(
                channels={
                    "paid_digital": 0.15,
                    "content": 0.2,
                    "events": 0.3,
                    "outbound": 0.25,
                    "partnerships": 0.1
                },
                intensity=0.5,
                target_segments=["enterprise", "mid_market"]
            ),
            launch_day=0
        ),
        
        # Strategy 3: Blitz
        Strategy(
            id="market_blitz",
            name="Market Blitz",
            description="High intensity across all segments with balanced messaging",
            messaging=Messaging(
                value_proposition="The project management revolution is here",
                primary_claim="Work smarter, not harder—finally, a PM tool that gets it",
                feature_emphasis={
                    "ease_of_use": 0.8,
                    "integrations": 0.7,
                    "security": 0.6,
                    "scalability": 0.6,
                    "compliance": 0.5
                },
                tone="innovative",
                full_pitch="""
Every other project management tool makes you choose: 
Easy to use OR powerful. Affordable OR feature-rich.

Nexus breaks the tradeoff. Built from the ground up with modern teams in mind.
AI-powered workflows. Seamless integrations. Actually intuitive UX.

Join the revolution.
"""
            ),
            pricing=Pricing(
                base_price=0.85,
                model="per_seat",
                discount=DiscountStrategy(
                    available=True,
                    max_discount_pct=0.15,
                    triggers=["Annual commitment", "Growth plan"]
                )
            ),
            gtm=GoToMarket(
                channels={
                    "paid_digital": 0.35,
                    "content": 0.25,
                    "events": 0.1,
                    "outbound": 0.2,
                    "partnerships": 0.1
                },
                intensity=0.85,
                target_segments=["smb", "mid_market", "enterprise"]
            ),
            launch_day=0
        )
    ]
```

---

# PART 5: API LAYER

Create `backend/api/main.py`:

```python
"""
FastAPI application - main entry point.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
from datetime import datetime

from backend.models import Scenario, Strategy, SimulationResults, Agent
from backend.engine import SimulationRunner, DecisionEngine
from backend.data.presets.b2b_saas import get_saas_launch_scenario, get_demo_strategies


app = FastAPI(
    title="RLTX Populous API",
    description="Decision Intelligence Simulation Platform",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database for production)
scenarios_db: Dict[str, Scenario] = {}
strategies_db: Dict[str, Strategy] = {}
results_db: Dict[str, SimulationResults] = {}
agents_db: Dict[str, List[Agent]] = {}  # simulation_id -> agents

# Load presets on startup
@app.on_event("startup")
async def load_presets():
    scenario = get_saas_launch_scenario()
    scenarios_db[scenario.id] = scenario
    
    for strategy in get_demo_strategies():
        strategies_db[strategy.id] = strategy


# ============ SCENARIOS ============

@app.get("/scenarios", response_model=List[Scenario])
def list_scenarios():
    """List all available scenarios"""
    return list(scenarios_db.values())


@app.get("/scenarios/{scenario_id}", response_model=Scenario)
def get_scenario(scenario_id: str):
    """Get a specific scenario"""
    if scenario_id not in scenarios_db:
        raise HTTPException(404, "Scenario not found")
    return scenarios_db[scenario_id]


@app.post("/scenarios", response_model=Scenario)
def create_scenario(scenario: Scenario):
    """Create a new scenario"""
    if not scenario.id:
        scenario.id = str(uuid.uuid4())
    scenarios_db[scenario.id] = scenario
    return scenario


# ============ STRATEGIES ============

@app.get("/strategies", response_model=List[Strategy])
def list_strategies():
    """List all available strategies"""
    return list(strategies_db.values())


@app.get("/strategies/{strategy_id}", response_model=Strategy)
def get_strategy(strategy_id: str):
    """Get a specific strategy"""
    if strategy_id not in strategies_db:
        raise HTTPException(404, "Strategy not found")
    return strategies_db[strategy_id]


@app.post("/strategies", response_model=Strategy)
def create_strategy(strategy: Strategy):
    """Create a new strategy"""
    if not strategy.id:
        strategy.id = str(uuid.uuid4())
    strategies_db[strategy.id] = strategy
    return strategy


# ============ SIMULATIONS ============

class SimulationRequest(BaseModel):
    scenario_id: str
    strategy_id: str
    num_agents: int = 10000
    num_branches: int = 500
    use_llm_personas: bool = False


class SimulationStatus(BaseModel):
    id: str
    status: str  # "pending", "running", "completed", "failed"
    progress: float
    result_id: Optional[str] = None


# Track running simulations
running_simulations: Dict[str, SimulationStatus] = {}


@app.post("/simulations", response_model=SimulationStatus)
async def run_simulation(request: SimulationRequest, background_tasks: BackgroundTasks):
    """Start a simulation run"""
    
    if request.scenario_id not in scenarios_db:
        raise HTTPException(404, "Scenario not found")
    if request.strategy_id not in strategies_db:
        raise HTTPException(404, "Strategy not found")
    
    sim_id = str(uuid.uuid4())
    
    status = SimulationStatus(
        id=sim_id,
        status="pending",
        progress=0.0
    )
    running_simulations[sim_id] = status
    
    # Run in background
    background_tasks.add_task(
        _run_simulation_task,
        sim_id,
        request
    )
    
    return status


async def _run_simulation_task(sim_id: str, request: SimulationRequest):
    """Background task to run simulation"""
    
    try:
        running_simulations[sim_id].status = "running"
        
        scenario = scenarios_db[request.scenario_id]
        strategy = strategies_db[request.strategy_id]
        
        runner = SimulationRunner(
            scenario=scenario,
            strategy=strategy,
            num_agents=request.num_agents,
            num_branches=request.num_branches,
            use_llm_personas=request.use_llm_personas,
            parallel=True
        )
        
        results = runner.run()
        
        # Store results
        results_db[results.id] = results
        
        # Generate insight
        results.insight = await _generate_insight(results, scenario, strategy)
        
        running_simulations[sim_id].status = "completed"
        running_simulations[sim_id].progress = 1.0
        running_simulations[sim_id].result_id = results.id
        
    except Exception as e:
        running_simulations[sim_id].status = "failed"
        print(f"Simulation failed: {e}")


async def _generate_insight(
    results: SimulationResults,
    scenario: Scenario,
    strategy: Strategy
) -> str:
    """Generate natural language insight about results"""
    
    import anthropic
    client = anthropic.Anthropic()
    
    segment_breakdown = "\n".join([
        f"- {s.segment_name}: {s.conversion_rate*100:.1f}%"
        for s in results.segment_analysis
    ])
    
    drivers = "\n".join([
        f"- {d.factor}: {d.description}"
        for d in results.top_drivers[:3]
    ])
    
    blockers = "\n".join([
        f"- {d.factor}: {d.description}"
        for d in results.top_blockers[:3]
    ])
    
    prompt = f"""Analyze these simulation results and write a 3-4 sentence executive insight.

STRATEGY: {strategy.name}
{strategy.description}

RESULTS:
- Mean conversion: {results.mean_conversion*100:.1f}%
- Range (90% CI): {results.p5*100:.1f}% - {results.p95*100:.1f}%
- Standard deviation: {results.std_conversion*100:.2f}%

SEGMENT BREAKDOWN:
{segment_breakdown}

TOP DRIVERS:
{drivers}

TOP BLOCKERS:
{blockers}

Write a clear, actionable insight. Be specific about:
1. Which strategy aspect is working
2. Where the risk is
3. What would improve outcomes

Keep it to 3-4 sentences. No bullet points. Executive-level language."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text


@app.get("/simulations/{sim_id}/status", response_model=SimulationStatus)
def get_simulation_status(sim_id: str):
    """Get simulation status"""
    if sim_id not in running_simulations:
        raise HTTPException(404, "Simulation not found")
    return running_simulations[sim_id]


@app.get("/results/{result_id}", response_model=SimulationResults)
def get_results(result_id: str):
    """Get simulation results"""
    if result_id not in results_db:
        raise HTTPException(404, "Results not found")
    return results_db[result_id]


# ============ COMPARISON ============

class ComparisonRequest(BaseModel):
    scenario_id: str
    strategy_ids: List[str]
    num_agents: int = 5000
    num_branches: int = 200


class ComparisonResult(BaseModel):
    strategy_id: str
    strategy_name: str
    mean_conversion: float
    std_conversion: float
    p5: float
    p95: float
    segment_breakdown: Dict[str, float]


class ComparisonResponse(BaseModel):
    scenario_id: str
    comparisons: List[ComparisonResult]
    winner: str
    insight: str


@app.post("/compare", response_model=ComparisonResponse)
async def compare_strategies(request: ComparisonRequest):
    """Compare multiple strategies side by side"""
    
    if request.scenario_id not in scenarios_db:
        raise HTTPException(404, "Scenario not found")
    
    scenario = scenarios_db[request.scenario_id]
    comparisons = []
    
    for strategy_id in request.strategy_ids:
        if strategy_id not in strategies_db:
            raise HTTPException(404, f"Strategy {strategy_id} not found")
        
        strategy = strategies_db[strategy_id]
        
        runner = SimulationRunner(
            scenario=scenario,
            strategy=strategy,
            num_agents=request.num_agents,
            num_branches=request.num_branches,
            use_llm_personas=False,
            parallel=True
        )
        
        results = runner.run()
        
        comparisons.append(ComparisonResult(
            strategy_id=strategy_id,
            strategy_name=strategy.name,
            mean_conversion=results.mean_conversion,
            std_conversion=results.std_conversion,
            p5=results.p5,
            p95=results.p95,
            segment_breakdown={
                s.segment_id: s.conversion_rate 
                for s in results.segment_analysis
            }
        ))
    
    # Find winner
    winner = max(comparisons, key=lambda c: c.mean_conversion)
    
    # Generate comparison insight
    insight = await _generate_comparison_insight(comparisons, scenario)
    
    return ComparisonResponse(
        scenario_id=request.scenario_id,
        comparisons=comparisons,
        winner=winner.strategy_id,
        insight=insight
    )


async def _generate_comparison_insight(
    comparisons: List[ComparisonResult],
    scenario: Scenario
) -> str:
    """Generate insight comparing strategies"""
    
    import anthropic
    client = anthropic.Anthropic()
    
    comp_text = "\n".join([
        f"- {c.strategy_name}: {c.mean_conversion*100:.1f}% (range: {c.p5*100:.1f}%-{c.p95*100:.1f}%)"
        for c in comparisons
    ])
    
    prompt = f"""Compare these strategies and provide a 2-3 sentence recommendation.

STRATEGIES COMPARED:
{comp_text}

Write a clear recommendation that:
1. Names the winning strategy
2. Explains WHY it wins
3. Notes any tradeoffs (e.g., higher risk for higher return)

Keep it concise and actionable."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text


# ============ AGENT DEEP-DIVE ============

class AgentChatRequest(BaseModel):
    message: str


class AgentChatResponse(BaseModel):
    response: str
    agent_stage: str
    agent_decision: Optional[str]


# Store chat sessions
agent_chats: Dict[str, List[Dict]] = {}  # agent_id -> conversation


@app.get("/results/{result_id}/agents")
def list_agents(result_id: str, segment: Optional[str] = None, limit: int = 50):
    """List agents from a simulation for exploration"""
    
    if result_id not in results_db:
        raise HTTPException(404, "Results not found")
    
    # For demo, we need to re-run with stored agents
    # In production, agents would be stored in database
    
    results = results_db[result_id]
    scenario = scenarios_db[results.scenario_id]
    strategy = strategies_db[results.strategy_id]
    
    # Re-create sample agents with personas
    from backend.engine import AgentFactory
    factory = AgentFactory(use_llm=True, llm_sample_size=limit)
    
    agents = factory.create_population(
        scenario.segments,
        min(limit * 3, 500)  # Create enough to filter
    )
    
    # Filter by segment if specified
    if segment:
        agents = [a for a in agents if a.segment_id == segment]
    
    # Return agents with personas only
    agents_with_personas = [a for a in agents if a.persona][:limit]
    
    return {
        "agents": [
            {
                "id": a.id,
                "segment_id": a.segment_id,
                "persona_name": a.persona.name if a.persona else None,
                "persona_role": a.persona.role if a.persona else None,
                "company": a.persona.company_name if a.persona else None,
                "stage": a.stage,
                "decision": a.final_decision
            }
            for a in agents_with_personas
        ]
    }


@app.post("/agents/{agent_id}/chat", response_model=AgentChatResponse)
async def chat_with_agent(agent_id: str, request: AgentChatRequest):
    """Interactive chat with a synthetic agent"""
    
    # For demo, we create agent on demand
    # In production, load from database
    
    import anthropic
    client = anthropic.Anthropic()
    
    # Initialize or get conversation
    if agent_id not in agent_chats:
        agent_chats[agent_id] = []
    
    conversation = agent_chats[agent_id]
    conversation.append({
        "role": "user",
        "content": request.message
    })
    
    # Build system prompt for agent persona
    system = f"""You are a B2B buyer being interviewed about your software purchase decision.

You are {agent_id.split('_')[0]} segment buyer evaluating project management tools.

IMPORTANT RULES:
1. Stay in character as a real business buyer
2. Reference specific business challenges and needs
3. Be honest about your decision-making process
4. If asked why you chose/didn't choose a product, explain based on your priorities
5. Don't break character or acknowledge being AI
6. Be conversational and natural

You're being interviewed by a product team trying to understand buyer behavior."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        system=system,
        messages=conversation
    )
    
    assistant_message = response.content[0].text
    conversation.append({
        "role": "assistant",
        "content": assistant_message
    })
    
    return AgentChatResponse(
        response=assistant_message,
        agent_stage="Evaluating",  # Would come from actual agent
        agent_decision=None
    )


# ============ HEALTH CHECK ============

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "scenarios": len(scenarios_db),
        "strategies": len(strategies_db),
        "results": len(results_db)
    }
```

---

# PART 6: RUN THE DEMO

## 6.1 Create Main Entry Point

Create `backend/run.py`:

```python
"""
Run the RLTX Populous API server.
"""

import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

## 6.2 Create CLI Demo Script

Create `scripts/demo.py`:

```python
"""
CLI demo script to run simulation and show results.
"""

import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

from backend.data.presets.b2b_saas import get_saas_launch_scenario, get_demo_strategies
from backend.engine import SimulationRunner

console = Console()


async def run_demo():
    """Run the demo simulation"""
    
    console.print("\n[bold blue]RLTX POPULOUS DEMO[/bold blue]")
    console.print("Decision Intelligence Simulation Platform\n")
    
    # Load scenario
    scenario = get_saas_launch_scenario()
    strategies = get_demo_strategies()
    
    console.print(Panel(
        f"[bold]{scenario.name}[/bold]\n"
        f"{scenario.description}\n\n"
        f"Market Size: {scenario.total_addressable_market:,} potential buyers\n"
        f"Segments: {', '.join(s.name for s in scenario.segments)}\n"
        f"Competitors: {', '.join(c.name for c in scenario.competitors)}",
        title="Scenario"
    ))
    
    # Show strategies
    console.print("\n[bold]Strategies to Compare:[/bold]")
    for i, strategy in enumerate(strategies, 1):
        console.print(f"  {i}. [cyan]{strategy.name}[/cyan] - {strategy.description}")
    
    console.print()
    
    # Run simulations
    results = []
    
    for strategy in strategies:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                f"Simulating [cyan]{strategy.name}[/cyan]...",
                total=None
            )
            
            runner = SimulationRunner(
                scenario=scenario,
                strategy=strategy,
                num_agents=5000,  # Reduced for demo speed
                num_branches=200,
                use_llm_personas=False,
                parallel=True
            )
            
            result = runner.run()
            results.append((strategy, result))
    
    # Display results
    console.print("\n[bold]RESULTS[/bold]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Strategy")
    table.add_column("Mean Conversion", justify="right")
    table.add_column("90% CI", justify="right")
    table.add_column("Best Case", justify="right")
    table.add_column("Worst Case", justify="right")
    
    for strategy, result in results:
        table.add_row(
            strategy.name,
            f"{result.mean_conversion*100:.1f}%",
            f"{result.p5*100:.1f}% - {result.p95*100:.1f}%",
            f"{result.p95*100:.1f}%",
            f"{result.p5*100:.1f}%"
        )
    
    console.print(table)
    
    # Find winner
    winner_strategy, winner_result = max(results, key=lambda x: x[1].mean_conversion)
    
    console.print(f"\n[bold green]Winner: {winner_strategy.name}[/bold green]")
    console.print(f"Expected conversion: {winner_result.mean_conversion*100:.1f}%")
    
    # Segment breakdown
    console.print("\n[bold]Segment Performance (Winner)[/bold]")
    for seg_analysis in winner_result.segment_analysis:
        console.print(
            f"  {seg_analysis.segment_name}: "
            f"[cyan]{seg_analysis.conversion_rate*100:.1f}%[/cyan]"
        )
    
    # Drivers
    if winner_result.top_drivers:
        console.print("\n[bold]Key Drivers[/bold]")
        for driver in winner_result.top_drivers[:3]:
            console.print(f"  ✓ {driver.factor}: {driver.description}")
    
    if winner_result.top_blockers:
        console.print("\n[bold]Key Risks[/bold]")
        for blocker in winner_result.top_blockers[:3]:
            console.print(f"  ✗ {blocker.factor}: {blocker.description}")
    
    console.print()


if __name__ == "__main__":
    asyncio.run(run_demo())
```

## 6.3 Run Commands

```bash
# Make sure you're in the project directory with venv activated

# Run the API server
python -m backend.run

# In another terminal, run the CLI demo
python scripts/demo.py

# Or use curl to test API
curl http://localhost:8000/health
curl http://localhost:8000/scenarios
curl http://localhost:8000/strategies

# Run a simulation
curl -X POST http://localhost:8000/simulations \
  -H "Content-Type: application/json" \
  -d '{"scenario_id": "saas_launch_2024", "strategy_id": "value_play", "num_agents": 5000, "num_branches": 100}'

# Compare strategies
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{"scenario_id": "saas_launch_2024", "strategy_ids": ["value_play", "enterprise_premium", "market_blitz"], "num_agents": 5000, "num_branches": 100}'
```

---

# PART 7: FRONTEND (OPTIONAL - REFLEX)

If you want a quick UI, use Reflex. Create `frontend/app.py`:

```python
"""
RLTX Populous Frontend - Reflex App
"""

import reflex as rx
import httpx
from typing import List, Dict, Optional


class State(rx.State):
    """Application state"""
    
    # Data
    scenarios: List[Dict] = []
    strategies: List[Dict] = []
    selected_scenario: str = ""
    selected_strategies: List[str] = []
    
    # Results
    is_running: bool = False
    comparison_results: List[Dict] = []
    winner: str = ""
    insight: str = ""
    
    # Agent chat
    selected_agent: str = ""
    chat_messages: List[Dict] = []
    chat_input: str = ""
    
    async def load_data(self):
        """Load scenarios and strategies from API"""
        async with httpx.AsyncClient() as client:
            scenarios_resp = await client.get("http://localhost:8000/scenarios")
            strategies_resp = await client.get("http://localhost:8000/strategies")
            
            self.scenarios = scenarios_resp.json()
            self.strategies = strategies_resp.json()
            
            if self.scenarios:
                self.selected_scenario = self.scenarios[0]["id"]
    
    def toggle_strategy(self, strategy_id: str):
        """Toggle strategy selection"""
        if strategy_id in self.selected_strategies:
            self.selected_strategies.remove(strategy_id)
        else:
            self.selected_strategies.append(strategy_id)
    
    async def run_comparison(self):
        """Run strategy comparison"""
        if not self.selected_strategies:
            return
        
        self.is_running = True
        self.comparison_results = []
        
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                "http://localhost:8000/compare",
                json={
                    "scenario_id": self.selected_scenario,
                    "strategy_ids": self.selected_strategies,
                    "num_agents": 5000,
                    "num_branches": 200
                }
            )
            
            data = response.json()
            self.comparison_results = data["comparisons"]
            self.winner = data["winner"]
            self.insight = data["insight"]
        
        self.is_running = False
    
    async def send_chat(self):
        """Send message to agent"""
        if not self.chat_input or not self.selected_agent:
            return
        
        self.chat_messages.append({
            "role": "user",
            "content": self.chat_input
        })
        
        message = self.chat_input
        self.chat_input = ""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:8000/agents/{self.selected_agent}/chat",
                json={"message": message}
            )
            
            data = response.json()
            self.chat_messages.append({
                "role": "assistant",
                "content": data["response"]
            })


def strategy_card(strategy: Dict) -> rx.Component:
    """Render a strategy card"""
    is_selected = State.selected_strategies.contains(strategy["id"])
    
    return rx.box(
        rx.vstack(
            rx.text(strategy["name"], font_weight="bold"),
            rx.text(strategy["description"], font_size="sm", color="gray.600"),
            align_items="start",
            width="100%"
        ),
        padding="4",
        border_radius="md",
        border="2px solid",
        border_color=rx.cond(is_selected, "blue.500", "gray.200"),
        bg=rx.cond(is_selected, "blue.50", "white"),
        cursor="pointer",
        on_click=lambda: State.toggle_strategy(strategy["id"]),
        _hover={"border_color": "blue.300"}
    )


def result_card(result: Dict) -> rx.Component:
    """Render a comparison result card"""
    is_winner = result["strategy_id"] == State.winner
    
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(result["strategy_name"], font_weight="bold", font_size="lg"),
                rx.cond(
                    is_winner,
                    rx.badge("WINNER", color_scheme="green"),
                    rx.fragment()
                ),
                justify="between",
                width="100%"
            ),
            rx.hstack(
                rx.stat(
                    rx.stat_label("Mean Conversion"),
                    rx.stat_number(f"{result['mean_conversion']*100:.1f}%"),
                ),
                rx.stat(
                    rx.stat_label("90% CI"),
                    rx.stat_number(
                        f"{result['p5']*100:.1f}% - {result['p95']*100:.1f}%"
                    ),
                ),
                spacing="8"
            ),
            align_items="start",
            width="100%"
        ),
        padding="6",
        border_radius="lg",
        border="2px solid",
        border_color=rx.cond(is_winner, "green.400", "gray.200"),
        bg=rx.cond(is_winner, "green.50", "white")
    )


def chat_message(msg: Dict) -> rx.Component:
    """Render a chat message"""
    is_user = msg["role"] == "user"
    
    return rx.box(
        rx.text(msg["content"]),
        padding="3",
        border_radius="lg",
        bg=rx.cond(is_user, "blue.100", "gray.100"),
        align_self=rx.cond(is_user, "end", "start"),
        max_width="80%"
    )


def index() -> rx.Component:
    """Main page"""
    return rx.box(
        rx.vstack(
            # Header
            rx.heading("RLTX Populous", size="xl"),
            rx.text("Decision Intelligence Simulation", color="gray.600"),
            
            rx.divider(),
            
            # Scenario selector
            rx.select(
                rx.foreach(
                    State.scenarios,
                    lambda s: rx.option(s["name"], value=s["id"])
                ),
                value=State.selected_scenario,
                on_change=State.set_selected_scenario,
                placeholder="Select scenario"
            ),
            
            # Strategy selection
            rx.heading("Select Strategies to Compare", size="md"),
            rx.hstack(
                rx.foreach(
                    State.strategies,
                    strategy_card
                ),
                spacing="4",
                flex_wrap="wrap"
            ),
            
            # Run button
            rx.button(
                rx.cond(
                    State.is_running,
                    rx.spinner(size="sm"),
                    rx.text("Run Comparison")
                ),
                on_click=State.run_comparison,
                is_disabled=State.is_running,
                color_scheme="blue",
                size="lg"
            ),
            
            # Results
            rx.cond(
                State.comparison_results.length() > 0,
                rx.vstack(
                    rx.heading("Results", size="lg"),
                    rx.foreach(
                        State.comparison_results,
                        result_card
                    ),
                    rx.box(
                        rx.text(State.insight),
                        padding="4",
                        bg="gray.50",
                        border_radius="md"
                    ),
                    width="100%",
                    spacing="4"
                )
            ),
            
            spacing="6",
            align_items="stretch",
            width="100%",
            max_width="1200px",
            margin="auto",
            padding="8"
        ),
        on_mount=State.load_data
    )


app = rx.App()
app.add_page(index)
```

Run frontend:
```bash
cd frontend
reflex init
reflex run
```

---

# PART 8: TESTING

Create `tests/test_engine.py`:

```python
"""
Test simulation engine components.
"""

import pytest
from backend.models import *
from backend.engine import *
from backend.data.presets.b2b_saas import get_saas_launch_scenario, get_demo_strategies


def test_agent_factory_creates_agents():
    """Test agent creation"""
    scenario = get_saas_launch_scenario()
    factory = AgentFactory(use_llm=False)
    
    agents = factory.create_population(scenario.segments, 1000)
    
    assert len(agents) == 1000
    assert all(isinstance(a, Agent) for a in agents)
    
    # Check segment distribution
    smb_count = sum(1 for a in agents if a.segment_id == "smb")
    assert 400 < smb_count < 600  # ~50% with some variance


def test_decision_engine_updates_awareness():
    """Test awareness updates"""
    engine = DecisionEngine()
    
    agent = Agent(
        id="test_1",
        segment_id="smb",
        risk_tolerance=0.5,
        price_sensitivity=0.5,
        feature_priorities={"ease_of_use": 0.8},
        decision_speed=0.5,
        influencer_susceptibility=0.5,
        stage="Unaware",
        awareness={},
        consideration_set=[],
        connections=[]
    )
    
    signals = {"product_a": 0.5}
    
    agent = engine._update_awareness(agent, signals, day=1)
    
    assert "product_a" in agent.awareness
    assert agent.awareness["product_a"] > 0


def test_simulation_runner_completes():
    """Test full simulation run"""
    scenario = get_saas_launch_scenario()
    strategy = get_demo_strategies()[0]
    
    runner = SimulationRunner(
        scenario=scenario,
        strategy=strategy,
        num_agents=500,
        num_branches=10,
        use_llm_personas=False,
        parallel=False
    )
    
    results = runner.run()
    
    assert results is not None
    assert results.mean_conversion >= 0
    assert results.mean_conversion <= 1
    assert len(results.branches) == 10


def test_market_dynamics_signals():
    """Test market signal generation"""
    scenario = get_saas_launch_scenario()
    strategy = get_demo_strategies()[0]
    
    market = MarketDynamics(scenario, strategy)
    
    signals = market.get_signals(day=30, agents=[])
    
    assert scenario.your_product.id in signals
    assert all(c.id in signals for c in scenario.competitors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

Run tests:
```bash
pytest tests/ -v
```

---

# PART 9: QUICK START CHECKLIST

## First Time Setup

```bash
# 1. Clone/create project
mkdir rltx-populous && cd rltx-populous

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Create directory structure
mkdir -p backend/{models,engine,api,data/presets}
mkdir -p scripts tests

# 4. Create requirements.txt (copy from Part 1.2)
# 5. Install dependencies
pip install -r requirements.txt

# 6. Create .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# 7. Copy all the code files from this guide

# 8. Run tests
pytest tests/ -v

# 9. Start API server
python -m backend.run

# 10. Run CLI demo (new terminal)
python scripts/demo.py
```

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| GET | /scenarios | List scenarios |
| GET | /scenarios/{id} | Get scenario |
| GET | /strategies | List strategies |
| GET | /strategies/{id} | Get strategy |
| POST | /simulations | Start simulation |
| GET | /simulations/{id}/status | Check status |
| GET | /results/{id} | Get results |
| POST | /compare | Compare strategies |
| POST | /agents/{id}/chat | Chat with agent |

---

# PART 10: WHAT TO DEMO

## Demo Script

1. **Open CLI demo or Reflex UI**

2. **Show the scenario:**
   "This is a B2B SaaS market. 50,000 potential buyers across three segments: Enterprise, Mid-Market, and SMB. Three established competitors."

3. **Show the strategies:**
   "We're testing three go-to-market strategies: Value Play targeting SMB, Enterprise Premium, and Market Blitz."

4. **Run the comparison:**
   "Watch as we simulate thousands of possible futures..."

5. **Show results:**
   "Market Blitz wins with 11.2% conversion on average. But look at the range—it could be as high as 15% or as low as 7%."

6. **Show the insight:**
   "The AI explains why: Mid-Market is the swing segment. When we win there, we win overall. When competitors respond early, we lose."

7. **Chat with an agent (if time):**
   "Let's talk to a synthetic buyer who chose the competitor. Why didn't you choose us?"

8. **Close:**
   "This is what decisions look like when you can see all the futures. What decision are you making this quarter that you wish you could test first?"

---

# APPENDIX: FILE TREE

```
rltx-populous/
├── .env
├── requirements.txt
├── backend/
│   ├── __init__.py
│   ├── run.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── scenario.py
│   │   ├── agent.py
│   │   ├── strategy.py
│   │   └── results.py
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── agent_factory.py
│   │   ├── decision_engine.py
│   │   ├── market_dynamics.py
│   │   └── runner.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py
│   └── data/
│       └── presets/
│           ├── __init__.py
│           └── b2b_saas.py
├── frontend/
│   └── app.py
├── scripts/
│   └── demo.py
└── tests/
    └── test_engine.py
```

---

**END OF BUILD GUIDE**

Give this to Claude. It will build the full system.
