"""
Graph Execution API - Runs the full Decision Intelligence pipeline with proper data flow.

This is the "real" API that runs nodes in dependency order with state accumulation.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from backend.engine.graph import (
    GraphExecutor, GraphExecutionResult, BatchInput, NODE_DEFINITIONS, get_execution_order
)

router = APIRouter(prefix="/api/graph", tags=["Graph Execution"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ExecuteGraphRequest(BaseModel):
    """Request to execute the decision intelligence graph"""
    batch_code: str = "W24"
    accelerator: str = "YC"
    max_companies: int = 5
    nodes_to_run: Optional[List[str]] = None  # None = all nodes


class ExecuteGraphResponse(BaseModel):
    """Response from graph execution"""
    execution_id: str
    status: str  # "running", "completed", "failed"
    progress: float
    nodes_completed: List[str] = []
    nodes_failed: List[str] = []
    total_time_ms: Optional[int] = None
    result_url: Optional[str] = None


class GraphStatusResponse(BaseModel):
    """Status of a graph execution"""
    execution_id: str
    status: str
    progress: float
    nodes_completed: List[str]
    nodes_total: int
    current_node: Optional[str] = None
    started_at: str
    elapsed_ms: int


class GraphResultResponse(BaseModel):
    """Full result of a graph execution"""
    execution_id: str
    success: bool
    total_time_ms: int
    nodes_completed: List[str]
    nodes_failed: List[str]

    # Per-company results
    companies: List[str]
    predictions: Dict[str, Any]
    decision_briefs: Dict[str, Any]

    # Batch-level analysis
    comparison_matrix: Optional[Dict] = None
    portfolio_analysis: Optional[Dict] = None

    # Enterprise Deliverables
    deliverables: Optional[Dict] = None

    # Full state (for debugging)
    full_state: Optional[Dict] = None


class DeliverableType(str):
    INVESTMENT_MEMO = "investment_memo"
    RISK_REGISTER = "risk_register"
    EXECUTIVE_BRIEF = "executive_brief"
    DECISION_MATRIX = "decision_matrix"


# ============================================================================
# IN-MEMORY STORAGE (replace with Redis/DB in production)
# ============================================================================

_executions: Dict[str, Dict] = {}


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/nodes")
async def list_nodes():
    """List all available nodes and their dependencies"""
    nodes = []
    for name, definition in NODE_DEFINITIONS.items():
        nodes.append({
            "name": name,
            "category": definition.category,
            "dependencies": definition.dependencies,
            "description": definition.description
        })

    return {
        "nodes": nodes,
        "execution_order": get_execution_order(),
        "total_nodes": len(nodes)
    }


@router.post("/execute", response_model=ExecuteGraphResponse)
async def execute_graph(request: ExecuteGraphRequest, background_tasks: BackgroundTasks):
    """
    Execute the full decision intelligence graph.

    This runs all nodes in dependency order, with each node's output
    flowing into downstream nodes.
    """
    execution_id = str(uuid.uuid4())[:8]

    # Initialize execution tracking
    _executions[execution_id] = {
        "status": "running",
        "progress": 0.0,
        "nodes_completed": [],
        "nodes_failed": [],
        "current_node": None,
        "started_at": datetime.now().isoformat(),
        "result": None
    }

    # Run in background
    background_tasks.add_task(
        _run_graph_execution,
        execution_id,
        request
    )

    return ExecuteGraphResponse(
        execution_id=execution_id,
        status="running",
        progress=0.0,
        result_url=f"/api/graph/results/{execution_id}"
    )


async def _run_graph_execution(execution_id: str, request: ExecuteGraphRequest):
    """Background task to run graph execution"""
    try:
        executor = GraphExecutor()
        batch_input = BatchInput(
            batch_code=request.batch_code,
            accelerator=request.accelerator,
            max_companies=request.max_companies
        )

        all_nodes = get_execution_order()
        total_nodes = len(request.nodes_to_run or all_nodes)

        def on_node_complete(node_name: str, result):
            exec_data = _executions.get(execution_id, {})
            exec_data["nodes_completed"].append(node_name)
            exec_data["progress"] = len(exec_data["nodes_completed"]) / total_nodes
            exec_data["current_node"] = None

        result = await executor.execute(
            batch_input=batch_input,
            nodes_to_run=request.nodes_to_run,
            on_node_complete=on_node_complete
        )

        # Store result
        _executions[execution_id]["status"] = "completed" if result.success else "failed"
        _executions[execution_id]["progress"] = 1.0
        _executions[execution_id]["nodes_completed"] = result.nodes_completed
        _executions[execution_id]["nodes_failed"] = result.nodes_failed
        _executions[execution_id]["result"] = result

    except Exception as e:
        _executions[execution_id]["status"] = "failed"
        _executions[execution_id]["error"] = str(e)
        print(f"[GraphAPI] Execution {execution_id} failed: {e}")


@router.get("/status/{execution_id}", response_model=GraphStatusResponse)
async def get_execution_status(execution_id: str):
    """Get status of a graph execution"""
    if execution_id not in _executions:
        raise HTTPException(404, "Execution not found")

    exec_data = _executions[execution_id]
    started = datetime.fromisoformat(exec_data["started_at"])
    elapsed = int((datetime.now() - started).total_seconds() * 1000)

    return GraphStatusResponse(
        execution_id=execution_id,
        status=exec_data["status"],
        progress=exec_data["progress"],
        nodes_completed=exec_data["nodes_completed"],
        nodes_total=len(get_execution_order()),
        current_node=exec_data.get("current_node"),
        started_at=exec_data["started_at"],
        elapsed_ms=elapsed
    )


@router.get("/results/{execution_id}", response_model=GraphResultResponse)
async def get_execution_results(execution_id: str, include_full_state: bool = False):
    """Get full results of a completed graph execution"""
    if execution_id not in _executions:
        raise HTTPException(404, "Execution not found")

    exec_data = _executions[execution_id]

    if exec_data["status"] == "running":
        raise HTTPException(400, "Execution still running")

    result: GraphExecutionResult = exec_data.get("result")
    if not result:
        raise HTTPException(500, "No result available")

    state = result.final_state

    # Convert predictions to serializable format
    predictions = {}
    for company, pred in state.predictions.items():
        predictions[company] = {
            "unicorn_probability": pred.unicorn_probability,
            "centaur_probability": pred.centaur_probability,
            "success_probability": pred.success_probability,
            "expected_valuation": pred.expected_valuation,
            "team_score": pred.team_score,
            "market_score": pred.market_score,
            "traction_score": pred.traction_score,
            "timing_score": pred.timing_score,
            "capital_score": pred.capital_score,
            "key_strengths": pred.key_strengths,
            "key_risks": pred.key_risks,
            "prediction_confidence": pred.prediction_confidence
        }

    # Convert decision briefs
    briefs = {}
    for company, brief in state.decision_briefs.items():
        briefs[company] = {
            "recommendation": brief.recommendation.value,
            "confidence": brief.confidence,
            "summary": brief.summary,
            "rationale": brief.rationale,
            "key_metrics": brief.key_metrics,
            "next_steps": brief.next_steps,
            "percentile_rank": brief.percentile_rank
        }

    response = GraphResultResponse(
        execution_id=execution_id,
        success=result.success,
        total_time_ms=result.total_time_ms,
        nodes_completed=result.nodes_completed,
        nodes_failed=result.nodes_failed,
        companies=state.target_companies,
        predictions=predictions,
        decision_briefs=briefs,
        comparison_matrix=state.comparison_matrix,
        portfolio_analysis=state.portfolio_analysis,
        deliverables=state.deliverables
    )

    if include_full_state:
        response.full_state = state.model_dump()

    return response


@router.post("/execute/sync", response_model=GraphResultResponse)
async def execute_graph_sync(request: ExecuteGraphRequest):
    """
    Execute graph synchronously (blocks until complete).
    Use for small batches or when you need immediate results.
    """
    executor = GraphExecutor()
    batch_input = BatchInput(
        batch_code=request.batch_code,
        accelerator=request.accelerator,
        max_companies=request.max_companies
    )

    result = await executor.execute(
        batch_input=batch_input,
        nodes_to_run=request.nodes_to_run
    )

    state = result.final_state

    # Convert to response
    predictions = {}
    for company, pred in state.predictions.items():
        predictions[company] = {
            "unicorn_probability": pred.unicorn_probability,
            "centaur_probability": pred.centaur_probability,
            "success_probability": pred.success_probability,
            "expected_valuation": pred.expected_valuation,
            "team_score": pred.team_score,
            "market_score": pred.market_score,
            "traction_score": pred.traction_score,
            "timing_score": pred.timing_score,
            "capital_score": pred.capital_score,
            "key_strengths": pred.key_strengths,
            "key_risks": pred.key_risks,
            "prediction_confidence": pred.prediction_confidence
        }

    briefs = {}
    for company, brief in state.decision_briefs.items():
        briefs[company] = {
            "recommendation": brief.recommendation.value,
            "confidence": brief.confidence,
            "summary": brief.summary,
            "rationale": brief.rationale,
            "key_metrics": brief.key_metrics,
            "next_steps": brief.next_steps,
            "percentile_rank": brief.percentile_rank
        }

    return GraphResultResponse(
        execution_id=result.execution_id,
        success=result.success,
        total_time_ms=result.total_time_ms,
        nodes_completed=result.nodes_completed,
        nodes_failed=result.nodes_failed,
        companies=state.target_companies,
        predictions=predictions,
        decision_briefs=briefs,
        comparison_matrix=state.comparison_matrix,
        portfolio_analysis=state.portfolio_analysis,
        deliverables=state.deliverables,
        full_state=state.model_dump()
    )


# ============================================================================
# DELIVERABLES ENDPOINTS
# ============================================================================

@router.get("/deliverables/{execution_id}")
async def get_deliverables(execution_id: str):
    """
    Get all generated deliverables for a completed execution.

    Returns board-ready documents:
    - Investment Memos (per company)
    - Risk Registers (per company)
    - Executive Briefs (per company)
    - Decision Matrix (batch-level)
    """
    if execution_id not in _executions:
        raise HTTPException(404, "Execution not found")

    exec_data = _executions[execution_id]

    if exec_data["status"] == "running":
        raise HTTPException(400, "Execution still running")

    result: GraphExecutionResult = exec_data.get("result")
    if not result:
        raise HTTPException(500, "No result available")

    state = result.final_state

    if not state.deliverables:
        raise HTTPException(404, "Deliverables not generated for this execution")

    return state.deliverables


@router.get("/deliverables/{execution_id}/investment-memo/{company_name}")
async def get_investment_memo(execution_id: str, company_name: str):
    """Get investment memo for a specific company"""
    if execution_id not in _executions:
        raise HTTPException(404, "Execution not found")

    exec_data = _executions[execution_id]
    result: GraphExecutionResult = exec_data.get("result")
    if not result:
        raise HTTPException(500, "No result available")

    state = result.final_state
    if not state.deliverables:
        raise HTTPException(404, "Deliverables not generated")

    memo = state.deliverables.get("investment_memos", {}).get(company_name)
    if not memo:
        raise HTTPException(404, f"Investment memo not found for {company_name}")

    return memo


@router.get("/deliverables/{execution_id}/risk-register/{company_name}")
async def get_risk_register(execution_id: str, company_name: str):
    """Get risk register for a specific company"""
    if execution_id not in _executions:
        raise HTTPException(404, "Execution not found")

    exec_data = _executions[execution_id]
    result: GraphExecutionResult = exec_data.get("result")
    if not result:
        raise HTTPException(500, "No result available")

    state = result.final_state
    if not state.deliverables:
        raise HTTPException(404, "Deliverables not generated")

    register = state.deliverables.get("risk_registers", {}).get(company_name)
    if not register:
        raise HTTPException(404, f"Risk register not found for {company_name}")

    return register


@router.get("/deliverables/{execution_id}/executive-brief/{company_name}")
async def get_executive_brief(execution_id: str, company_name: str):
    """Get executive brief for a specific company"""
    if execution_id not in _executions:
        raise HTTPException(404, "Execution not found")

    exec_data = _executions[execution_id]
    result: GraphExecutionResult = exec_data.get("result")
    if not result:
        raise HTTPException(500, "No result available")

    state = result.final_state
    if not state.deliverables:
        raise HTTPException(404, "Deliverables not generated")

    brief = state.deliverables.get("executive_briefs", {}).get(company_name)
    if not brief:
        raise HTTPException(404, f"Executive brief not found for {company_name}")

    return brief


@router.get("/deliverables/{execution_id}/decision-matrix")
async def get_decision_matrix(execution_id: str):
    """Get the batch-level decision matrix"""
    if execution_id not in _executions:
        raise HTTPException(404, "Execution not found")

    exec_data = _executions[execution_id]
    result: GraphExecutionResult = exec_data.get("result")
    if not result:
        raise HTTPException(500, "No result available")

    state = result.final_state
    if not state.deliverables:
        raise HTTPException(404, "Deliverables not generated")

    matrix = state.deliverables.get("decision_matrix")
    if not matrix:
        raise HTTPException(404, "Decision matrix not found")

    return matrix


@router.get("/demo")
async def run_demo():
    """
    Quick demo endpoint - runs the full pipeline on YC W24 batch (3 companies).
    Returns results in ~30-60 seconds.
    """
    executor = GraphExecutor()
    batch_input = BatchInput(
        batch_code="W24",
        accelerator="YC",
        max_companies=3
    )

    result = await executor.execute(batch_input=batch_input)
    state = result.final_state

    # Build response
    output = {
        "execution_id": result.execution_id,
        "success": result.success,
        "time_ms": result.total_time_ms,
        "batch": state.batch.batch_name if state.batch else "Unknown",
        "companies_analyzed": state.target_companies,
        "predictions": [],
        "top_pick": None
    }

    for company in state.target_companies:
        pred = state.predictions.get(company)
        brief = state.decision_briefs.get(company)

        if pred:
            company_summary = {
                "company": company,
                "unicorn_probability": f"{pred.unicorn_probability * 100:.1f}%",
                "expected_valuation": f"${pred.expected_valuation / 1e6:.0f}M",
                "recommendation": brief.recommendation.value if brief else "MONITOR",
                "strengths": pred.key_strengths[:2],
                "risks": pred.key_risks[:2],
                "factor_scores": {
                    "team": f"{pred.team_score * 100:.0f}",
                    "market": f"{pred.market_score * 100:.0f}",
                    "traction": f"{pred.traction_score * 100:.0f}",
                    "timing": f"{pred.timing_score * 100:.0f}",
                    "capital": f"{pred.capital_score * 100:.0f}"
                }
            }
            output["predictions"].append(company_summary)

    # Identify top pick
    if output["predictions"]:
        top = max(output["predictions"], key=lambda x: float(x["unicorn_probability"].rstrip("%")))
        output["top_pick"] = {
            "company": top["company"],
            "unicorn_probability": top["unicorn_probability"],
            "summary": f"{top['company']} leads the batch with {top['unicorn_probability']} unicorn probability."
        }

    return output
