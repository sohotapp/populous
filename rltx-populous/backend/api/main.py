"""
FastAPI application - main entry point.
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables - find .env relative to this file
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path)

# Fallback: manual loading if dotenv fails
if not os.environ.get("ANTHROPIC_API_KEY") and _env_path.exists():
    with open(_env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value

from backend.models import Scenario, Strategy, SimulationResults, Agent
from backend.engine import SimulationRunner, DecisionEngine
from backend.data.presets.b2b_saas import get_saas_launch_scenario, get_demo_strategies

# Import new API routers for Populous features
from backend.api.projects import router as projects_router
from backend.api.audiences import router as audiences_router
from backend.api.surveys import router as surveys_router
from backend.api.decision_intelligence import router as di_router
from backend.api.startups import router as startups_router
from backend.api.nodes import router as nodes_router
from backend.api.graph import router as graph_router


# In-memory storage (replace with database for production)
scenarios_db: Dict[str, Scenario] = {}
strategies_db: Dict[str, Strategy] = {}
results_db: Dict[str, SimulationResults] = {}
agents_db: Dict[str, List[Agent]] = {}  # simulation_id -> agents


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load presets on startup"""
    scenario = get_saas_launch_scenario()
    scenarios_db[scenario.id] = scenario

    for strategy in get_demo_strategies():
        strategies_db[strategy.id] = strategy

    yield  # App runs here

    # Cleanup on shutdown (if needed)


app = FastAPI(
    title="RLTX Populous API",
    description="Decision Intelligence Simulation Platform",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Populous feature routers
app.include_router(projects_router)
app.include_router(audiences_router)
app.include_router(surveys_router)
app.include_router(di_router)  # Decision Intelligence routes at /api/di/*
app.include_router(startups_router)  # Startup prediction routes at /api/startups/*
app.include_router(nodes_router)  # Node-based pipeline routes at /api/nodes/*
app.include_router(graph_router)  # Graph execution engine at /api/graph/*


@app.get("/")
def root():
    """API root"""
    return {
        "name": "Populous",
        "tagline": "There's a future where you win; we engineer that for you.",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


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

    try:
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

    except Exception as e:
        return f"Simulation completed. Mean conversion: {results.mean_conversion*100:.1f}%"


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

    try:
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

    except Exception:
        winner = max(comparisons, key=lambda c: c.mean_conversion)
        return f"{winner.strategy_name} has the highest mean conversion at {winner.mean_conversion*100:.1f}%."


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

    try:
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
        segment = agent_id.split("_")[0] if "_" in agent_id else "mid_market"
        system = f"""You are a B2B buyer being interviewed about your software purchase decision.

You are a {segment} segment buyer evaluating project management tools.

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

    except Exception as e:
        return AgentChatResponse(
            response=f"Agent chat temporarily unavailable. Error: {str(e)}",
            agent_stage="Unknown",
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
