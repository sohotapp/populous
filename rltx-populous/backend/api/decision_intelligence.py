"""
Decision Intelligence API Routes
Stanford agents, temporal simulation, causal traces, recommendations
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import uuid
import os
import numpy as np

# Import new models
from backend.models.decision import Decision, DecisionStatus, Option, Constraint, SuccessCriteria
from backend.models.world import World, Segment, Competitor, Product
from backend.models.generative_agent import GenerativeAgent, AgentState, Memory, Relationship
from backend.models.simulation import TemporalSimulation, SimulationConfig, SimulationStatus
from backend.models.trace import Trace
from backend.models.action import Recommendation

router = APIRouter(prefix="/api/di", tags=["Decision Intelligence"])

# In-memory storage
decisions_db: Dict[str, Decision] = {}
worlds_db: Dict[str, World] = {}
audiences_db: Dict[str, List[GenerativeAgent]] = {}
simulations_db: Dict[str, TemporalSimulation] = {}
traces_db: Dict[str, Trace] = {}
recommendations_db: Dict[str, Recommendation] = {}


# ==================== DECISIONS ====================

class CreateDecisionRequest(BaseModel):
    title: str
    description: str
    options: List[Dict]
    constraints: List[Dict] = []
    success_criteria: Dict


@router.post("/decisions")
async def create_decision(request: CreateDecisionRequest):
    """Create a new decision"""
    decision_id = str(uuid.uuid4())

    options = [Option(id=opt.get("id", str(uuid.uuid4())), **{k: v for k, v in opt.items() if k != "id"}) for opt in request.options]
    constraints = [Constraint(id=c.get("id", str(uuid.uuid4())), **{k: v for k, v in c.items() if k != "id"}) for c in request.constraints]
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


@router.get("/decisions")
async def list_decisions():
    """List all decisions"""
    return {"decisions": [d.model_dump() for d in decisions_db.values()]}


@router.get("/decisions/{decision_id}")
async def get_decision(decision_id: str):
    """Get a specific decision"""
    if decision_id not in decisions_db:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decisions_db[decision_id].model_dump()


# ==================== WORLDS ====================

class CreateWorldRequest(BaseModel):
    name: str
    description: str
    total_addressable_market: int
    market_growth_rate: float
    segments: List[Dict]
    competitors: List[Dict]
    your_product: Dict
    your_market_share: float


@router.post("/worlds")
async def create_world(request: CreateWorldRequest):
    """Create a market world"""
    world_id = str(uuid.uuid4())

    world = World(
        id=world_id,
        name=request.name,
        description=request.description,
        total_addressable_market=request.total_addressable_market,
        market_growth_rate=request.market_growth_rate,
        segments=[Segment(id=s.get("id", str(uuid.uuid4())), **{k: v for k, v in s.items() if k != "id"}) for s in request.segments],
        competitors=[Competitor(id=c.get("id", str(uuid.uuid4())), **{k: v for k, v in c.items() if k != "id"}) for c in request.competitors],
        your_product=Product(id=request.your_product.get("id", str(uuid.uuid4())), **{k: v for k, v in request.your_product.items() if k != "id"}),
        your_market_share=request.your_market_share,
        created_at=datetime.now()
    )

    worlds_db[world_id] = world
    return {"id": world_id, "world": world.model_dump()}


@router.get("/worlds")
async def list_worlds():
    """List all worlds"""
    return {"worlds": [w.model_dump() for w in worlds_db.values()]}


@router.get("/worlds/{world_id}")
async def get_world(world_id: str):
    """Get a specific world"""
    if world_id not in worlds_db:
        raise HTTPException(status_code=404, detail="World not found")
    return worlds_db[world_id].model_dump()


# ==================== AUDIENCES ====================

class CreateAudienceRequest(BaseModel):
    name: str
    description: str
    size: int
    world_id: str
    segment_distribution: Dict[str, float] = {}


@router.post("/audiences")
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

    audiences_db[audience_id] = []

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
            agent = _generate_single_agent(segment, i, audience_id)
            agents.append(agent)

    # Build social network
    _build_network(agents)

    audiences_db[audience_id] = agents


def _generate_single_agent(segment: Segment, index: int, audience_id: str) -> GenerativeAgent:
    """Generate a single agent"""
    names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Quinn", "Avery"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    occupations = ["Software Engineer", "Marketing Manager", "CFO", "Product Manager",
                   "Sales Director", "Analyst", "Consultant", "VP Engineering"]
    cities = ["San Francisco", "New York", "Austin", "Seattle", "Boston", "Chicago"]

    return GenerativeAgent(
        id=f"agent_{audience_id[:8]}_{index}",
        name=f"{np.random.choice(names)} {np.random.choice(last_names)}",
        age=int(np.random.randint(25, 65)),
        occupation=np.random.choice(occupations),
        income=float(np.random.uniform(80000, 250000)),
        location=np.random.choice(cities),
        education=np.random.choice(["Bachelor's", "Master's", "MBA", "PhD"]),
        segment_id=segment.id,
        personality={
            "openness": float(np.random.beta(5, 5)),
            "conscientiousness": float(np.random.beta(5, 5)),
            "extraversion": float(np.random.beta(5, 5)),
            "agreeableness": float(np.random.beta(5, 5)),
            "neuroticism": float(np.random.beta(5, 5))
        },
        values=list(np.random.choice(["efficiency", "innovation", "reliability", "growth", "quality"], size=3, replace=False)),
        pain_points=list(np.random.choice(["manual processes", "lack of insights", "slow reporting", "integration issues"], size=2, replace=False)),
        goals=list(np.random.choice(["reduce costs", "increase efficiency", "better decisions", "faster growth"], size=2, replace=False)),
        price_sensitivity=float(segment.price_sensitivity + np.random.uniform(-0.2, 0.2)),
        brand_loyalty=float(segment.brand_loyalty + np.random.uniform(-0.2, 0.2)),
        risk_tolerance=float(segment.risk_tolerance + np.random.uniform(-0.2, 0.2)),
        social_influence=float(np.random.beta(2, 5)),
        decision_style=np.random.choice(["analytical", "intuitive", "social", "habitual"]),
        utility_weights={
            "price": float(np.random.uniform(0.2, 0.4)),
            "quality": float(np.random.uniform(0.2, 0.4)),
            "convenience": float(np.random.uniform(0.1, 0.3)),
            "status": float(np.random.uniform(0.0, 0.2))
        }
    )


def _build_network(agents: List[GenerativeAgent], connectivity: float = 0.05):
    """Build social network connections"""
    n = len(agents)

    for i, agent in enumerate(agents):
        num_connections = int(n * connectivity)
        if num_connections > 0 and n > 1:
            connection_indices = np.random.choice(
                [j for j in range(n) if j != i],
                size=min(num_connections, n - 1),
                replace=False
            )

            for j in connection_indices:
                other = agents[j]
                same_segment = agent.segment_id == other.segment_id
                trust = float(np.random.uniform(0.5, 0.9) if same_segment else np.random.uniform(0.2, 0.5))

                agent.relationships.append(Relationship(
                    other_agent_id=other.id,
                    relationship_type="colleague" if same_segment else "acquaintance",
                    trust_level=trust,
                    influence_weight=trust * agent.social_influence
                ))


@router.get("/audiences")
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


@router.get("/audiences/{audience_id}")
async def get_audience(audience_id: str, limit: int = 50):
    """Get audience details"""
    if audience_id not in audiences_db:
        raise HTTPException(status_code=404, detail="Audience not found")

    agents = audiences_db[audience_id]
    return {
        "id": audience_id,
        "total_size": len(agents),
        "status": "ready" if agents else "generating",
        "agents": [a.model_dump() for a in agents[:limit]]
    }


# ==================== AGENT CHAT ====================

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Dict] = []


@router.post("/audiences/{audience_id}/agents/{agent_id}/chat")
async def chat_with_agent(audience_id: str, agent_id: str, request: ChatRequest):
    """Chat with a synthetic agent"""
    if audience_id not in audiences_db:
        raise HTTPException(status_code=404, detail="Audience not found")

    agents = audiences_db[audience_id]
    agent = next((a for a in agents if a.id == agent_id), None)

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Use chat engine if available
    try:
        from anthropic import Anthropic
        from backend.engine.chat_engine import ChatEngine

        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        chat_engine = ChatEngine(client)

        response = chat_engine.chat(
            agent=agent,
            user_message=request.message,
            conversation_history=request.conversation_history
        )

        return {
            "agent_id": agent_id,
            "response": response,
            "agent_name": agent.name,
            "agent_state": agent.state
        }
    except Exception as e:
        return {
            "agent_id": agent_id,
            "response": f"I'm {agent.name}, a {agent.occupation}. [Chat engine unavailable: {str(e)}]",
            "agent_name": agent.name,
            "agent_state": agent.state
        }


# ==================== PREDICTIONS ====================

class PredictRequest(BaseModel):
    audience_id: str
    questions: List[Dict]


@router.post("/predictions/survey")
async def predict_survey_responses(request: PredictRequest):
    """Predict survey responses"""
    if request.audience_id not in audiences_db:
        raise HTTPException(status_code=404, detail="Audience not found")

    agents = audiences_db[request.audience_id]

    if not agents:
        raise HTTPException(status_code=400, detail="Audience is still generating")

    try:
        from anthropic import Anthropic
        from backend.engine.prediction_engine import PredictionEngine

        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        prediction_engine = PredictionEngine(client)

        predictions = prediction_engine.predict_responses(
            agents=agents,
            questions=request.questions
        )

        return predictions
    except Exception as e:
        return {
            "overall_confidence": "low",
            "predictions": [],
            "error": str(e)
        }


# ==================== BIAS ====================

class BiasCheckRequest(BaseModel):
    question: str
    options: List[str] = []


@router.post("/bias/check")
async def check_question_bias(request: BiasCheckRequest):
    """Check a question for bias"""
    try:
        from anthropic import Anthropic
        from backend.engine.bias_engine import BiasEngine

        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        bias_engine = BiasEngine(client)

        result = bias_engine.check_bias(
            question=request.question,
            options=request.options
        )
        return result
    except Exception as e:
        # Fall back to rule-based only
        from backend.engine.bias_engine import BiasEngine
        bias_engine = BiasEngine(None)
        return bias_engine.check_bias(request.question, request.options)


# ==================== TEMPLATES ====================

@router.get("/templates/audiences")
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


@router.get("/templates/scenarios")
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


# ==================== RESEARCH ====================

class ResearchRequest(BaseModel):
    query: str
    depth: str = "deep"  # quick, standard, deep


@router.post("/research")
async def research_company(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Research a company using Exa API"""
    try:
        from backend.engine.research_engine import ResearchEngine
        from backend.db.supabase import get_database

        research_id = str(uuid.uuid4())
        engine = ResearchEngine()
        db = get_database()

        # Run research (this can take a while for deep research)
        result = await engine.research_company(request.query, request.depth)

        # Save to database
        await db.save_research_result(result)

        return {
            "id": result.id,
            "query": result.query,
            "target_company": result.target_company.model_dump() if result.target_company else None,
            "competitors": [c.model_dump() for c in result.competitors],
            "market": result.market.model_dump() if result.market else None,
            "sources_consulted": result.sources_consulted,
            "overall_confidence": result.overall_confidence,
            "sources": result.target_company.research_sources[:10] if result.target_company else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")


@router.get("/research/{research_id}")
async def get_research_result(research_id: str):
    """Get a research result by ID"""
    from backend.db.supabase import get_database
    db = get_database()

    result = await db.get_research_result(research_id)
    if not result:
        raise HTTPException(status_code=404, detail="Research result not found")

    return result.model_dump()


# ==================== COMPETITOR ANALYSIS ====================

class CompetitorAnalysisRequest(BaseModel):
    your_move: Dict
    competitor_ids: List[str] = []
    research_id: Optional[str] = None


@router.post("/competitors/analyze")
async def analyze_competitors(request: CompetitorAnalysisRequest):
    """Game-theoretic competitor response analysis"""
    try:
        from backend.engine.competitor_engine import CompetitorEngine
        from backend.engine.research_engine import ResearchEngine
        from backend.db.supabase import get_database

        engine = CompetitorEngine()
        db = get_database()

        # Get competitors from research result if provided
        competitors = []
        if request.research_id:
            result = await db.get_research_result(request.research_id)
            if result:
                competitor_agents = engine.generate_competitor_agents(result.competitors)
                competitors = competitor_agents

        if not competitors:
            raise HTTPException(status_code=400, detail="No competitors to analyze. Provide research_id.")

        # Run game-theoretic analysis
        analysis = engine.predict_responses(
            your_move=request.your_move,
            competitors=competitors
        )

        return {
            "your_move": analysis.your_move,
            "competitor_responses": analysis.competitor_responses,
            "most_likely_scenario": analysis.most_likely_scenario,
            "scenario_probabilities": analysis.scenario_probabilities,
            "nash_equilibrium": analysis.nash_equilibrium,
            "recommended_strategies": analysis.recommended_counter_strategies,
            "risk_factors": analysis.risk_factors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/competitors/simulate")
async def simulate_competitive_game(request: Dict):
    """Simulate multiple rounds of competitive game"""
    try:
        from backend.engine.competitor_engine import CompetitorEngine
        from backend.db.supabase import get_database

        engine = CompetitorEngine()
        db = get_database()

        research_id = request.get("research_id")
        your_moves = request.get("moves", [])
        rounds = request.get("rounds", 3)

        if not research_id:
            raise HTTPException(status_code=400, detail="research_id required")

        result = await db.get_research_result(research_id)
        if not result:
            raise HTTPException(status_code=404, detail="Research not found")

        competitor_agents = engine.generate_competitor_agents(result.competitors)

        history = engine.simulate_game(
            your_moves=your_moves,
            competitors=competitor_agents,
            rounds=rounds
        )

        return {"game_history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


# ==================== SCENARIO BRANCHING ====================

class ScenarioBranchRequest(BaseModel):
    decision_id: str
    your_move: Dict
    company_name: str
    competitor_names: List[str] = []
    max_depth: int = 4
    num_simulations: int = 100


@router.post("/scenarios/branch")
async def generate_scenario_branches(request: ScenarioBranchRequest):
    """Generate scenario branching tree"""
    try:
        from backend.engine.scenario_engine import ScenarioEngine, ScenarioBranchInput
        from backend.engine.competitor_engine import CompetitorEngine
        from backend.db.supabase import get_database

        scenario_engine = ScenarioEngine()
        competitor_engine = CompetitorEngine()
        db = get_database()

        # Build input
        branch_input = ScenarioBranchInput(
            decision_id=request.decision_id,
            your_move=request.your_move,
            company_name=request.company_name,
            competitor_names=request.competitor_names,
            max_depth=request.max_depth,
            num_simulations=request.num_simulations
        )

        # Get decision and any associated research
        decision = await db.get_decision(request.decision_id)
        competitors = []

        # Generate scenario tree
        tree = await scenario_engine.generate_scenario_tree(
            input_data=branch_input,
            competitors=competitors
        )

        # Generate summary
        summary = scenario_engine.generate_summary(
            tree=tree,
            decision_title=decision.title if decision else "Decision"
        )

        return {
            "tree_id": tree.id,
            "headline": summary.headline,
            "outcome_probabilities": tree.outcome_probabilities,
            "expected_metrics": tree.expected_metrics.model_dump(),
            "total_paths": tree.total_paths,
            "total_nodes": tree.total_nodes,
            "best_case": summary.best_case,
            "worst_case": summary.worst_case,
            "most_likely": summary.most_likely,
            "key_risks": summary.key_risks,
            "key_opportunities": summary.key_opportunities,
            "recommended_actions": summary.recommended_actions,
            "visualization_data": summary.tree_visualization_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario generation failed: {str(e)}")


@router.post("/scenarios/monte-carlo")
async def run_monte_carlo(request: ScenarioBranchRequest):
    """Run Monte Carlo simulation for outcome distribution"""
    try:
        from backend.engine.scenario_engine import ScenarioEngine, ScenarioBranchInput

        scenario_engine = ScenarioEngine()

        branch_input = ScenarioBranchInput(
            decision_id=request.decision_id,
            your_move=request.your_move,
            company_name=request.company_name,
            competitor_names=request.competitor_names,
            num_simulations=request.num_simulations
        )

        results = await scenario_engine.run_monte_carlo(
            input_data=branch_input,
            competitors=[],
            num_simulations=request.num_simulations
        )

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monte Carlo failed: {str(e)}")


# ==================== CONFIDENCE DECOMPOSITION ====================

class ConfidenceRequest(BaseModel):
    prediction: Dict
    research_id: Optional[str] = None
    time_horizon_days: int = 90


@router.post("/confidence/decompose")
async def decompose_confidence(request: ConfidenceRequest):
    """Decompose prediction confidence into components"""
    try:
        from backend.engine.confidence_engine import ConfidenceEngine
        from backend.db.supabase import get_database

        engine = ConfidenceEngine()
        db = get_database()

        research_result = None
        if request.research_id:
            research_result = await db.get_research_result(request.research_id)

        decomposition = engine.decompose_confidence(
            prediction=request.prediction,
            research_result=research_result,
            time_horizon_days=request.time_horizon_days
        )

        # Generate human-readable report
        report = engine.generate_confidence_report(
            decomposition=decomposition,
            prediction_summary=request.prediction.get("summary", "Prediction")
        )

        return {
            "overall_confidence": decomposition.overall_confidence,
            "confidence_level": decomposition.confidence_level.value,
            "confidence_interval": decomposition.confidence_interval,
            "components": [
                {
                    "name": c.name,
                    "source": c.source.value,
                    "contribution": c.contribution,
                    "reducible": c.reducible,
                    "reduction_actions": c.reduction_actions[:2]
                }
                for c in decomposition.components
            ],
            "primary_uncertainty": decomposition.primary_uncertainty,
            "most_reducible": decomposition.most_reducible,
            "improvement_actions": decomposition.confidence_improvement_actions,
            "report": {
                "headline": report.headline,
                "plain_english": report.plain_english,
                "to_increase_confidence": report.to_increase_confidence,
                "key_assumptions": report.key_assumptions
            },
            "chart_data": decomposition.breakdown_chart_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Confidence decomposition failed: {str(e)}")


@router.post("/confidence/sensitivity")
async def run_sensitivity_analysis(request: Dict):
    """Run sensitivity analysis on prediction"""
    try:
        from backend.engine.confidence_engine import ConfidenceEngine

        engine = ConfidenceEngine()

        prediction = request.get("prediction", {})
        variables = request.get("variables", [])
        variation = request.get("variation_range", 0.2)

        analysis = engine.run_sensitivity_analysis(
            prediction=prediction,
            variables=variables,
            variation_range=variation
        )

        return {
            "most_sensitive_to": analysis.most_sensitive_to,
            "least_sensitive_to": analysis.least_sensitive_to,
            "variables_to_monitor": analysis.variables_to_monitor,
            "robustness_score": analysis.robustness_score,
            "sensitivities": analysis.sensitivities
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sensitivity analysis failed: {str(e)}")


# ==================== DECISION JOURNAL ====================

@router.post("/journal/{decision_id}/create")
async def create_journal(decision_id: str):
    """Create a decision journal"""
    try:
        from backend.engine.journal_engine import JournalEngine
        from backend.db.supabase import get_database

        engine = JournalEngine()
        db = get_database()

        decision = await db.get_decision(decision_id)
        if not decision:
            raise HTTPException(status_code=404, detail="Decision not found")

        journal = await engine.create_journal(decision)

        return {
            "journal_id": journal.id,
            "decision_id": journal.decision_id,
            "created_at": journal.created_at.isoformat(),
            "entries_count": len(journal.entries)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Journal creation failed: {str(e)}")


class AddPredictionRequest(BaseModel):
    prediction_type: str
    predicted_value: str
    confidence: float
    due_date: Optional[str] = None
    assumptions: List[str] = []


@router.post("/journal/{decision_id}/predictions")
async def add_prediction_to_journal(decision_id: str, request: AddPredictionRequest):
    """Add a prediction to the journal"""
    try:
        from backend.engine.journal_engine import JournalEngine
        from backend.models.journal import DecisionJournal
        from datetime import datetime

        engine = JournalEngine()

        # Get or create journal (simplified - in production would be from DB)
        journal = DecisionJournal(decision_id=decision_id)

        due_date = datetime.fromisoformat(request.due_date) if request.due_date else None

        prediction = await engine.add_prediction(
            journal=journal,
            prediction_type=request.prediction_type,
            predicted_value=request.predicted_value,
            confidence=request.confidence,
            due_date=due_date,
            assumptions=request.assumptions
        )

        return {
            "prediction_id": prediction.id,
            "prediction_type": prediction.prediction_type,
            "predicted_value": prediction.predicted_value,
            "confidence": prediction.confidence,
            "due_date": prediction.due_date.isoformat() if prediction.due_date else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add prediction: {str(e)}")


class RecordOutcomeRequest(BaseModel):
    prediction_id: str
    actual_value: str
    description: str = ""
    sources: List[str] = []


@router.post("/journal/{decision_id}/outcomes")
async def record_outcome(decision_id: str, request: RecordOutcomeRequest):
    """Record an actual outcome for a prediction"""
    try:
        from backend.engine.journal_engine import JournalEngine
        from backend.models.journal import DecisionJournal

        engine = JournalEngine()

        # Get journal (simplified)
        journal = DecisionJournal(decision_id=decision_id)

        outcome = await engine.record_outcome(
            journal=journal,
            prediction_id=request.prediction_id,
            actual_value=request.actual_value,
            description=request.description,
            sources=request.sources
        )

        return {
            "outcome_id": outcome.id,
            "prediction_id": outcome.prediction_id,
            "actual_value": outcome.actual_value,
            "recorded_at": outcome.recorded_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record outcome: {str(e)}")


@router.get("/journal/{decision_id}")
async def get_journal(decision_id: str):
    """Get decision journal"""
    try:
        from backend.db.supabase import get_database

        db = get_database()
        entries = await db.get_journal(decision_id)

        return {
            "decision_id": decision_id,
            "entries": entries,
            "total_entries": len(entries)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get journal: {str(e)}")


@router.post("/journal/{decision_id}/review")
async def conduct_decision_review(decision_id: str):
    """Conduct a structured review of a decision"""
    try:
        from backend.engine.journal_engine import JournalEngine
        from backend.models.journal import DecisionJournal
        from backend.db.supabase import get_database

        engine = JournalEngine()
        db = get_database()

        decision = await db.get_decision(decision_id)
        if not decision:
            raise HTTPException(status_code=404, detail="Decision not found")

        journal = DecisionJournal(decision_id=decision_id)

        review = await engine.conduct_review(journal, decision)

        return {
            "review_id": review.id,
            "decision_id": review.decision_id,
            "predictions_made": review.predictions_made,
            "predictions_accurate": review.predictions_accurate,
            "accuracy_rate": review.accuracy_rate,
            "what_went_well": review.what_went_well,
            "what_went_wrong": review.what_went_wrong,
            "surprises": review.surprises,
            "lessons": [l.model_dump() for l in review.lessons],
            "overall_score": review.overall_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")


# ==================== EXPORT ====================

class ExportRequest(BaseModel):
    decision_id: str
    format: str = "markdown"  # markdown, pdf
    include_scenarios: bool = True
    include_confidence: bool = True
    include_journal: bool = True


@router.post("/export")
async def export_decision(request: ExportRequest):
    """Export decision analysis to markdown or PDF"""
    try:
        from backend.engine.export_engine import ExportEngine
        from backend.db.supabase import get_database
        from fastapi.responses import Response

        engine = ExportEngine()
        db = get_database()

        # Get decision
        decision = await db.get_decision(request.decision_id)
        if not decision:
            raise HTTPException(status_code=404, detail="Decision not found")

        # Get optional data
        scenario_summary = None
        confidence = None
        journal = None

        if request.format == "markdown":
            content = engine.export_decision_to_markdown(
                decision=decision,
                scenario_summary=scenario_summary,
                confidence=confidence,
                journal=journal
            )
            return {
                "format": "markdown",
                "content": content,
                "filename": f"{decision.title.replace(' ', '_')}_analysis.md"
            }
        elif request.format == "pdf":
            pdf_bytes = engine.export_decision_to_pdf(
                decision=decision,
                scenario_summary=scenario_summary,
                confidence=confidence,
                journal=journal
            )
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={decision.title.replace(' ', '_')}_analysis.pdf"
                }
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/export/competitive")
async def export_competitive_analysis(research_id: str, your_move: Dict):
    """Export competitive analysis to markdown"""
    try:
        from backend.engine.export_engine import ExportEngine
        from backend.engine.competitor_engine import CompetitorEngine
        from backend.db.supabase import get_database

        export_engine = ExportEngine()
        competitor_engine = CompetitorEngine()
        db = get_database()

        # Get research result
        result = await db.get_research_result(research_id)
        if not result:
            raise HTTPException(status_code=404, detail="Research not found")

        # Run competitor analysis
        competitor_agents = competitor_engine.generate_competitor_agents(result.competitors)
        analysis = competitor_engine.predict_responses(
            your_move=your_move,
            competitors=competitor_agents
        )

        # Export to markdown
        markdown = export_engine.export_competitive_analysis_markdown(
            company_name=result.target_company.name if result.target_company else "Company",
            competitor_analysis={
                "your_move": analysis.your_move,
                "competitor_responses": analysis.competitor_responses,
                "scenario_probabilities": analysis.scenario_probabilities,
                "nash_equilibrium": analysis.nash_equilibrium,
                "risk_factors": analysis.risk_factors,
                "recommended_strategies": analysis.recommended_counter_strategies
            }
        )

        return {
            "format": "markdown",
            "content": markdown,
            "filename": f"competitive_analysis_{result.target_company.name.replace(' ', '_')}.md"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/export/journal/{decision_id}")
async def export_journal_markdown(decision_id: str):
    """Export decision journal to markdown"""
    try:
        from backend.engine.export_engine import ExportEngine
        from backend.engine.journal_engine import JournalEngine
        from backend.models.journal import DecisionJournal
        from backend.db.supabase import get_database

        export_engine = ExportEngine()
        journal_engine = JournalEngine()
        db = get_database()

        decision = await db.get_decision(decision_id)
        if not decision:
            raise HTTPException(status_code=404, detail="Decision not found")

        journal = DecisionJournal(decision_id=decision_id)
        journal_export = journal_engine.export_journal(journal, decision)

        markdown = export_engine.export_journal_to_markdown(journal_export)

        return {
            "format": "markdown",
            "content": markdown,
            "filename": f"journal_{decision.title.replace(' ', '_')}.md"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# ==================== HEALTH ====================

@router.get("/health")
async def di_health_check():
    """Decision Intelligence health check"""
    return {
        "status": "healthy",
        "decisions": len(decisions_db),
        "worlds": len(worlds_db),
        "audiences": len(audiences_db),
        "simulations": len(simulations_db)
    }
