# SURGICAL BUILD PLAN - Part 3
## API Layer, Frontend Components, Build Sequence

---

# PART 3: API LAYER

All API routes in a single FastAPI application with clear organization.

## 3.1 Main Application Entry

### File: `backend/api/main.py`
```python
"""
RLTX Populous API
Main FastAPI application with all routes
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import uuid
from anthropic import Anthropic
import os

# Import models
from backend.models.decision import Decision, DecisionStatus, Option, Constraint, SuccessCriteria
from backend.models.world import World, Segment, Competitor, Product
from backend.models.agent import Agent
from backend.models.simulation import Simulation, SimulationConfig, Event, SimulationStatus
from backend.models.trace import Trace
from backend.models.action import Recommendation

# Import engines
from backend.engine.agent_engine import AgentEngine
from backend.engine.simulation_engine import SimulationEngine
from backend.engine.network_engine import NetworkEngine
from backend.engine.trace_engine import TraceEngine
from backend.engine.decision_engine import DecisionEngine
from backend.engine.chat_engine import ChatEngine
from backend.engine.prediction_engine import PredictionEngine
from backend.engine.bias_engine import BiasEngine

# Initialize app
app = FastAPI(
    title="RLTX Populous API",
    description="Decision Intelligence Platform API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM client
anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Initialize engines
agent_engine = AgentEngine(anthropic)
network_engine = NetworkEngine()
simulation_engine = SimulationEngine(agent_engine, network_engine)
trace_engine = TraceEngine(anthropic)
decision_engine = DecisionEngine(anthropic)
chat_engine = ChatEngine(anthropic)
prediction_engine = PredictionEngine(anthropic)
bias_engine = BiasEngine(anthropic)

# In-memory storage (replace with DB in production)
decisions_db: Dict[str, Decision] = {}
worlds_db: Dict[str, World] = {}
audiences_db: Dict[str, List[Agent]] = {}
simulations_db: Dict[str, Simulation] = {}
traces_db: Dict[str, Trace] = {}
recommendations_db: Dict[str, Recommendation] = {}

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ==================== DECISIONS API ====================

class CreateDecisionRequest(BaseModel):
    title: str
    description: str
    options: List[Dict]
    constraints: List[Dict] = []
    success_criteria: Dict

@app.post("/api/decisions")
async def create_decision(request: CreateDecisionRequest):
    """Create a new decision"""
    decision_id = str(uuid.uuid4())

    options = [Option(**opt) for opt in request.options]
    constraints = [Constraint(**c) for c in request.constraints]
    success = SuccessCriteria(**request.success_criteria)

    decision = Decision(
        id=decision_id,
        title=request.title,
        description=request.description,
        options=options,
        constraints=constraints,
        success_criteria=success,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    decisions_db[decision_id] = decision
    return {"id": decision_id, "decision": decision.model_dump()}

@app.get("/api/decisions")
async def list_decisions():
    """List all decisions"""
    return {"decisions": [d.model_dump() for d in decisions_db.values()]}

@app.get("/api/decisions/{decision_id}")
async def get_decision(decision_id: str):
    """Get a specific decision"""
    if decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decisions_db[decision_id].model_dump()

@app.put("/api/decisions/{decision_id}")
async def update_decision(decision_id: str, updates: Dict):
    """Update a decision"""
    if decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")

    decision = decisions_db[decision_id]
    for key, value in updates.items():
        if hasattr(decision, key):
            setattr(decision, key, value)
    decision.updated_at = datetime.now()

    return decision.model_dump()


# ==================== WORLDS API ====================

class CreateWorldRequest(BaseModel):
    name: str
    description: str
    total_addressable_market: int
    market_growth_rate: float
    segments: List[Dict]
    competitors: List[Dict]
    your_product: Dict
    your_market_share: float

@app.post("/api/worlds")
async def create_world(request: CreateWorldRequest):
    """Create a market world"""
    world_id = str(uuid.uuid4())

    world = World(
        id=world_id,
        name=request.name,
        description=request.description,
        total_addressable_market=request.total_addressable_market,
        market_growth_rate=request.market_growth_rate,
        segments=[Segment(**s) for s in request.segments],
        competitors=[Competitor(**c) for c in request.competitors],
        your_product=Product(**request.your_product),
        your_market_share=request.your_market_share,
        created_at=datetime.now()
    )

    worlds_db[world_id] = world
    return {"id": world_id, "world": world.model_dump()}

@app.get("/api/worlds")
async def list_worlds():
    """List all worlds"""
    return {"worlds": [w.model_dump() for w in worlds_db.values()]}

@app.get("/api/worlds/{world_id}")
async def get_world(world_id: str):
    """Get a specific world"""
    if world_id not in worlds_db:
        raise HTTPException(status_code=404, detail="World not found")
    return worlds_db[world_id].model_dump()


# ==================== AUDIENCES API ====================

class CreateAudienceRequest(BaseModel):
    name: str
    description: str
    size: int  # Number of agents to generate
    world_id: str
    segment_distribution: Dict[str, float]  # segment_id -> percentage

class GenerateAgentsRequest(BaseModel):
    audience_id: str
    segment: Dict
    count: int

@app.post("/api/audiences")
async def create_audience(request: CreateAudienceRequest, background_tasks: BackgroundTasks):
    """Create and generate an audience"""
    audience_id = str(uuid.uuid4())

    if request.world_id not in worlds_db:
        raise HTTPException(status_code=404, detail="World not found")

    world = worlds_db[request.world_id]

    # Start generation in background
    background_tasks.add_task(
        _generate_audience,
        audience_id,
        request.size,
        request.segment_distribution,
        world
    )

    audiences_db[audience_id] = []  # Placeholder

    return {
        "id": audience_id,
        "status": "generating",
        "size": request.size
    }

async def _generate_audience(
    audience_id: str,
    size: int,
    segment_distribution: Dict[str, float],
    world: World
):
    """Background task to generate audience"""
    agents = []

    for segment in world.segments:
        seg_percent = segment_distribution.get(segment.id, 1.0 / len(world.segments))
        seg_count = int(size * seg_percent)

        for i in range(seg_count):
            agent = _generate_single_agent(segment, i)
            agents.append(agent)

    # Build social network
    network_engine.build_network(agents)

    audiences_db[audience_id] = agents

def _generate_single_agent(segment: Segment, index: int) -> Agent:
    """Generate a single agent with realistic attributes"""
    import numpy as np

    # Sample from segment characteristics
    return Agent(
        id=f"agent_{uuid.uuid4().hex[:8]}",
        name=f"Customer_{index}",
        age=np.random.randint(25, 65),
        occupation=_random_occupation(segment),
        income=_sample_income(segment),
        location=_random_location(),
        education=_random_education(),
        segment_id=segment.id,
        personality={
            "openness": np.random.beta(5, 5),
            "conscientiousness": np.random.beta(5, 5),
            "extraversion": np.random.beta(5, 5),
            "agreeableness": np.random.beta(5, 5),
            "neuroticism": np.random.beta(5, 5)
        },
        values=_random_values(),
        pain_points=_random_pain_points(segment),
        goals=_random_goals(segment),
        price_sensitivity=segment.price_sensitivity + np.random.uniform(-0.2, 0.2),
        brand_loyalty=segment.brand_loyalty + np.random.uniform(-0.2, 0.2),
        risk_tolerance=segment.risk_tolerance + np.random.uniform(-0.2, 0.2),
        social_influence=np.random.beta(2, 5),
        decision_style=np.random.choice(["analytical", "intuitive", "social", "habitual"]),
        utility_weights={
            "price": np.random.uniform(0.2, 0.4),
            "quality": np.random.uniform(0.2, 0.4),
            "convenience": np.random.uniform(0.1, 0.3),
            "status": np.random.uniform(0.0, 0.2)
        }
    )

# Helper functions for agent generation
def _random_occupation(segment) -> str:
    occupations = ["Software Engineer", "Marketing Manager", "CFO", "Product Manager",
                   "Sales Director", "Analyst", "Consultant", "VP Engineering"]
    return np.random.choice(occupations)

def _sample_income(segment) -> float:
    return np.random.uniform(80000, 250000)

def _random_location() -> str:
    cities = ["San Francisco", "New York", "Austin", "Seattle", "Boston", "Chicago"]
    return np.random.choice(cities)

def _random_education() -> str:
    return np.random.choice(["Bachelor's", "Master's", "MBA", "PhD"])

def _random_values() -> List[str]:
    all_values = ["efficiency", "innovation", "reliability", "growth", "quality", "cost-savings"]
    return list(np.random.choice(all_values, size=3, replace=False))

def _random_pain_points(segment) -> List[str]:
    pains = ["manual processes", "lack of insights", "slow reporting", "integration issues"]
    return list(np.random.choice(pains, size=2, replace=False))

def _random_goals(segment) -> List[str]:
    goals = ["reduce costs", "increase efficiency", "better decisions", "faster growth"]
    return list(np.random.choice(goals, size=2, replace=False))

@app.get("/api/audiences")
async def list_audiences():
    """List all audiences"""
    result = []
    for audience_id, agents in audiences_db.items():
        result.append({
            "id": audience_id,
            "size": len(agents),
            "status": "ready" if agents else "generating"
        })
    return {"audiences": result}

@app.get("/api/audiences/{audience_id}")
async def get_audience(audience_id: str, limit: int = 50):
    """Get audience details with sample of agents"""
    if audience_id not in audiences_db:
        raise HTTPException(status_code=404, detail="Audience not found")

    agents = audiences_db[audience_id]
    return {
        "id": audience_id,
        "total_size": len(agents),
        "agents": [a.model_dump() for a in agents[:limit]]
    }

@app.get("/api/audiences/{audience_id}/agents/{agent_id}")
async def get_agent(audience_id: str, agent_id: str):
    """Get a specific agent"""
    if audience_id not in audiences_db:
        raise HTTPException(status_code=404, detail="Audience not found")

    agents = audiences_db[audience_id]
    agent = next((a for a in agents if a.id == agent_id), None)

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent.model_dump()


# ==================== SIMULATIONS API ====================

class RunSimulationRequest(BaseModel):
    decision_id: str
    world_id: str
    audience_id: str
    option_id: str
    duration_days: int = 90
    num_branches: int = 100  # Reduced for demo speed
    events: List[Dict] = []

@app.post("/api/simulations")
async def run_simulation(request: RunSimulationRequest, background_tasks: BackgroundTasks):
    """Start a simulation"""
    sim_id = str(uuid.uuid4())

    # Validate references
    if request.decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")
    if request.world_id not in worlds_db:
        raise HTTPException(status_code=404, detail="World not found")
    if request.audience_id not in audiences_db:
        raise HTTPException(status_code=404, detail="Audience not found")

    decision = decisions_db[request.decision_id]
    option = next((o for o in decision.options if o.id == request.option_id), None)
    if not option:
        raise HTTPException(status_code=404, detail="Option not found")

    # Create config
    config = SimulationConfig(
        decision_id=request.decision_id,
        world_id=request.world_id,
        audience_id=request.audience_id,
        option_id=request.option_id,
        duration_days=request.duration_days,
        num_branches=request.num_branches,
        events=[Event(**e) for e in request.events]
    )

    # Create placeholder simulation
    simulation = Simulation(
        id=sim_id,
        config=config,
        status=SimulationStatus.PENDING
    )
    simulations_db[sim_id] = simulation

    # Run in background
    background_tasks.add_task(
        _run_simulation_background,
        sim_id,
        config,
        worlds_db[request.world_id],
        audiences_db[request.audience_id],
        option.model_dump()
    )

    return {"id": sim_id, "status": "pending"}

async def _run_simulation_background(
    sim_id: str,
    config: SimulationConfig,
    world: World,
    agents: List[Agent],
    option: Dict
):
    """Background task to run simulation"""
    import copy

    simulations_db[sim_id].status = SimulationStatus.RUNNING

    try:
        # Deep copy agents for simulation
        sim_agents = copy.deepcopy(agents)

        # Run simulation
        result = simulation_engine.run_simulation(
            config=config,
            agents=sim_agents,
            world=world,
            option=option,
            progress_callback=lambda p: _update_sim_progress(sim_id, p)
        )

        simulations_db[sim_id] = result

        # Generate trace
        trace = trace_engine.generate_trace(result, sim_agents, option)
        traces_db[f"{sim_id}_{option['id']}"] = trace

    except Exception as e:
        simulations_db[sim_id].status = SimulationStatus.FAILED
        simulations_db[sim_id].error = str(e)

def _update_sim_progress(sim_id: str, progress: float):
    """Update simulation progress"""
    if sim_id in simulations_db:
        simulations_db[sim_id].progress = progress

@app.get("/api/simulations/{sim_id}")
async def get_simulation(sim_id: str):
    """Get simulation status and results"""
    if sim_id not in simulations_db:
        raise HTTPException(status_code=404, detail="Simulation not found")

    sim = simulations_db[sim_id]
    return {
        "id": sim_id,
        "status": sim.status.value,
        "progress": sim.progress,
        "aggregate_results": sim.aggregate_results,
        "error": sim.error
    }

@app.get("/api/simulations/{sim_id}/timeline")
async def get_simulation_timeline(sim_id: str, branch_id: int = 0):
    """Get timeline data for visualization"""
    if sim_id not in simulations_db:
        raise HTTPException(status_code=404, detail="Simulation not found")

    sim = simulations_db[sim_id]

    if not sim.branch_results or branch_id >= len(sim.branch_results):
        return {"timeline": []}

    branch = sim.branch_results[branch_id]

    timeline = []
    for snapshot in branch.daily_snapshots:
        timeline.append({
            "day": snapshot.day,
            "retention_rate": snapshot.metrics.get("retention_rate", 0),
            "churn_rate": snapshot.metrics.get("churn_rate", 0),
            "awareness": snapshot.metrics.get("awareness_avg", 0)
        })

    return {"timeline": timeline, "key_events": branch.key_events}


# ==================== TRACES API ====================

@app.get("/api/traces/{sim_id}/{option_id}")
async def get_trace(sim_id: str, option_id: str):
    """Get causal trace for a simulation"""
    trace_key = f"{sim_id}_{option_id}"

    if trace_key not in traces_db:
        raise HTTPException(status_code=404, detail="Trace not found")

    trace = traces_db[trace_key]
    return trace.model_dump()

@app.get("/api/traces/{sim_id}/{option_id}/narrative")
async def get_trace_narrative(sim_id: str, option_id: str):
    """Get narrative explanation of the trace"""
    trace_key = f"{sim_id}_{option_id}"

    if trace_key not in traces_db:
        raise HTTPException(status_code=404, detail="Trace not found")
    if sim_id not in simulations_db:
        raise HTTPException(status_code=404, detail="Simulation not found")

    trace = traces_db[trace_key]
    simulation = simulations_db[sim_id]

    narrative = trace_engine.generate_narrative(trace, simulation)

    return {"narrative": narrative}


# ==================== RECOMMENDATIONS API ====================

@app.post("/api/recommendations/generate")
async def generate_recommendation(decision_id: str):
    """Generate recommendation for a decision"""
    if decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")

    decision = decisions_db[decision_id]

    # Find all simulations for this decision
    decision_sims = {
        sim.config.option_id: sim
        for sim in simulations_db.values()
        if sim.config.decision_id == decision_id and sim.status == SimulationStatus.COMPLETED
    }

    if not decision_sims:
        raise HTTPException(status_code=400, detail="No completed simulations found")

    # Find all traces
    decision_traces = {
        option_id: traces_db.get(f"{sim.id}_{option_id}")
        for option_id, sim in decision_sims.items()
    }

    # Generate recommendation
    recommendation = decision_engine.generate_recommendation(
        decision_id=decision_id,
        simulations=decision_sims,
        traces={k: v for k, v in decision_traces.items() if v},
        options=[o.model_dump() for o in decision.options],
        constraints=[c.model_dump() for c in decision.constraints]
    )

    recommendations_db[decision_id] = recommendation

    return recommendation.model_dump()

@app.get("/api/recommendations/{decision_id}")
async def get_recommendation(decision_id: str):
    """Get recommendation for a decision"""
    if decision_id not in recommendations_db:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    return recommendations_db[decision_id].model_dump()


# ==================== AGENT CHAT API ====================

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Dict] = []

@app.post("/api/audiences/{audience_id}/agents/{agent_id}/chat")
async def chat_with_agent(audience_id: str, agent_id: str, request: ChatRequest):
    """Chat with a synthetic agent"""
    if audience_id not in audiences_db:
        raise HTTPException(status_code=404, detail="Audience not found")

    agents = audiences_db[audience_id]
    agent = next((a for a in agents if a.id == agent_id), None)

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    response = chat_engine.chat(
        agent=agent,
        user_message=request.message,
        conversation_history=request.conversation_history
    )

    return {
        "agent_id": agent_id,
        "response": response,
        "agent_name": agent.name,
        "agent_state": agent.state.value
    }

@app.get("/api/audiences/{audience_id}/agents/{agent_id}/journey")
async def get_agent_journey(audience_id: str, agent_id: str):
    """Get agent's decision journey"""
    if audience_id not in audiences_db:
        raise HTTPException(status_code=404, detail="Audience not found")

    agents = audiences_db[audience_id]
    agent = next((a for a in agents if a.id == agent_id), None)

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    journey = chat_engine.get_decision_journey(agent)

    return {"agent_id": agent_id, "journey": journey}


# ==================== PREDICTIONS API ====================

class PredictRequest(BaseModel):
    audience_id: str
    questions: List[Dict]

@app.post("/api/predictions/survey")
async def predict_survey_responses(request: PredictRequest):
    """Predict survey responses for an audience"""
    if request.audience_id not in audiences_db:
        raise HTTPException(status_code=404, detail="Audience not found")

    agents = audiences_db[request.audience_id]

    if not agents:
        raise HTTPException(status_code=400, detail="Audience is still generating")

    predictions = prediction_engine.predict_responses(
        agents=agents,
        questions=request.questions
    )

    return predictions


# ==================== BIAS API ====================

class BiasCheckRequest(BaseModel):
    question: str
    options: List[str] = []

class SuggestQuestionsRequest(BaseModel):
    survey_purpose: str
    existing_questions: List[str] = []
    audience_description: str

@app.post("/api/bias/check")
async def check_question_bias(request: BiasCheckRequest):
    """Check a question for bias"""
    result = bias_engine.check_bias(
        question=request.question,
        options=request.options
    )
    return result

@app.post("/api/suggestions/questions")
async def suggest_survey_questions(request: SuggestQuestionsRequest):
    """Suggest additional survey questions"""
    suggestions = bias_engine.suggest_questions(
        survey_purpose=request.survey_purpose,
        existing_questions=request.existing_questions,
        audience_description=request.audience_description
    )
    return {"suggestions": suggestions}


# ==================== TEMPLATES API ====================

@app.get("/api/templates/audiences")
async def list_audience_templates():
    """List audience templates"""
    templates = [
        {
            "id": "b2b_saas_buyers",
            "name": "B2B SaaS Buyers",
            "description": "Mid-market B2B software decision makers",
            "size": 500,
            "segments": ["IT Leaders", "Business Leaders", "End Users"]
        },
        {
            "id": "enterprise_tech",
            "name": "Enterprise Tech Buyers",
            "description": "Fortune 500 technology decision makers",
            "size": 200,
            "segments": ["CIO/CTO", "VP Engineering", "IT Directors"]
        },
        {
            "id": "smb_owners",
            "name": "SMB Business Owners",
            "description": "Small business owners and operators",
            "size": 1000,
            "segments": ["Solo Founders", "Small Teams", "Growth Stage"]
        }
    ]
    return {"templates": templates}

@app.get("/api/templates/scenarios")
async def list_scenario_templates():
    """List scenario templates"""
    templates = [
        {
            "id": "price_increase",
            "name": "Price Increase Impact",
            "description": "Analyze impact of pricing changes",
            "decision_type": "pricing"
        },
        {
            "id": "new_feature_launch",
            "name": "New Feature Launch",
            "description": "Test new feature adoption",
            "decision_type": "product"
        },
        {
            "id": "market_expansion",
            "name": "Market Expansion",
            "description": "Evaluate new market entry",
            "decision_type": "strategy"
        }
    ]
    return {"templates": templates}


# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

# PART 4: FRONTEND COMPONENTS

## 4.1 Core Types

### File: `src/lib/types.ts`
```typescript
// Core domain types

export interface Decision {
  id: string;
  title: string;
  description: string;
  options: Option[];
  constraints: Constraint[];
  success_criteria: SuccessCriteria;
  status: 'draft' | 'configured' | 'simulating' | 'completed';
  world_id?: string;
  audience_id?: string;
  simulation_id?: string;
  created_at: string;
  updated_at: string;
}

export interface Option {
  id: string;
  name: string;
  description: string;
  parameters: Record<string, number>;
}

export interface Constraint {
  id: string;
  description: string;
  metric: string;
  operator: '>=' | '<=' | '==';
  value: number;
}

export interface SuccessCriteria {
  primary_metric: string;
  optimization: 'maximize' | 'minimize';
  secondary_metrics: string[];
}

export interface World {
  id: string;
  name: string;
  description: string;
  total_addressable_market: number;
  market_growth_rate: number;
  segments: Segment[];
  competitors: Competitor[];
  your_product: Product;
  your_market_share: number;
}

export interface Segment {
  id: string;
  name: string;
  description: string;
  size_percent: number;
  characteristics: Record<string, unknown>;
  decision_cycle_days: number;
  price_sensitivity: number;
  brand_loyalty: number;
  risk_tolerance: number;
}

export interface Competitor {
  id: string;
  name: string;
  market_share: number;
  positioning: string;
  price_point: number;
  strengths: string[];
  weaknesses: string[];
  response_speed: 'fast' | 'medium' | 'slow';
  aggression: number;
}

export interface Product {
  id: string;
  name: string;
  current_price: number;
  features: Record<string, number>;
  positioning: string;
  strengths: string[];
  weaknesses: string[];
}

export interface Agent {
  id: string;
  name: string;
  age: number;
  occupation: string;
  income: number;
  location: string;
  education: string;
  segment_id: string;
  personality: Record<string, number>;
  values: string[];
  pain_points: string[];
  goals: string[];
  price_sensitivity: number;
  brand_loyalty: number;
  risk_tolerance: number;
  social_influence: number;
  decision_style: 'analytical' | 'intuitive' | 'social' | 'habitual';
  state: AgentState;
  awareness: number;
}

export type AgentState =
  | 'unaware'
  | 'aware'
  | 'considering'
  | 'evaluating'
  | 'decided'
  | 'churned'
  | 'retained';

export interface Audience {
  id: string;
  name: string;
  description: string;
  size: number;
  status: 'generating' | 'ready';
  agents?: Agent[];
}

export interface Simulation {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  aggregate_results?: AggregateResults;
  error?: string;
}

export interface AggregateResults {
  retention: {
    mean: number;
    std: number;
    p5: number;
    p25: number;
    p50: number;
    p75: number;
    p95: number;
  };
  churn: {
    mean: number;
    std: number;
    p5: number;
    p95: number;
  };
  outcome_distribution: {
    success: number;
    mixed: number;
    failure: number;
  };
  confidence: number;
}

export interface TimelinePoint {
  day: number;
  retention_rate: number;
  churn_rate: number;
  awareness: number;
}

export interface Trace {
  id: string;
  simulation_id: string;
  option_id: string;
  nodes: TraceNode[];
  edges: TraceEdge[];
  root_causes: string[];
  key_drivers: Sensitivity[];
  counterfactuals: Counterfactual[];
}

export interface TraceNode {
  id: string;
  type: 'event' | 'decision' | 'outcome' | 'factor';
  description: string;
  timestamp?: number;
  metrics: Record<string, number>;
  agent_count?: number;
}

export interface TraceEdge {
  source_id: string;
  target_id: string;
  weight: number;
  description: string;
}

export interface Sensitivity {
  factor: string;
  importance: number;
  direction: 'positive' | 'negative';
  description: string;
}

export interface Counterfactual {
  id: string;
  description: string;
  changed_factor: string;
  original_value: number;
  counterfactual_value: number;
  outcome_change: Record<string, number>;
}

export interface Recommendation {
  decision_id: string;
  recommended_option_id: string;
  recommended_option_name: string;
  confidence: number;
  expected_outcome: Record<string, number | string>;
  reasoning: string;
  comparison_to_alternatives: Array<{
    option_id: string;
    retention: string;
    why_not: string;
  }>;
  execution_plan: ActionItem[];
  contingencies: Contingency[];
  approval_gates: ApprovalGate[];
  key_risks: string[];
  monitoring_metrics: Array<{
    metric: string;
    frequency: string;
    threshold: string;
    owner: string;
  }>;
  executive_summary: string;
}

export interface ActionItem {
  id: string;
  action: string;
  description: string;
  owner: string;
  due_date: string;
  phase: string;
  dependencies: string[];
  approval_required: boolean;
}

export interface Contingency {
  id: string;
  trigger: string;
  detection: string;
  response: string;
  escalation: string;
  timeframe: string;
}

export interface ApprovalGate {
  id: string;
  condition: string;
  approver: string;
  threshold?: string;
}

export interface SurveyQuestion {
  id: string;
  text: string;
  type: 'single_choice' | 'rating_scale' | 'open_text';
  options?: string[];
  scale?: number;
}

export interface PredictionResult {
  question: string;
  type: string;
  distribution?: Record<string, number>;
  mean?: number;
  std?: number;
  themes?: Array<{ theme: string; percent: number }>;
  confidence: string;
}

export interface BiasCheckResult {
  has_bias: boolean;
  issues: Array<{
    type: string;
    description: string;
    severity: 'high' | 'medium' | 'low';
  }>;
  suggestion?: string;
}
```

## 4.2 API Client

### File: `src/lib/api.ts`
```typescript
import type {
  Decision,
  World,
  Audience,
  Agent,
  Simulation,
  Trace,
  Recommendation,
  PredictionResult,
  BiasCheckResult,
  SurveyQuestion,
  TimelinePoint,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

// ==================== DECISIONS ====================

export async function createDecision(data: {
  title: string;
  description: string;
  options: Array<{
    id: string;
    name: string;
    description: string;
    parameters: Record<string, number>;
  }>;
  constraints?: Array<{
    id: string;
    description: string;
    metric: string;
    operator: string;
    value: number;
  }>;
  success_criteria: {
    primary_metric: string;
    optimization: string;
    secondary_metrics?: string[];
  };
}): Promise<{ id: string; decision: Decision }> {
  return fetchAPI('/api/decisions', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getDecisions(): Promise<{ decisions: Decision[] }> {
  return fetchAPI('/api/decisions');
}

export async function getDecision(id: string): Promise<Decision> {
  return fetchAPI(`/api/decisions/${id}`);
}

// ==================== WORLDS ====================

export async function createWorld(data: Partial<World>): Promise<{ id: string; world: World }> {
  return fetchAPI('/api/worlds', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getWorlds(): Promise<{ worlds: World[] }> {
  return fetchAPI('/api/worlds');
}

export async function getWorld(id: string): Promise<World> {
  return fetchAPI(`/api/worlds/${id}`);
}

// ==================== AUDIENCES ====================

export async function createAudience(data: {
  name: string;
  description: string;
  size: number;
  world_id: string;
  segment_distribution: Record<string, number>;
}): Promise<{ id: string; status: string }> {
  return fetchAPI('/api/audiences', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getAudiences(): Promise<{ audiences: Audience[] }> {
  return fetchAPI('/api/audiences');
}

export async function getAudience(id: string, limit = 50): Promise<{
  id: string;
  total_size: number;
  agents: Agent[];
}> {
  return fetchAPI(`/api/audiences/${id}?limit=${limit}`);
}

export async function getAgent(audienceId: string, agentId: string): Promise<Agent> {
  return fetchAPI(`/api/audiences/${audienceId}/agents/${agentId}`);
}

// ==================== SIMULATIONS ====================

export async function runSimulation(data: {
  decision_id: string;
  world_id: string;
  audience_id: string;
  option_id: string;
  duration_days?: number;
  num_branches?: number;
  events?: Array<{
    id: string;
    day: number;
    type: string;
    description: string;
    parameters: Record<string, unknown>;
  }>;
}): Promise<{ id: string; status: string }> {
  return fetchAPI('/api/simulations', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getSimulation(id: string): Promise<Simulation> {
  return fetchAPI(`/api/simulations/${id}`);
}

export async function getSimulationTimeline(
  id: string,
  branchId = 0
): Promise<{ timeline: TimelinePoint[]; key_events: Array<{ day: number; event: string }> }> {
  return fetchAPI(`/api/simulations/${id}/timeline?branch_id=${branchId}`);
}

// ==================== TRACES ====================

export async function getTrace(simId: string, optionId: string): Promise<Trace> {
  return fetchAPI(`/api/traces/${simId}/${optionId}`);
}

export async function getTraceNarrative(
  simId: string,
  optionId: string
): Promise<{ narrative: string }> {
  return fetchAPI(`/api/traces/${simId}/${optionId}/narrative`);
}

// ==================== RECOMMENDATIONS ====================

export async function generateRecommendation(
  decisionId: string
): Promise<Recommendation> {
  return fetchAPI(`/api/recommendations/generate?decision_id=${decisionId}`, {
    method: 'POST',
  });
}

export async function getRecommendation(decisionId: string): Promise<Recommendation> {
  return fetchAPI(`/api/recommendations/${decisionId}`);
}

// ==================== AGENT CHAT ====================

export async function chatWithAgent(
  audienceId: string,
  agentId: string,
  message: string,
  history: Array<{ role: string; content: string }> = []
): Promise<{
  agent_id: string;
  response: string;
  agent_name: string;
  agent_state: string;
}> {
  return fetchAPI(`/api/audiences/${audienceId}/agents/${agentId}/chat`, {
    method: 'POST',
    body: JSON.stringify({
      message,
      conversation_history: history,
    }),
  });
}

export async function getAgentJourney(
  audienceId: string,
  agentId: string
): Promise<{
  agent_id: string;
  journey: Array<{
    timestamp: number;
    type: string;
    description?: string;
    choice?: string;
    reasoning?: string;
    confidence?: number;
  }>;
}> {
  return fetchAPI(`/api/audiences/${audienceId}/agents/${agentId}/journey`);
}

// ==================== PREDICTIONS ====================

export async function predictSurveyResponses(
  audienceId: string,
  questions: SurveyQuestion[]
): Promise<{
  overall_confidence: string;
  predictions: PredictionResult[];
}> {
  return fetchAPI('/api/predictions/survey', {
    method: 'POST',
    body: JSON.stringify({
      audience_id: audienceId,
      questions,
    }),
  });
}

// ==================== BIAS ====================

export async function checkBias(
  question: string,
  options: string[] = []
): Promise<BiasCheckResult> {
  return fetchAPI('/api/bias/check', {
    method: 'POST',
    body: JSON.stringify({ question, options }),
  });
}

export async function suggestQuestions(
  surveyPurpose: string,
  existingQuestions: string[],
  audienceDescription: string
): Promise<{
  suggestions: Array<{
    question: string;
    type: string;
    rationale: string;
    options?: string[];
  }>;
}> {
  return fetchAPI('/api/suggestions/questions', {
    method: 'POST',
    body: JSON.stringify({
      survey_purpose: surveyPurpose,
      existing_questions: existingQuestions,
      audience_description: audienceDescription,
    }),
  });
}

// ==================== TEMPLATES ====================

export async function getAudienceTemplates(): Promise<{
  templates: Array<{
    id: string;
    name: string;
    description: string;
    size: number;
    segments: string[];
  }>;
}> {
  return fetchAPI('/api/templates/audiences');
}

export async function getScenarioTemplates(): Promise<{
  templates: Array<{
    id: string;
    name: string;
    description: string;
    decision_type: string;
  }>;
}> {
  return fetchAPI('/api/templates/scenarios');
}
```

## 4.3 React Query Hooks

### File: `src/lib/hooks.ts`
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as api from './api';
import type { SurveyQuestion } from './types';

// ==================== DECISIONS ====================

export function useDecisions() {
  return useQuery({
    queryKey: ['decisions'],
    queryFn: () => api.getDecisions(),
  });
}

export function useDecision(id: string) {
  return useQuery({
    queryKey: ['decisions', id],
    queryFn: () => api.getDecision(id),
    enabled: !!id,
  });
}

export function useCreateDecision() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.createDecision,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['decisions'] });
    },
  });
}

// ==================== AUDIENCES ====================

export function useAudiences() {
  return useQuery({
    queryKey: ['audiences'],
    queryFn: () => api.getAudiences(),
  });
}

export function useAudience(id: string) {
  return useQuery({
    queryKey: ['audiences', id],
    queryFn: () => api.getAudience(id),
    enabled: !!id,
    refetchInterval: (data) =>
      data?.agents?.length === 0 ? 2000 : false,
  });
}

export function useCreateAudience() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.createAudience,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['audiences'] });
    },
  });
}

export function useAgent(audienceId: string, agentId: string) {
  return useQuery({
    queryKey: ['agents', audienceId, agentId],
    queryFn: () => api.getAgent(audienceId, agentId),
    enabled: !!audienceId && !!agentId,
  });
}

// ==================== SIMULATIONS ====================

export function useSimulation(id: string) {
  return useQuery({
    queryKey: ['simulations', id],
    queryFn: () => api.getSimulation(id),
    enabled: !!id,
    refetchInterval: (data) => {
      if (data?.status === 'running' || data?.status === 'pending') {
        return 1000; // Poll every second while running
      }
      return false;
    },
  });
}

export function useSimulationTimeline(id: string, branchId = 0) {
  return useQuery({
    queryKey: ['simulations', id, 'timeline', branchId],
    queryFn: () => api.getSimulationTimeline(id, branchId),
    enabled: !!id,
  });
}

export function useRunSimulation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.runSimulation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['simulations'] });
    },
  });
}

// ==================== TRACES ====================

export function useTrace(simId: string, optionId: string) {
  return useQuery({
    queryKey: ['traces', simId, optionId],
    queryFn: () => api.getTrace(simId, optionId),
    enabled: !!simId && !!optionId,
  });
}

export function useTraceNarrative(simId: string, optionId: string) {
  return useQuery({
    queryKey: ['traces', simId, optionId, 'narrative'],
    queryFn: () => api.getTraceNarrative(simId, optionId),
    enabled: !!simId && !!optionId,
  });
}

// ==================== RECOMMENDATIONS ====================

export function useRecommendation(decisionId: string) {
  return useQuery({
    queryKey: ['recommendations', decisionId],
    queryFn: () => api.getRecommendation(decisionId),
    enabled: !!decisionId,
  });
}

export function useGenerateRecommendation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.generateRecommendation,
    onSuccess: (data) => {
      queryClient.setQueryData(['recommendations', data.decision_id], data);
    },
  });
}

// ==================== AGENT CHAT ====================

export function useChatWithAgent() {
  return useMutation({
    mutationFn: ({
      audienceId,
      agentId,
      message,
      history,
    }: {
      audienceId: string;
      agentId: string;
      message: string;
      history?: Array<{ role: string; content: string }>;
    }) => api.chatWithAgent(audienceId, agentId, message, history),
  });
}

export function useAgentJourney(audienceId: string, agentId: string) {
  return useQuery({
    queryKey: ['agents', audienceId, agentId, 'journey'],
    queryFn: () => api.getAgentJourney(audienceId, agentId),
    enabled: !!audienceId && !!agentId,
  });
}

// ==================== PREDICTIONS ====================

export function usePredictSurvey() {
  return useMutation({
    mutationFn: ({
      audienceId,
      questions,
    }: {
      audienceId: string;
      questions: SurveyQuestion[];
    }) => api.predictSurveyResponses(audienceId, questions),
  });
}

// ==================== BIAS ====================

export function useCheckBias() {
  return useMutation({
    mutationFn: ({
      question,
      options,
    }: {
      question: string;
      options?: string[];
    }) => api.checkBias(question, options),
  });
}

export function useSuggestQuestions() {
  return useMutation({
    mutationFn: ({
      surveyPurpose,
      existingQuestions,
      audienceDescription,
    }: {
      surveyPurpose: string;
      existingQuestions: string[];
      audienceDescription: string;
    }) => api.suggestQuestions(surveyPurpose, existingQuestions, audienceDescription),
  });
}

// ==================== TEMPLATES ====================

export function useAudienceTemplates() {
  return useQuery({
    queryKey: ['templates', 'audiences'],
    queryFn: () => api.getAudienceTemplates(),
  });
}

export function useScenarioTemplates() {
  return useQuery({
    queryKey: ['templates', 'scenarios'],
    queryFn: () => api.getScenarioTemplates(),
  });
}
```

---

## 4.4 Core Components (Summary)

Due to length, here are the key component signatures. Full implementations follow the Figma designs.

### Survey Builder Components

```typescript
// src/components/survey/QuestionBuilder.tsx
interface QuestionBuilderProps {
  questions: SurveyQuestion[];
  onQuestionsChange: (questions: SurveyQuestion[]) => void;
  onBiasCheck: (question: SurveyQuestion) => void;
}

// src/components/survey/SurveyPreview.tsx
interface SurveyPreviewProps {
  questions: SurveyQuestion[];
  audienceId?: string;
}

// src/components/survey/ResponsePredictions.tsx
interface ResponsePredictionsProps {
  predictions: PredictionResult[];
  isLoading: boolean;
}

// src/components/survey/BiasWarning.tsx
interface BiasWarningProps {
  result: BiasCheckResult;
  onApplySuggestion: (suggestion: string) => void;
}

// src/components/survey/ConfidenceBadge.tsx
interface ConfidenceBadgeProps {
  level: 'high' | 'medium' | 'low';
}

// src/components/survey/AISuggestion.tsx
interface AISuggestionProps {
  suggestion: {
    question: string;
    type: string;
    rationale: string;
    options?: string[];
  };
  onAccept: () => void;
  onDismiss: () => void;
}
```

### Audience Components

```typescript
// src/components/audience/AudienceList.tsx
interface AudienceListProps {
  audiences: Audience[];
  selectedId?: string;
  onSelect: (id: string) => void;
}

// src/components/audience/AudienceDetail.tsx
interface AudienceDetailProps {
  audience: Audience;
  agents: Agent[];
  onAgentClick: (agentId: string) => void;
}

// src/components/audience/CreateAudienceForm.tsx
interface CreateAudienceFormProps {
  worldId: string;
  segments: Segment[];
  onSubmit: (data: CreateAudienceData) => void;
}

// src/components/audience/AgentCard.tsx
interface AgentCardProps {
  agent: Agent;
  onClick: () => void;
}

// src/components/audience/AgentChat.tsx
interface AgentChatProps {
  audienceId: string;
  agent: Agent;
  onClose: () => void;
}
```

### Simulation & Results Components

```typescript
// src/components/simulation/SimulationProgress.tsx
interface SimulationProgressProps {
  simulation: Simulation;
}

// src/components/simulation/TimelineChart.tsx
interface TimelineChartProps {
  timeline: TimelinePoint[];
  keyEvents: Array<{ day: number; event: string }>;
}

// src/components/simulation/OutcomeDistribution.tsx
interface OutcomeDistributionProps {
  distribution: {
    success: number;
    mixed: number;
    failure: number;
  };
}

// src/components/simulation/ConfidenceInterval.tsx
interface ConfidenceIntervalProps {
  metric: string;
  p5: number;
  p25: number;
  p50: number;
  p75: number;
  p95: number;
}
```

### Trace & Decision Components

```typescript
// src/components/trace/TraceViewer.tsx
interface TraceViewerProps {
  trace: Trace;
  onNodeClick: (nodeId: string) => void;
}

// src/components/trace/CausalChain.tsx
interface CausalChainProps {
  nodes: TraceNode[];
  edges: TraceEdge[];
}

// src/components/trace/CounterfactualCard.tsx
interface CounterfactualCardProps {
  counterfactual: Counterfactual;
}

// src/components/decision/RecommendationCard.tsx
interface RecommendationCardProps {
  recommendation: Recommendation;
}

// src/components/decision/ExecutionPlan.tsx
interface ExecutionPlanProps {
  actions: ActionItem[];
  contingencies: Contingency[];
  approvalGates: ApprovalGate[];
}

// src/components/decision/RiskMatrix.tsx
interface RiskMatrixProps {
  risks: string[];
  contingencies: Contingency[];
}
```

---

# PART 5: PAGE STRUCTURE

## 5.1 Page Routes

```
src/app/
├── (dashboard)/
│   ├── layout.tsx           # Dashboard shell with sidebar
│   ├── page.tsx             # Home/Overview
│   │
│   ├── projects/
│   │   ├── page.tsx         # Projects list (Screen 1)
│   │   ├── new/
│   │   │   └── page.tsx     # Survey Builder (Screens 7-9)
│   │   └── [id]/
│   │       ├── page.tsx     # Project detail
│   │       ├── simulate/
│   │       │   └── page.tsx # Run simulation
│   │       └── results/
│   │           └── page.tsx # Results dashboard (Screen 8)
│   │
│   ├── audiences/
│   │   ├── page.tsx         # Audiences list (Screen 2)
│   │   ├── new/
│   │   │   └── page.tsx     # Create audience (Screens 3-5)
│   │   └── [id]/
│   │       └── page.tsx     # Audience detail
│   │
│   ├── decisions/
│   │   ├── page.tsx         # Decisions list
│   │   ├── new/
│   │   │   └── page.tsx     # Create decision
│   │   └── [id]/
│   │       ├── page.tsx     # Decision detail
│   │       └── trace/
│   │           └── page.tsx # Causal trace viewer
│   │
│   └── templates/
│       └── page.tsx         # Templates library (Screen 6)
│
├── api/                     # Next.js API routes (if needed)
├── layout.tsx               # Root layout
└── page.tsx                 # Landing/login
```

## 5.2 Dashboard Layout

### File: `src/app/(dashboard)/layout.tsx`
```typescript
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Users,
  FolderKanban,
  FileStack,
  ChevronLeft,
  ChevronRight,
  Settings,
} from 'lucide-react';

const navigation = [
  { name: 'Overview', href: '/', icon: LayoutDashboard },
  { name: 'Projects', href: '/projects', icon: FolderKanban },
  { name: 'Audiences', href: '/audiences', icon: Users },
  { name: 'Templates', href: '/templates', icon: FileStack },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside
        className={cn(
          'flex flex-col bg-white border-r border-gray-200 transition-all duration-300',
          collapsed ? 'w-16' : 'w-64'
        )}
      >
        {/* Logo */}
        <div className="flex items-center h-16 px-4 border-b border-gray-200">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">R</span>
            </div>
            {!collapsed && (
              <span className="font-semibold text-gray-900">RLTX Populous</span>
            )}
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href ||
              (item.href !== '/' && pathname.startsWith(item.href));

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-indigo-50 text-indigo-600'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                )}
              >
                <item.icon className="w-5 h-5" />
                {!collapsed && <span>{item.name}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Collapse toggle */}
        <div className="p-2 border-t border-gray-200">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex items-center justify-center w-full p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg"
          >
            {collapsed ? (
              <ChevronRight className="w-5 h-5" />
            ) : (
              <ChevronLeft className="w-5 h-5" />
            )}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}
```

---

# PART 6: BUILD SEQUENCE

## Phase 1: Foundation (Backend Core)
**Files to create first - everything else depends on these**

1. **Models** (in order):
   - `backend/models/decision.py`
   - `backend/models/world.py`
   - `backend/models/agent.py`
   - `backend/models/simulation.py`
   - `backend/models/trace.py`
   - `backend/models/action.py`

2. **Core Engines** (in order):
   - `backend/engine/agent_engine.py` - Stanford architecture
   - `backend/engine/network_engine.py` - Social network
   - `backend/engine/simulation_engine.py` - Monte Carlo (depends on agent + network)

3. **API Skeleton**:
   - `backend/api/main.py` - Basic routes, health check

## Phase 2: Intelligence Layer (Backend AI)
**The AI-powered engines that provide insights**

4. **Analysis Engines**:
   - `backend/engine/trace_engine.py` - Causal analysis
   - `backend/engine/decision_engine.py` - Recommendations

5. **Interaction Engines**:
   - `backend/engine/chat_engine.py` - Agent interviews
   - `backend/engine/prediction_engine.py` - Survey predictions
   - `backend/engine/bias_engine.py` - Bias detection

6. **Complete API**:
   - Add all remaining routes to `main.py`
   - Test all endpoints with curl/Postman

## Phase 3: Frontend Foundation
**Core frontend infrastructure**

7. **Types & API Client**:
   - `src/lib/types.ts`
   - `src/lib/api.ts`
   - `src/lib/hooks.ts`

8. **Layout & Navigation**:
   - `src/app/(dashboard)/layout.tsx`
   - Basic page shells for all routes

## Phase 4: Survey Builder (Core Feature)
**The main value prop - where users spend most time**

9. **Survey Components**:
   - `QuestionBuilder.tsx`
   - `SurveyPreview.tsx`
   - `ResponsePredictions.tsx`
   - `BiasWarning.tsx`
   - `ConfidenceBadge.tsx`
   - `AISuggestion.tsx`

10. **Survey Page**:
    - `src/app/(dashboard)/projects/new/page.tsx`
    - Connect all components
    - Real-time prediction updates

## Phase 5: Audiences
**Synthetic population management**

11. **Audience Components**:
    - `AudienceList.tsx`
    - `AudienceDetail.tsx`
    - `CreateAudienceForm.tsx`
    - `AgentCard.tsx`
    - `AgentChat.tsx` (modal)

12. **Audience Pages**:
    - `src/app/(dashboard)/audiences/page.tsx`
    - `src/app/(dashboard)/audiences/new/page.tsx`
    - `src/app/(dashboard)/audiences/[id]/page.tsx`

## Phase 6: Simulation & Results
**Where the magic happens**

13. **Simulation Components**:
    - `SimulationProgress.tsx`
    - `TimelineChart.tsx` (Recharts)
    - `OutcomeDistribution.tsx`
    - `ConfidenceInterval.tsx`

14. **Trace Components**:
    - `TraceViewer.tsx` (D3 or React Flow)
    - `CausalChain.tsx`
    - `CounterfactualCard.tsx`

15. **Results Page**:
    - `src/app/(dashboard)/projects/[id]/results/page.tsx`

## Phase 7: Decision Layer
**The actionable output**

16. **Decision Components**:
    - `RecommendationCard.tsx`
    - `ExecutionPlan.tsx`
    - `ContingencyTable.tsx`
    - `RiskMatrix.tsx`
    - `ApprovalGates.tsx`

17. **Decision Pages**:
    - `src/app/(dashboard)/decisions/[id]/page.tsx`
    - `src/app/(dashboard)/decisions/[id]/trace/page.tsx`

## Phase 8: Polish & Templates
**Final touches**

18. **Templates**:
    - `src/app/(dashboard)/templates/page.tsx`
    - Pre-built audience templates
    - Scenario templates

19. **Projects Dashboard**:
    - `src/app/(dashboard)/projects/page.tsx`
    - Project cards with status

20. **Error & Loading States**:
    - Skeleton loaders
    - Error boundaries
    - Empty states

---

# PART 7: INTEGRATION CHECKLIST

## Frontend → Backend Integration Points

| Frontend Component | API Endpoint | Data Flow |
|-------------------|--------------|-----------|
| QuestionBuilder | POST /api/bias/check | Real-time bias check on typing |
| QuestionBuilder | POST /api/suggestions/questions | AI question suggestions |
| ResponsePredictions | POST /api/predictions/survey | Debounced predictions (300ms) |
| CreateAudienceForm | POST /api/audiences | Trigger generation |
| AudienceDetail | GET /api/audiences/{id} | Poll while generating |
| AgentChat | POST /api/.../agents/{id}/chat | Stream responses |
| SimulationProgress | GET /api/simulations/{id} | Poll every 1s while running |
| TimelineChart | GET /api/simulations/{id}/timeline | Load on completion |
| TraceViewer | GET /api/traces/{simId}/{optionId} | Load on demand |
| RecommendationCard | POST /api/recommendations/generate | Trigger on completion |

## Key UX Flows

### 1. Survey Creation Flow
```
User types question
    → Debounce 300ms
    → POST /api/bias/check
    → Show BiasWarning if issues
    → POST /api/predictions/survey
    → Show ResponsePredictions
```

### 2. Audience Generation Flow
```
User fills form
    → POST /api/audiences
    → Show progress modal
    → Poll GET /api/audiences/{id} every 2s
    → On ready: Show AudienceDetail
```

### 3. Simulation Flow
```
User clicks "Run Simulation"
    → POST /api/simulations
    → Show SimulationProgress
    → Poll GET /api/simulations/{id} every 1s
    → On complete:
        → GET /api/simulations/{id}/timeline
        → GET /api/traces/{simId}/{optionId}
        → POST /api/recommendations/generate
    → Navigate to Results page
```

### 4. Agent Interview Flow
```
User clicks agent card
    → Open AgentChat modal
    → GET /api/.../agents/{id}/journey (show context)
    → User sends message
    → POST /api/.../agents/{id}/chat
    → Stream response
```

---

# PART 8: DEPLOYMENT

## Railway Configuration

### File: `railway.toml`
```toml
[build]
builder = "nixpacks"
buildCommand = "cd populous-frontend && npm install && npm run build"

[deploy]
startCommand = "cd rltx-populous && python -m backend.api.main"
healthcheckPath = "/health"
healthcheckTimeout = 300

[variables]
PYTHONPATH = "/app/rltx-populous"
```

### Environment Variables
```
ANTHROPIC_API_KEY=sk-ant-...
NEXT_PUBLIC_API_URL=https://your-app.railway.app
```

## Dockerfile (Alternative)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Python deps
COPY rltx-populous/requirements.txt .
RUN pip install -r requirements.txt

# Copy backend
COPY rltx-populous/ ./rltx-populous/

# Install Node for frontend build
RUN apt-get update && apt-get install -y nodejs npm

# Build frontend
COPY populous-frontend/ ./populous-frontend/
RUN cd populous-frontend && npm install && npm run build

EXPOSE 8000

CMD ["uvicorn", "rltx-populous.backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

# SUMMARY

This plan provides:
1. **6 Pydantic models** - Complete data layer
2. **7 Backend engines** - Full intelligence layer
3. **1 comprehensive API** - All routes in single file
4. **Complete TypeScript types** - Full type safety
5. **API client + React Query hooks** - Modern data fetching
6. **Component signatures** - Ready to implement
7. **8 page routes** - Complete user journey
8. **Phased build sequence** - Dependencies respected
9. **Integration checklist** - Nothing missed
10. **Deployment config** - Production ready

**Total files to create:** ~35 files
**Estimated implementation:** Build each file in sequence per Phase

This is the surgical plan. Each file is self-contained and can be built incrementally.
