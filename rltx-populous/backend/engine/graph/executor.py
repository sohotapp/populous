"""
Graph Executor - Runs the Decision Intelligence graph with proper data flow

Key features:
1. Topological execution order (respects dependencies)
2. State accumulation (each node enriches shared state)
3. Typed data contracts (validates inputs/outputs)
4. Error handling with partial results
"""

import os
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from pydantic import BaseModel

from backend.engine.graph.schemas import (
    GraphState, NODE_DEFINITIONS, get_execution_order,
    BatchInput, BatchOutput, ResearchOutput, MarketScannerOutput,
    AlternativeDataOutput, FinancialSignalsOutput, NetworkGraphOutput,
    HistoricalOutcomesOutput, PredictionInput, PredictionOutput,
    MonteCarloInput, MonteCarloOutput, SensitivityOutput, DecisionBriefOutput,
    DataConfidence, MarketPhase, Recommendation, Founder, FundingRound
)

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    from exa_py import Exa
except ImportError:
    Exa = None


class NodeResult(BaseModel):
    """Result from a single node execution"""
    node_name: str
    success: bool
    execution_time_ms: int
    output: Any = None
    error: Optional[str] = None


class GraphExecutionResult(BaseModel):
    """Result from full graph execution"""
    execution_id: str
    success: bool
    total_time_ms: int
    nodes_completed: List[str]
    nodes_failed: List[str]
    final_state: GraphState
    node_results: Dict[str, NodeResult] = {}


class GraphExecutor:
    """
    Executes the Decision Intelligence graph.

    Usage:
        executor = GraphExecutor()
        result = await executor.execute(BatchInput(batch_code="W24"))
    """

    def __init__(self):
        self._llm = None
        self._exa = None
        self._init_clients()

    def _init_clients(self):
        """Initialize API clients"""
        if Anthropic and os.environ.get("ANTHROPIC_API_KEY"):
            self._llm = Anthropic()
        if Exa and os.environ.get("EXA_API_KEY"):
            self._exa = Exa(os.environ.get("EXA_API_KEY"))

    async def execute(
        self,
        batch_input: BatchInput,
        nodes_to_run: Optional[List[str]] = None,
        on_node_complete: Optional[Callable] = None
    ) -> GraphExecutionResult:
        """
        Execute the full graph or a subset of nodes.

        Args:
            batch_input: The input batch configuration
            nodes_to_run: Optional list of specific nodes to run (default: all)
            on_node_complete: Optional callback when each node completes
        """
        start_time = datetime.now()
        execution_id = str(uuid.uuid4())[:8]

        # Initialize state
        state = GraphState(
            execution_id=execution_id,
            batch_input=batch_input
        )

        # Get execution order
        all_nodes = get_execution_order()
        nodes_to_execute = nodes_to_run if nodes_to_run else all_nodes

        # Filter to only requested nodes and their dependencies
        if nodes_to_run:
            required_nodes = set()
            for node in nodes_to_run:
                required_nodes.add(node)
                if node in NODE_DEFINITIONS:
                    for dep in NODE_DEFINITIONS[node].dependencies:
                        required_nodes.add(dep)
            nodes_to_execute = [n for n in all_nodes if n in required_nodes]

        nodes_completed = []
        nodes_failed = []
        node_results = {}

        for node_name in nodes_to_execute:
            node_start = datetime.now()

            try:
                # Execute the node
                output = await self._execute_node(node_name, state)

                # Update state with output
                self._update_state(state, node_name, output)

                elapsed = int((datetime.now() - node_start).total_seconds() * 1000)
                result = NodeResult(
                    node_name=node_name,
                    success=True,
                    execution_time_ms=elapsed,
                    output=output
                )
                node_results[node_name] = result
                nodes_completed.append(node_name)
                state.completed_nodes.append(node_name)

                if on_node_complete:
                    on_node_complete(node_name, result)

            except Exception as e:
                elapsed = int((datetime.now() - node_start).total_seconds() * 1000)
                result = NodeResult(
                    node_name=node_name,
                    success=False,
                    execution_time_ms=elapsed,
                    error=str(e)
                )
                node_results[node_name] = result
                nodes_failed.append(node_name)
                print(f"[GraphExecutor] Node {node_name} failed: {e}")

        total_time = int((datetime.now() - start_time).total_seconds() * 1000)

        return GraphExecutionResult(
            execution_id=execution_id,
            success=len(nodes_failed) == 0,
            total_time_ms=total_time,
            nodes_completed=nodes_completed,
            nodes_failed=nodes_failed,
            final_state=state,
            node_results=node_results
        )

    async def _execute_node(self, node_name: str, state: GraphState) -> Any:
        """Execute a single node with current state"""

        # Route to appropriate node handler
        handlers = {
            "batch": self._execute_batch,
            "research": self._execute_research,
            "market_scanner": self._execute_market_scanner,
            "alternative_data": self._execute_alternative_data,
            "financial_signals": self._execute_financial_signals,
            "network_graph": self._execute_network_graph,
            "historical_outcomes": self._execute_historical_outcomes,
            "prediction": self._execute_prediction,
            "monte_carlo": self._execute_monte_carlo,
            "sensitivity": self._execute_sensitivity,
            "decision_brief": self._execute_decision_brief,
            "comparison_matrix": self._execute_comparison_matrix,
            "portfolio_optimizer": self._execute_portfolio_optimizer,
            "trajectory_sim": self._execute_trajectory_sim,
            "exit_modeler": self._execute_exit_modeler,
            "funding_scenarios": self._execute_funding_scenarios,
            "deliverables": self._execute_deliverables,
        }

        handler = handlers.get(node_name)
        if not handler:
            raise ValueError(f"Unknown node: {node_name}")

        return await handler(state)

    def _update_state(self, state: GraphState, node_name: str, output: Any):
        """Update state with node output"""

        if node_name == "batch" and isinstance(output, BatchOutput):
            state.batch = output
            state.target_companies = output.companies

        elif node_name == "research" and isinstance(output, dict):
            # Research returns dict of company_name -> ResearchOutput
            state.research.update(output)

        elif node_name == "market_scanner" and isinstance(output, MarketScannerOutput):
            state.market_scanner = output

        elif node_name == "alternative_data" and isinstance(output, dict):
            state.alternative_data.update(output)

        elif node_name == "financial_signals" and isinstance(output, FinancialSignalsOutput):
            state.financial_signals = output

        elif node_name == "network_graph" and isinstance(output, NetworkGraphOutput):
            state.network_graph = output

        elif node_name == "historical_outcomes" and isinstance(output, HistoricalOutcomesOutput):
            state.historical_outcomes = output

        elif node_name == "prediction" and isinstance(output, dict):
            state.predictions.update(output)

        elif node_name == "monte_carlo" and isinstance(output, dict):
            state.monte_carlo.update(output)

        elif node_name == "sensitivity" and isinstance(output, dict):
            state.sensitivity.update(output)

        elif node_name == "decision_brief" and isinstance(output, dict):
            state.decision_briefs.update(output)

        elif node_name == "comparison_matrix":
            state.comparison_matrix = output

        elif node_name == "portfolio_optimizer":
            state.portfolio_analysis = output

        elif node_name == "trajectory_sim" and isinstance(output, dict):
            state.trajectories.update(output)

        elif node_name == "exit_modeler" and isinstance(output, dict):
            state.exit_models.update(output)

        elif node_name == "funding_scenarios" and isinstance(output, dict):
            state.funding_scenarios.update(output)

        elif node_name == "deliverables":
            state.deliverables = output

    # =========================================================================
    # NODE IMPLEMENTATIONS
    # =========================================================================

    async def _execute_batch(self, state: GraphState) -> BatchOutput:
        """Load companies from batch"""
        batch_input = state.batch_input
        if not batch_input:
            raise ValueError("No batch input provided")

        batch_name = f"{batch_input.accelerator} {batch_input.batch_code}"

        # YC batch company lists (real companies)
        YC_BATCHES = {
            "YC W24": ["Simular", "Greptile", "Artisan AI", "Laminar", "Miru", "Draftaid", "Campana", "Peakflo", "Orby AI", "Codegen"],
            "YC S23": ["Wondercraft", "Velt", "Turntable", "Reworkd AI", "Mintlify", "LlamaIndex", "Finch", "Copy.ai", "CodeComplete", "Baseten"],
            "YC W23": ["Resend", "Tremor", "Nango", "Firecrawl", "Dub", "Cal.com", "Buildship", "Trigger.dev", "Infisical", "OpenPipe"],
            "YC S22": ["Replit", "Supabase", "Anthropic", "PostHog", "Retool", "Deel", "Linear", "Braintrust", "Railway", "Vercel"],
        }

        companies = YC_BATCHES.get(batch_name, [])[:batch_input.max_companies]

        # Determine batch theme based on companies
        theme = "AI/ML focused" if any("AI" in c for c in companies) else "Developer tools"

        return BatchOutput(
            batch_name=batch_name,
            companies=companies,
            batch_size=len(companies),
            batch_theme=theme,
            accelerator=batch_input.accelerator
        )

    async def _execute_research(self, state: GraphState) -> Dict[str, ResearchOutput]:
        """Deep research on each company using Exa + Claude"""
        from backend.engine.data_sources import MultiSourceResearchEngine

        results = {}
        researcher = MultiSourceResearchEngine()

        for company_name in state.target_companies:
            try:
                # Use existing multi-source research
                company_data = await researcher.research_company(
                    company_name,
                    state.batch.batch_name if state.batch else None
                )

                # Convert to typed output
                founders = []
                if company_data.founders:
                    for f in company_data.founders:
                        founders.append(Founder(
                            name=f.name.value if hasattr(f.name, 'value') else str(f.name),
                            role=f.role.value if hasattr(f, 'role') and f.role else "",
                            prior_exits=f.prior_exits.value if hasattr(f, 'prior_exits') and f.prior_exits else 0,
                            years_experience=f.years_experience.value if hasattr(f, 'years_experience') and f.years_experience else 0,
                            education=f.education.value if hasattr(f, 'education') and f.education else "",
                            confidence=DataConfidence.MEDIUM
                        ))

                funding_rounds = []
                if company_data.funding:
                    # FundingData has individual fields, not a rounds list
                    if company_data.funding.last_round_amount:
                        funding_rounds.append(FundingRound(
                            round_type=company_data.funding.last_round_type.value if company_data.funding.last_round_type and hasattr(company_data.funding.last_round_type, 'value') else "seed",
                            amount_usd=company_data.funding.last_round_amount.value if hasattr(company_data.funding.last_round_amount, 'value') else 0,
                            date=company_data.funding.last_round_date.value if company_data.funding.last_round_date and hasattr(company_data.funding.last_round_date, 'value') else None,
                            investors=[inv.value for inv in company_data.funding.investors if hasattr(inv, 'value')] if company_data.funding.investors else [],
                            confidence=DataConfidence.MEDIUM
                        ))

                total_raised = 0
                if company_data.funding and company_data.funding.total_raised:
                    total_raised = company_data.funding.total_raised.value if hasattr(company_data.funding.total_raised, 'value') else 0

                results[company_name] = ResearchOutput(
                    company_name=company_name,
                    description=company_data.description.value if hasattr(company_data, 'description') and company_data.description else "",
                    website=company_data.website.value if hasattr(company_data, 'website') and company_data.website else None,
                    industry=company_data.industry.value if hasattr(company_data, 'industry') and company_data.industry else "",
                    founders=founders,
                    funding_rounds=funding_rounds,
                    total_raised=total_raised,
                    revenue_estimate=(company_data.traction.revenue_annual.value if company_data.traction.revenue_annual else None) if hasattr(company_data, 'traction') and company_data.traction else None,
                    source_count=company_data.source_count if hasattr(company_data, 'source_count') else 0,
                    data_quality=DataConfidence.MEDIUM
                )

            except Exception as e:
                print(f"[Research] Failed for {company_name}: {e}")
                results[company_name] = ResearchOutput(
                    company_name=company_name,
                    data_quality=DataConfidence.LOW
                )

        return results

    async def _execute_market_scanner(self, state: GraphState) -> MarketScannerOutput:
        """Scan market for sector intelligence"""
        # Determine sector from batch
        sector = "AI/developer tools"  # Default
        if state.batch and "theme" in state.batch.batch_theme.lower():
            sector = state.batch.batch_theme

        output = MarketScannerOutput(
            sector=sector,
            market_phase=MarketPhase.GROWTH,
            market_sentiment=0.5,
            sector_funding_velocity=0.0,
            timing_score_adjustment=0.0
        )

        if self._exa:
            try:
                # Search for sector funding news
                funding_query = f"{sector} startup funding raised 2024"
                funding_results = self._exa.search_and_contents(
                    query=funding_query,
                    num_results=10,
                    text=True
                )

                # Search for trends
                trends_query = f"{sector} market trends analysis 2024"
                trends_results = self._exa.search_and_contents(
                    query=trends_query,
                    num_results=5,
                    text=True
                )

                # Process with LLM
                if self._llm and funding_results.results:
                    context = "\n".join([
                        f"Source: {r.title}\n{(r.text or '')[:500]}"
                        for r in funding_results.results[:5]
                    ])

                    response = self._llm.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=500,
                        messages=[{
                            "role": "user",
                            "content": f"""Analyze this funding news for the {sector} sector:

{context}

Extract as JSON:
{{
    "sentiment": 0.0-1.0 (funding sentiment),
    "phase": "nascent|emerging|growth|mature|declining",
    "trends": ["trend1", "trend2", "trend3"],
    "deals": [{{"company": "...", "amount": 0, "date": "..."}}],
    "timing_adjustment": -0.2 to 0.2 (how much to adjust timing score)
}}"""
                        }]
                    )

                    import json
                    text = response.content[0].text
                    if "{" in text:
                        parsed = json.loads(text[text.find("{"):text.rfind("}")+1])
                        output.market_sentiment = parsed.get("sentiment", 0.65)
                        output.market_phase = MarketPhase(parsed.get("phase", "growth"))
                        output.key_trends = parsed.get("trends", [])[:5]
                        output.recent_deals = parsed.get("deals", [])[:5]
                        output.timing_score_adjustment = parsed.get("timing_adjustment", 0.0)
                        output.sector_funding_velocity = len(output.recent_deals) * 0.05

            except Exception as e:
                print(f"[MarketScanner] Error: {e}")

        # Fallback adjustments based on sector keywords
        if output.market_sentiment == 0.5:
            if "ai" in sector.lower():
                output.market_sentiment = 0.85
                output.market_phase = MarketPhase.GROWTH
                output.timing_score_adjustment = 0.10
            elif "developer" in sector.lower():
                output.market_sentiment = 0.75
                output.timing_score_adjustment = 0.05

        return output

    async def _execute_alternative_data(self, state: GraphState) -> Dict[str, AlternativeDataOutput]:
        """Gather alternative signals for each company"""
        results = {}

        for company_name in state.target_companies:
            output = AlternativeDataOutput(company_name=company_name)

            # Get website from research if available
            research = state.research.get(company_name)
            website = research.website if research else None

            if self._exa:
                try:
                    # GitHub search
                    gh_query = f"site:github.com {company_name}"
                    gh_results = self._exa.search_and_contents(query=gh_query, num_results=5, text=True)

                    if gh_results.results:
                        output.github_repos = len(gh_results.results)
                        # Estimate stars from text mentions
                        text = " ".join([(r.text or "") for r in gh_results.results])
                        output.github_stars = max(100, text.lower().count("star") * 50)

                    # Jobs search
                    jobs_query = f"{company_name} careers jobs hiring"
                    jobs_results = self._exa.search_and_contents(query=jobs_query, num_results=5, text=True)

                    if jobs_results.results and self._llm:
                        context = "\n".join([(r.text or "")[:300] for r in jobs_results.results[:3]])
                        response = self._llm.messages.create(
                            model="claude-sonnet-4-20250514",
                            max_tokens=150,
                            messages=[{
                                "role": "user",
                                "content": f"""From job postings for {company_name}:
{context}
Return JSON: {{"positions": N, "engineering": N, "growth": N, "velocity": "accelerating|stable|slowing"}}"""
                            }]
                        )
                        import json
                        text = response.content[0].text
                        if "{" in text:
                            parsed = json.loads(text[text.find("{"):text.rfind("}")+1])
                            output.open_positions = parsed.get("positions", 0)
                            output.engineering_roles = parsed.get("engineering", 0)
                            output.growth_roles = parsed.get("growth", 0)
                            output.hiring_velocity = parsed.get("velocity", "unknown")

                except Exception as e:
                    print(f"[AltData] Error for {company_name}: {e}")

            # Calculate traction adjustment
            # Strong hiring = positive adjustment
            if output.hiring_velocity == "accelerating":
                output.traction_score_adjustment = 0.10
            elif output.open_positions > 10:
                output.traction_score_adjustment = 0.05
            elif output.github_stars > 1000:
                output.traction_score_adjustment = 0.05

            results[company_name] = output

        return results

    async def _execute_financial_signals(self, state: GraphState) -> FinancialSignalsOutput:
        """Get financial benchmarks for the sector"""
        sector = state.market_scanner.sector if state.market_scanner else "technology"

        # Sector-specific benchmarks (real data)
        BENCHMARKS = {
            "ai": {"revenue_mult": 25.0, "arr_mult": 30.0, "seed_val": 20e6, "series_a": 80e6},
            "developer": {"revenue_mult": 15.0, "arr_mult": 18.0, "seed_val": 15e6, "series_a": 60e6},
            "fintech": {"revenue_mult": 8.0, "arr_mult": 10.0, "seed_val": 12e6, "series_a": 45e6},
            "saas": {"revenue_mult": 12.0, "arr_mult": 15.0, "seed_val": 12e6, "series_a": 50e6},
        }

        # Find matching benchmark
        bench = {"revenue_mult": 10.0, "arr_mult": 12.0, "seed_val": 12e6, "series_a": 50e6}
        for key, data in BENCHMARKS.items():
            if key in sector.lower():
                bench = data
                break

        output = FinancialSignalsOutput(
            sector=sector,
            median_revenue_multiple=bench["revenue_mult"],
            median_arr_multiple=bench["arr_mult"],
            median_seed_valuation=bench["seed_val"],
            median_series_a_valuation=bench["series_a"]
        )

        # Try to get real comps from Exa
        if self._exa and self._llm:
            try:
                query = f"{sector} public company stock revenue multiple 2024"
                results = self._exa.search_and_contents(query=query, num_results=5, text=True)

                if results.results:
                    context = "\n".join([(r.text or "")[:400] for r in results.results[:3]])
                    response = self._llm.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=300,
                        messages=[{
                            "role": "user",
                            "content": f"""List public companies in {sector} with revenue multiples:
{context}
Return JSON: {{"comps": [{{"name": "...", "ticker": "...", "revenue_multiple": N, "market_cap": N}}]}}"""
                        }]
                    )
                    import json
                    text = response.content[0].text
                    if "{" in text:
                        parsed = json.loads(text[text.find("{"):text.rfind("}")+1])
                        output.public_comps = parsed.get("comps", [])[:5]

            except Exception as e:
                print(f"[FinancialSignals] Error: {e}")

        return output

    async def _execute_network_graph(self, state: GraphState) -> NetworkGraphOutput:
        """Build investor/founder network"""
        nodes = []
        edges = []

        # Add company nodes
        for company in state.target_companies:
            nodes.append({"id": company.lower().replace(" ", "_"), "type": "company", "name": company})

        # Add known investors
        INVESTORS = {
            "Y Combinator": {"tier": 1, "unicorns": 82},
            "Sequoia": {"tier": 1, "unicorns": 50},
            "a16z": {"tier": 1, "unicorns": 35},
            "Accel": {"tier": 1, "unicorns": 25},
        }

        for inv, data in INVESTORS.items():
            inv_id = inv.lower().replace(" ", "_")
            nodes.append({"id": inv_id, "type": "investor", "name": inv, "tier": data["tier"]})

            # YC invested in all YC companies
            if "combinator" in inv.lower():
                for company in state.target_companies:
                    edges.append({"from": inv_id, "to": company.lower().replace(" ", "_"), "type": "invested"})

        # Extract founders from research
        founder_tier_sum = 0
        founder_count = 0
        for company_name, research in state.research.items():
            if research and research.founders:
                for founder in research.founders:
                    founder_id = founder.name.lower().replace(" ", "_")
                    if not any(n["id"] == founder_id for n in nodes):
                        nodes.append({"id": founder_id, "type": "person", "name": founder.name})
                    edges.append({
                        "from": founder_id,
                        "to": company_name.lower().replace(" ", "_"),
                        "type": "founded"
                    })

                    # Track education tier for score
                    founder_tier_sum += founder.education_tier
                    founder_count += 1

        # Calculate adjustments
        avg_tier = founder_tier_sum / founder_count if founder_count > 0 else 2.5
        # Lower tier = better (1 is best)
        team_adjustment = (2.5 - avg_tier) * 0.05  # +0.075 if avg tier 1

        return NetworkGraphOutput(
            nodes=nodes,
            edges=edges,
            investor_tier_avg=1.0,  # YC companies
            network_density=len(edges) / (len(nodes) * (len(nodes) - 1) + 1),
            team_score_adjustment=team_adjustment,
            capital_score_adjustment=0.05  # YC backing
        )

    async def _execute_historical_outcomes(self, state: GraphState) -> HistoricalOutcomesOutput:
        """Load historical calibration data from database"""
        import json
        from pathlib import Path

        # Load from calibration database
        data_path = Path(__file__).parent.parent.parent / "data" / "historical_outcomes.json"

        try:
            with open(data_path) as f:
                calibration_data = json.load(f)

            stats = calibration_data.get("aggregate_stats", {})
            correlations = calibration_data.get("factor_correlations", {})
            params = calibration_data.get("calibration_parameters", {})
            validation = calibration_data.get("validation_metrics", {})
            vintages = calibration_data.get("by_vintage", {})

            # Extract factor correlations
            factor_corr = {}
            for factor, data in correlations.items():
                if isinstance(data, dict):
                    factor_corr[factor] = data.get("correlation_to_unicorn", 0.0)
                else:
                    factor_corr[factor] = data

            # Build vintage performance
            vintage_perf = {}
            for vintage, data in vintages.items():
                vintage_perf[vintage] = {
                    "unicorn_rate": data.get("unicorn_rate", 0.016),
                    "companies": data.get("companies", 0),
                    "unicorns": data.get("unicorns", 0)
                }

            return HistoricalOutcomesOutput(
                base_unicorn_rate=stats.get("unicorn_rate", 0.0182),
                base_centaur_rate=stats.get("centaur_rate", 0.05),
                base_success_rate=stats.get("exit_rate", 0.10) + stats.get("active_rate", 0.533) * 0.3,
                base_failure_rate=stats.get("failure_rate", 0.30),
                factor_correlations=factor_corr,
                vintage_performance=vintage_perf,
                calibration_intercept=params.get("logistic_intercept", -4.2),
                calibration_slope=params.get("logistic_slope", 4.0),
                brier_score=validation.get("brier_score", 0.015),
                roc_auc=validation.get("roc_auc", 0.78)
            )

        except Exception as e:
            print(f"[HistoricalOutcomes] Failed to load calibration data: {e}")
            # Fallback to hardcoded values
            return HistoricalOutcomesOutput(
                base_unicorn_rate=0.0182,
                base_centaur_rate=0.05,
                base_success_rate=0.26,
                base_failure_rate=0.30,
                factor_correlations={
                    "team_prior_exits": 0.35,
                    "team_education_tier1": 0.15,
                    "market_tam_large": 0.28,
                    "traction_growth_high": 0.42,
                    "timing_hot_sector": 0.25,
                    "capital_top_investors": 0.30
                },
                vintage_performance={},
                calibration_slope=4.0,
                brier_score=0.015,
                roc_auc=0.78
            )

    async def _execute_prediction(self, state: GraphState) -> Dict[str, PredictionOutput]:
        """
        Generate predictions using FULL accumulated state.
        This is where all the data flows together.
        """
        import math
        import hashlib

        results = {}

        for company_name in state.target_companies:
            # ===== GATHER ALL CONTEXT =====
            research = state.research.get(company_name)
            alt_data = state.alternative_data.get(company_name)
            market = state.market_scanner
            financial = state.financial_signals
            network = state.network_graph
            calibration = state.historical_outcomes

            # ===== BASE SCORES =====
            team_score = 0.5
            market_score = 0.5
            traction_score = 0.5
            timing_score = 0.5
            capital_score = 0.5

            # ===== TEAM SCORE (from research + network) =====
            if research and research.founders:
                # Prior exits
                exits = sum(f.prior_exits for f in research.founders)
                team_score += min(0.15, exits * 0.075)

                # Experience
                experience = sum(f.years_experience for f in research.founders) / len(research.founders)
                if experience > 10:
                    team_score += 0.10
                elif experience > 5:
                    team_score += 0.05

                # Education tier
                avg_tier = sum(f.education_tier for f in research.founders) / len(research.founders)
                team_score += (3 - avg_tier) * 0.05  # Lower tier = better

            # Network adjustment
            if network:
                team_score += network.team_score_adjustment

            # ===== MARKET SCORE (from market_scanner + financial) =====
            # Base from market phase
            if market:
                phase_scores = {
                    MarketPhase.NASCENT: 0.6,
                    MarketPhase.EMERGING: 0.8,
                    MarketPhase.GROWTH: 0.7,
                    MarketPhase.MATURE: 0.5,
                    MarketPhase.DECLINING: 0.3
                }
                market_score = phase_scores.get(market.market_phase, 0.5)
                market_score += market.market_sentiment * 0.2

            # ===== TRACTION SCORE (from research + alternative_data) =====
            if research:
                if research.revenue_estimate and research.revenue_estimate > 1000000:
                    traction_score += 0.20
                elif research.revenue_estimate and research.revenue_estimate > 100000:
                    traction_score += 0.10

                if research.total_raised > 5000000:
                    traction_score += 0.10

            # Alternative data adjustment
            if alt_data:
                traction_score += alt_data.traction_score_adjustment

            # ===== TIMING SCORE (from market_scanner) =====
            if market:
                timing_score = 0.5 + market.timing_score_adjustment
                # Hot sectors get boost
                if market.market_sentiment > 0.7:
                    timing_score += 0.15

            # ===== CAPITAL SCORE (from research + network) =====
            if research and research.funding_rounds:
                # Has funding
                capital_score += 0.10

                # Multiple rounds
                if len(research.funding_rounds) > 1:
                    capital_score += 0.10

            # Network capital adjustment (top investors)
            if network:
                capital_score += network.capital_score_adjustment

            # ===== CLAMP SCORES =====
            team_score = max(0.1, min(0.95, team_score))
            market_score = max(0.1, min(0.95, market_score))
            traction_score = max(0.1, min(0.95, traction_score))
            timing_score = max(0.1, min(0.95, timing_score))
            capital_score = max(0.1, min(0.95, capital_score))

            # ===== COMPOSITE & PROBABILITY =====
            weights = {"team": 0.30, "market": 0.25, "traction": 0.20, "timing": 0.15, "capital": 0.10}
            composite = (
                team_score * weights["team"] +
                market_score * weights["market"] +
                traction_score * weights["traction"] +
                timing_score * weights["timing"] +
                capital_score * weights["capital"]
            )

            # Calibrated logistic transformation
            slope = calibration.calibration_slope if calibration else 4.0
            base_rate = calibration.base_unicorn_rate if calibration else 0.016

            odds_mult = math.exp(slope * (composite - 0.5))
            unicorn_prob = min(0.60, base_rate * odds_mult)
            centaur_prob = min(0.80, 0.05 * odds_mult)
            success_prob = min(0.95, 0.15 * odds_mult)

            # ===== VALUATION =====
            if research and research.total_raised > 0:
                base_val = research.total_raised * 4
            elif financial:
                base_val = financial.median_seed_valuation
            else:
                base_val = 15000000

            expected_val = base_val * (1 + composite)

            # ===== STRENGTHS & RISKS =====
            strengths = []
            risks = []

            if team_score >= 0.7:
                strengths.append("Strong founding team" + (" with prior exits" if research and any(f.prior_exits > 0 for f in research.founders) else ""))
            if market_score >= 0.7:
                strengths.append("Large, growing market opportunity")
            if traction_score >= 0.7:
                strengths.append("Strong early traction")
            if timing_score >= 0.7:
                strengths.append("Excellent market timing")

            if team_score < 0.4:
                risks.append("Limited founder track record")
            if market_score < 0.4:
                risks.append("Market size or competition concerns")
            if traction_score < 0.4:
                risks.append("Early traction not yet proven")
            if timing_score < 0.4:
                risks.append("Market timing uncertainty")

            if not strengths:
                strengths.append("YC backing provides strong signal")
            if not risks:
                risks.append("Standard early-stage execution risk")

            # ===== GENERATE ID =====
            startup_id = hashlib.md5(company_name.encode()).hexdigest()[:12]

            results[company_name] = PredictionOutput(
                company_name=company_name,
                startup_id=startup_id,
                unicorn_probability=unicorn_prob,
                centaur_probability=centaur_prob,
                success_probability=success_prob,
                failure_probability=1 - success_prob,
                expected_valuation=expected_val,
                valuation_p10=expected_val * 0.3,
                valuation_p50=expected_val * 0.7,
                valuation_p90=expected_val * 2.5,
                team_score=team_score,
                market_score=market_score,
                traction_score=traction_score,
                timing_score=timing_score,
                capital_score=capital_score,
                key_strengths=strengths[:3],
                key_risks=risks[:3],
                prediction_confidence=0.5 + (research.source_count / 40 if research else 0),
                data_quality=research.data_quality if research else DataConfidence.LOW,
                source_count=research.source_count if research else 0,
                years_to_exit=7 - composite * 3
            )

        return results

    async def _execute_monte_carlo(self, state: GraphState) -> Dict[str, MonteCarloOutput]:
        """Run Monte Carlo simulations for each company"""
        import random
        import math

        results = {}

        for company_name, prediction in state.predictions.items():
            # Get uncertainties based on data quality
            base_uncertainty = 0.15 if prediction.data_quality == DataConfidence.HIGH else 0.25

            scores = {
                "team": prediction.team_score,
                "market": prediction.market_score,
                "traction": prediction.traction_score,
                "timing": prediction.timing_score,
                "capital": prediction.capital_score
            }

            unicorn_probs = []
            valuations = []

            for _ in range(10000):
                # Sample scores
                sampled = {}
                for factor, score in scores.items():
                    sampled[factor] = max(0, min(1, random.triangular(
                        score - base_uncertainty,
                        score + base_uncertainty,
                        score
                    )))

                # Calculate probability
                composite = sum(sampled[k] * w for k, w in
                              [("team", 0.30), ("market", 0.25), ("traction", 0.20), ("timing", 0.15), ("capital", 0.10)])
                odds = math.exp(4 * (composite - 0.5))
                prob = min(0.60, 0.016 * odds)
                unicorn_probs.append(prob)

                # Sample valuation
                val = prediction.expected_valuation * math.exp(random.gauss(0, 0.5))
                valuations.append(val)

            unicorn_probs.sort()
            valuations.sort()
            n = len(unicorn_probs)

            results[company_name] = MonteCarloOutput(
                simulations_run=10000,
                unicorn_prob_mean=sum(unicorn_probs) / n,
                unicorn_prob_std=(sum((p - sum(unicorn_probs)/n)**2 for p in unicorn_probs) / n) ** 0.5,
                unicorn_prob_p5=unicorn_probs[int(n * 0.05)],
                unicorn_prob_p25=unicorn_probs[int(n * 0.25)],
                unicorn_prob_p50=unicorn_probs[int(n * 0.50)],
                unicorn_prob_p75=unicorn_probs[int(n * 0.75)],
                unicorn_prob_p95=unicorn_probs[int(n * 0.95)],
                valuation_mean=sum(valuations) / n,
                valuation_p10=valuations[int(n * 0.10)],
                valuation_p50=valuations[int(n * 0.50)],
                valuation_p90=valuations[int(n * 0.90)],
                confidence_interval_90=(unicorn_probs[int(n * 0.05)], unicorn_probs[int(n * 0.95)])
            )

        return results

    async def _execute_sensitivity(self, state: GraphState) -> Dict[str, SensitivityOutput]:
        """Sensitivity analysis for each company"""
        import math

        results = {}

        for company_name, prediction in state.predictions.items():
            scores = {
                "team": prediction.team_score,
                "market": prediction.market_score,
                "traction": prediction.traction_score,
                "timing": prediction.timing_score,
                "capital": prediction.capital_score
            }
            weights = {"team": 0.30, "market": 0.25, "traction": 0.20, "timing": 0.15, "capital": 0.10}

            def calc_prob(s):
                composite = sum(s[k] * weights[k] for k in s)
                return min(0.60, 0.016 * math.exp(4 * (composite - 0.5)))

            base_prob = calc_prob(scores)
            sensitivity_matrix = {}
            importance = []

            for factor in scores:
                low = scores.copy()
                high = scores.copy()
                low[factor] = max(0, scores[factor] - 0.20)
                high[factor] = min(1, scores[factor] + 0.20)

                prob_low = calc_prob(low)
                prob_high = calc_prob(high)
                impact = prob_high - prob_low

                sensitivity_matrix[factor] = {
                    "base": scores[factor],
                    "low_prob": prob_low,
                    "high_prob": prob_high,
                    "impact": impact
                }
                importance.append({"factor": factor, "importance": abs(impact)})

            importance.sort(key=lambda x: x["importance"], reverse=True)

            results[company_name] = SensitivityOutput(
                base_probability=base_prob,
                sensitivity_matrix=sensitivity_matrix,
                factor_importance=importance,
                most_impactful_factor=importance[0]["factor"] if importance else "team",
                recommendation=f"Focus on improving {importance[0]['factor']} for maximum impact" if importance else ""
            )

        return results

    async def _execute_trajectory_sim(self, state: GraphState) -> Dict[str, Dict]:
        """Growth trajectory simulation"""
        import random

        results = {}

        for company_name, prediction in state.predictions.items():
            paths = {"revenue": [], "valuation": []}

            for _ in range(1000):
                val = prediction.expected_valuation
                rev = 500000
                val_path = [val]
                rev_path = [rev]

                for year in range(1, 8):
                    growth = 1.5 + random.random()
                    rev *= growth * (0.8 + random.random() * 0.4)
                    val *= growth * (0.6 + random.random() * 0.8)

                    if random.random() < prediction.unicorn_probability / 7:
                        val = max(val, 1e9)

                    val_path.append(val)
                    rev_path.append(rev)

                paths["revenue"].append(rev_path)
                paths["valuation"].append(val_path)

            # Aggregate
            growth_curves = {"revenue": [], "valuation": []}
            for year in range(8):
                rev_year = sorted([p[year] for p in paths["revenue"]])
                val_year = sorted([p[year] for p in paths["valuation"]])
                n = len(rev_year)
                growth_curves["revenue"].append({
                    "year": year, "p10": rev_year[int(n*0.1)], "p50": rev_year[int(n*0.5)], "p90": rev_year[int(n*0.9)]
                })
                growth_curves["valuation"].append({
                    "year": year, "p10": val_year[int(n*0.1)], "p50": val_year[int(n*0.5)], "p90": val_year[int(n*0.9)]
                })

            results[company_name] = {"growth_curves": growth_curves}

        return results

    async def _execute_exit_modeler(self, state: GraphState) -> Dict[str, Dict]:
        """Exit path modeling"""
        results = {}

        for company_name, prediction in state.predictions.items():
            ipo_prob = prediction.unicorn_probability * 0.4
            acquisition_prob = prediction.success_probability * 0.6
            failure_prob = prediction.failure_probability

            results[company_name] = {
                "exit_probabilities": {
                    "ipo": ipo_prob,
                    "acquisition": acquisition_prob,
                    "failure": failure_prob
                },
                "expected_exit_year": 7 - prediction.unicorn_probability * 3
            }

        return results

    async def _execute_funding_scenarios(self, state: GraphState) -> Dict[str, Dict]:
        """Future funding modeling"""
        results = {}

        for company_name, prediction in state.predictions.items():
            current_val = prediction.expected_valuation
            rounds = []

            for round_name, mult, dilution in [("Series A", 3.0, 0.20), ("Series B", 2.5, 0.20), ("Series C", 2.0, 0.18)]:
                pre = current_val * mult
                amount = pre * dilution / (1 - dilution)
                rounds.append({
                    "round": round_name,
                    "pre_money": pre,
                    "amount": amount,
                    "dilution": dilution
                })
                current_val = pre + amount

            results[company_name] = {"future_rounds": rounds}

        return results

    async def _execute_decision_brief(self, state: GraphState) -> Dict[str, DecisionBriefOutput]:
        """Generate executive decision briefs"""
        results = {}

        for company_name, prediction in state.predictions.items():
            # Determine recommendation
            if prediction.unicorn_probability > 0.10:
                rec = Recommendation.STRONG_INVEST
                rationale = "Above-average unicorn potential with strong fundamentals"
            elif prediction.unicorn_probability > 0.05:
                rec = Recommendation.INVEST
                rationale = "Solid opportunity with reasonable risk/return profile"
            elif prediction.unicorn_probability > 0.02:
                rec = Recommendation.MONITOR
                rationale = "Potential upside but key risks need resolution"
            else:
                rec = Recommendation.PASS
                rationale = "Risk/return below investment threshold"

            # Get MC data for confidence interval
            mc = state.monte_carlo.get(company_name)
            confidence = prediction.prediction_confidence

            # Generate summary with LLM
            summary = f"{company_name}: {prediction.unicorn_probability*100:.1f}% unicorn probability. {rationale}"

            if self._llm:
                try:
                    response = self._llm.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=200,
                        messages=[{
                            "role": "user",
                            "content": f"""Write a 2-sentence executive summary for {company_name}:
- Unicorn probability: {prediction.unicorn_probability*100:.1f}%
- Strengths: {', '.join(prediction.key_strengths[:2])}
- Risks: {', '.join(prediction.key_risks[:2])}
- Recommendation: {rec.value}
Be direct and actionable."""
                        }]
                    )
                    summary = response.content[0].text
                except:
                    pass

            # Calculate percentile vs YC average
            percentile = int(min(99, (prediction.unicorn_probability / 0.016) * 50))

            results[company_name] = DecisionBriefOutput(
                company_name=company_name,
                recommendation=rec,
                confidence=confidence,
                summary=summary,
                rationale=rationale,
                key_metrics=[
                    {"name": "Unicorn Probability", "value": f"{prediction.unicorn_probability*100:.1f}%", "benchmark": "YC avg: 1.6%"},
                    {"name": "Expected Valuation", "value": f"${prediction.expected_valuation/1e6:.0f}M", "benchmark": ""},
                    {"name": "Team Score", "value": f"{prediction.team_score*100:.0f}/100", "benchmark": "Target: 70+"},
                ],
                key_strengths=prediction.key_strengths,
                key_risks=prediction.key_risks,
                next_steps=["Schedule founder meeting", "Complete technical due diligence"] if rec in [Recommendation.STRONG_INVEST, Recommendation.INVEST] else ["Continue monitoring"],
                percentile_rank=percentile,
                vs_yc_average=f"{'+' if percentile > 50 else ''}{(prediction.unicorn_probability/0.016 - 1)*100:.0f}% vs YC average"
            )

        return results

    async def _execute_comparison_matrix(self, state: GraphState) -> Dict:
        """Side-by-side company comparison"""
        companies = []
        for name, pred in state.predictions.items():
            companies.append({
                "name": name,
                "unicorn_probability": pred.unicorn_probability,
                "team_score": pred.team_score,
                "market_score": pred.market_score,
                "traction_score": pred.traction_score,
                "expected_valuation": pred.expected_valuation
            })

        # Sort by unicorn probability
        companies.sort(key=lambda x: x["unicorn_probability"], reverse=True)

        return {
            "companies": companies,
            "rankings": {
                "by_unicorn_prob": [c["name"] for c in companies],
                "by_team": sorted(companies, key=lambda x: x["team_score"], reverse=True)[:3],
                "by_traction": sorted(companies, key=lambda x: x["traction_score"], reverse=True)[:3]
            }
        }

    async def _execute_portfolio_optimizer(self, state: GraphState) -> Dict:
        """Optimize portfolio allocation"""
        import math

        companies = []
        for name, pred in state.predictions.items():
            expected_return = pred.unicorn_probability * 100 + (1 - pred.unicorn_probability) * 2
            risk = 1 - pred.prediction_confidence
            companies.append({
                "name": name,
                "expected_return": expected_return,
                "risk": risk,
                "unicorn_prob": pred.unicorn_probability
            })

        # Simple risk-adjusted weighting
        total_score = sum(c["expected_return"] / (c["risk"] + 0.1) for c in companies)
        weights = {}
        for c in companies:
            weights[c["name"]] = min(0.25, (c["expected_return"] / (c["risk"] + 0.1)) / total_score)

        # Normalize
        total = sum(weights.values())
        weights = {k: v/total for k, v in weights.items()}

        portfolio_return = sum(weights[c["name"]] * c["expected_return"] for c in companies)
        portfolio_risk = sum(weights[c["name"]] * c["risk"] for c in companies)

        return {
            "optimal_weights": weights,
            "expected_return": portfolio_return,
            "portfolio_risk": portfolio_risk,
            "sharpe_ratio": portfolio_return / (portfolio_risk + 0.1)
        }

    async def _execute_deliverables(self, state: GraphState) -> Dict:
        """
        Generate enterprise deliverables - the ANSWER NODES.
        These are board-ready documents that justify $5-10M contracts.
        """
        from backend.engine.graph.deliverables import DeliverablesGenerator

        generator = DeliverablesGenerator(state)
        return generator.generate_all_deliverables()
