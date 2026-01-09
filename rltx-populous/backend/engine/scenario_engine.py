"""
Scenario Branching Engine
Generates explorable futures with probability trees
"In 73% of futures, you retain. In 15%, competitor responds. In 12%, market shifts."
"""

import os
import random
import numpy as np
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict
from anthropic import Anthropic

from backend.models.scenario_branch import (
    ScenarioTree, ScenarioNode, ScenarioPath, ScenarioCluster,
    ScenarioMetrics, ScenarioOutcome, BranchType, ScenarioBranchInput,
    ScenarioSummary
)
from backend.models.competitor_agent import (
    CompetitorAgent, MarketState, MoveType, CompetitorMove
)
from backend.engine.competitor_engine import CompetitorEngine


class ScenarioEngine:
    """
    Engine for generating and analyzing scenario branches.
    Creates explorable decision trees with probability distributions.
    """

    def __init__(self, llm_client: Anthropic = None):
        self.llm = llm_client or Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.competitor_engine = CompetitorEngine(llm_client=self.llm)

    async def generate_scenario_tree(
        self,
        input_data: ScenarioBranchInput,
        competitors: List[CompetitorAgent],
        market_state: Optional[MarketState] = None
    ) -> ScenarioTree:
        """
        Generate a complete scenario tree from a decision.
        """
        if market_state is None:
            market_state = MarketState()

        tree = ScenarioTree(
            decision_id=input_data.decision_id,
        )

        # Create root node (your move)
        root = ScenarioNode(
            branch_type=BranchType.YOUR_MOVE,
            actor=input_data.company_name,
            action=input_data.your_move.get("type", "strategic_move"),
            description=self._describe_move(input_data.your_move),
            probability=1.0,
            cumulative_probability=1.0,
            time_offset_days=0,
            metrics=ScenarioMetrics(
                market_share=market_state.our_share,
                customer_retention=0.95,
                competitive_position=0.0
            )
        )

        tree.nodes[root.id] = root
        tree.root_id = root.id

        # Generate branches recursively
        await self._expand_node(
            tree=tree,
            node=root,
            competitors=competitors,
            market_state=market_state,
            your_move=input_data.your_move,
            max_depth=input_data.max_depth,
            branch_factor=input_data.branch_factor,
            time_horizon=input_data.time_horizon_days,
            include_market_events=input_data.include_market_events
        )

        # Compute all paths through the tree
        tree.paths = self._compute_paths(tree)

        # Cluster paths by outcome
        tree.clusters = self._cluster_paths(tree)

        # Calculate outcome probabilities
        tree.outcome_probabilities = self._calculate_outcome_probabilities(tree)

        # Calculate expected metrics
        tree.expected_metrics = self._calculate_expected_metrics(tree)

        # Identify key insights
        tree.dominant_scenarios = self._find_dominant_scenarios(tree)
        tree.critical_uncertainties = self._find_critical_uncertainties(tree)
        tree.recommended_hedges = self._generate_hedges(tree)

        # Update metadata
        tree.max_depth = max((n.depth for n in tree.nodes.values()), default=0)
        tree.total_nodes = len(tree.nodes)
        tree.total_paths = len(tree.paths)

        return tree

    async def _expand_node(
        self,
        tree: ScenarioTree,
        node: ScenarioNode,
        competitors: List[CompetitorAgent],
        market_state: MarketState,
        your_move: Dict,
        max_depth: int,
        branch_factor: int,
        time_horizon: int,
        include_market_events: bool,
        current_depth: int = 0
    ):
        """
        Recursively expand a node with possible branches.
        """
        if current_depth >= max_depth:
            # Assign final outcome at leaf nodes
            node.outcome = self._determine_outcome(node.metrics, market_state)
            return

        branches = []

        # 1. Competitor responses (if we haven't seen competitor response yet)
        if node.branch_type != BranchType.COMPETITOR_RESPONSE:
            for competitor in competitors:
                response_probs = competitor.get_response_probability(your_move)

                # Get top responses by probability
                sorted_responses = sorted(
                    response_probs.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:branch_factor]

                for response_desc, prob in sorted_responses:
                    if prob < 0.05:  # Skip very unlikely responses
                        continue

                    response_metrics = self._project_metrics_from_response(
                        node.metrics, response_desc, competitor
                    )

                    branch = ScenarioNode(
                        parent_id=node.id,
                        depth=current_depth + 1,
                        branch_type=BranchType.COMPETITOR_RESPONSE,
                        actor=competitor.name,
                        action=response_desc,
                        description=f"{competitor.name}: {response_desc}",
                        probability=prob,
                        cumulative_probability=node.cumulative_probability * prob,
                        time_offset_days=node.time_offset_days + self._estimate_delay(response_desc),
                        metrics=response_metrics,
                        key_drivers=[f"Response to {your_move.get('type', 'your move')}"]
                    )
                    branches.append(branch)

        # 2. Customer reactions
        customer_branches = self._generate_customer_reactions(
            node, your_move, market_state, branch_factor
        )
        branches.extend(customer_branches)

        # 3. Market events (external shocks)
        if include_market_events and random.random() < 0.3:
            market_branches = self._generate_market_events(
                node, time_horizon, branch_factor
            )
            branches.extend(market_branches)

        # Normalize probabilities
        if branches:
            total_prob = sum(b.probability for b in branches)
            if total_prob > 0:
                for b in branches:
                    b.probability = b.probability / total_prob
                    b.cumulative_probability = node.cumulative_probability * b.probability

        # Add branches to tree and expand recursively
        for branch in branches[:branch_factor]:
            tree.nodes[branch.id] = branch
            node.children_ids.append(branch.id)

            await self._expand_node(
                tree=tree,
                node=branch,
                competitors=competitors,
                market_state=market_state,
                your_move=your_move,
                max_depth=max_depth,
                branch_factor=branch_factor,
                time_horizon=time_horizon,
                include_market_events=include_market_events,
                current_depth=current_depth + 1
            )

        # If no branches, this is a leaf node
        if not node.children_ids:
            node.outcome = self._determine_outcome(node.metrics, market_state)

    def _generate_customer_reactions(
        self,
        node: ScenarioNode,
        your_move: Dict,
        market_state: MarketState,
        branch_factor: int
    ) -> List[ScenarioNode]:
        """
        Generate possible customer reactions to moves.
        """
        reactions = []
        move_type = your_move.get("type", "")

        if move_type == "price_change":
            percent = your_move.get("percent", 0)

            if percent > 0:  # Price increase
                # Some customers accept
                accept_prob = max(0.3, 0.8 - abs(percent) * 0.03)
                reactions.append(ScenarioNode(
                    parent_id=node.id,
                    depth=node.depth + 1,
                    branch_type=BranchType.CUSTOMER_REACTION,
                    actor="Customers",
                    action="accept_price_increase",
                    description=f"Customers accept {percent}% price increase",
                    probability=accept_prob,
                    time_offset_days=node.time_offset_days + 30,
                    metrics=ScenarioMetrics(
                        market_share=node.metrics.market_share * 0.95,
                        revenue_impact=percent * 0.9,  # Some churn
                        customer_retention=0.9
                    ),
                    opportunities=["Increased revenue per customer"]
                ))

                # Some customers churn
                churn_prob = 1 - accept_prob
                reactions.append(ScenarioNode(
                    parent_id=node.id,
                    depth=node.depth + 1,
                    branch_type=BranchType.CUSTOMER_REACTION,
                    actor="Customers",
                    action="price_sensitive_churn",
                    description=f"Price-sensitive customers churn",
                    probability=churn_prob,
                    time_offset_days=node.time_offset_days + 14,
                    metrics=ScenarioMetrics(
                        market_share=node.metrics.market_share * 0.85,
                        revenue_impact=-10,
                        customer_retention=0.75
                    ),
                    risks=["Customer churn accelerates", "Competitor gains customers"]
                ))

            else:  # Price decrease
                reactions.append(ScenarioNode(
                    parent_id=node.id,
                    depth=node.depth + 1,
                    branch_type=BranchType.CUSTOMER_REACTION,
                    actor="Customers",
                    action="attracted_by_lower_price",
                    description="New customers attracted by lower price",
                    probability=0.6,
                    time_offset_days=node.time_offset_days + 21,
                    metrics=ScenarioMetrics(
                        market_share=node.metrics.market_share * 1.1,
                        revenue_impact=abs(percent) * -0.5,  # Lower margin but more volume
                        customer_retention=0.95
                    ),
                    opportunities=["Market share expansion", "Customer acquisition"]
                ))

        elif move_type == "feature_launch":
            reactions.append(ScenarioNode(
                parent_id=node.id,
                depth=node.depth + 1,
                branch_type=BranchType.CUSTOMER_REACTION,
                actor="Customers",
                action="feature_adoption",
                description="Customers adopt new feature",
                probability=0.65,
                time_offset_days=node.time_offset_days + 30,
                metrics=ScenarioMetrics(
                    market_share=node.metrics.market_share * 1.05,
                    customer_retention=0.97,
                    competitive_position=0.1
                ),
                opportunities=["Increased product stickiness"]
            ))

        return reactions

    def _generate_market_events(
        self,
        node: ScenarioNode,
        time_horizon: int,
        branch_factor: int
    ) -> List[ScenarioNode]:
        """
        Generate possible market events (external shocks).
        """
        events = []

        # Economic downturn
        events.append(ScenarioNode(
            parent_id=node.id,
            depth=node.depth + 1,
            branch_type=BranchType.MARKET_EVENT,
            actor="Market",
            action="economic_downturn",
            description="Economic conditions worsen, budgets tighten",
            probability=0.15,
            time_offset_days=node.time_offset_days + 45,
            metrics=ScenarioMetrics(
                market_share=node.metrics.market_share * 0.95,
                revenue_impact=-15,
                risk_exposure=0.7
            ),
            risks=["Budget cuts", "Delayed decisions", "Focus on cost reduction"]
        ))

        # New market entrant
        events.append(ScenarioNode(
            parent_id=node.id,
            depth=node.depth + 1,
            branch_type=BranchType.MARKET_EVENT,
            actor="Market",
            action="new_entrant",
            description="New competitor enters market",
            probability=0.1,
            time_offset_days=node.time_offset_days + 60,
            metrics=ScenarioMetrics(
                market_share=node.metrics.market_share * 0.9,
                competitive_position=-0.2,
                risk_exposure=0.5
            ),
            risks=["Increased competition", "Pricing pressure"]
        ))

        # Regulatory change
        events.append(ScenarioNode(
            parent_id=node.id,
            depth=node.depth + 1,
            branch_type=BranchType.MARKET_EVENT,
            actor="Market",
            action="regulatory_change",
            description="Regulatory environment shifts",
            probability=0.08,
            time_offset_days=node.time_offset_days + 90,
            metrics=ScenarioMetrics(
                risk_exposure=0.6
            ),
            risks=["Compliance costs", "Operational changes required"]
        ))

        return events

    def _describe_move(self, move: Dict) -> str:
        """Generate human-readable description of a move."""
        move_type = move.get("type", "strategic_move")
        if move_type == "price_change":
            percent = move.get("percent", 0)
            direction = "increase" if percent > 0 else "decrease"
            return f"Price {direction} of {abs(percent)}%"
        elif move_type == "feature_launch":
            features = move.get("features", ["new feature"])
            return f"Launch: {', '.join(features)}"
        elif move_type == "marketing_campaign":
            return f"Marketing campaign: {move.get('message', 'brand awareness')}"
        return str(move)

    def _project_metrics_from_response(
        self,
        current_metrics: ScenarioMetrics,
        response_desc: str,
        competitor: CompetitorAgent
    ) -> ScenarioMetrics:
        """Project metrics based on competitor response."""
        metrics = ScenarioMetrics(
            market_share=current_metrics.market_share,
            revenue_impact=current_metrics.revenue_impact,
            customer_retention=current_metrics.customer_retention,
            competitive_position=current_metrics.competitive_position,
            risk_exposure=current_metrics.risk_exposure
        )

        response_lower = response_desc.lower()

        if "no_response" in response_lower:
            metrics.competitive_position += 0.1
            metrics.market_share *= 1.02

        elif "price" in response_lower and ("cut" in response_lower or "reduction" in response_lower or "undercut" in response_lower):
            metrics.competitive_position -= 0.15
            metrics.market_share *= 0.97
            metrics.risk_exposure += 0.2

        elif "match" in response_lower:
            # Maintain status quo
            metrics.competitive_position *= 0.95

        elif "feature" in response_lower:
            metrics.competitive_position -= 0.1
            metrics.customer_retention *= 0.98

        elif "marketing" in response_lower or "campaign" in response_lower:
            metrics.competitive_position -= 0.05
            metrics.market_share *= 0.98

        return metrics

    def _estimate_delay(self, response_desc: str) -> int:
        """Estimate time delay for a response."""
        response_lower = response_desc.lower()

        if "immediate" in response_lower:
            return 3
        elif "no_response" in response_lower:
            return 0
        elif "price" in response_lower:
            return 7
        elif "feature" in response_lower:
            return 30
        elif "marketing" in response_lower:
            return 14
        else:
            return 14

    def _determine_outcome(
        self,
        metrics: ScenarioMetrics,
        initial_state: MarketState
    ) -> ScenarioOutcome:
        """Determine the outcome category for a leaf node."""
        # Compare final metrics to initial state
        share_change = metrics.market_share / initial_state.our_share if initial_state.our_share > 0 else 1

        if share_change > 1.1 and metrics.competitive_position > 0:
            return ScenarioOutcome.FAVORABLE
        elif share_change < 0.9 or metrics.competitive_position < -0.2:
            return ScenarioOutcome.UNFAVORABLE
        elif metrics.risk_exposure > 0.6:
            return ScenarioOutcome.ESCALATION
        else:
            return ScenarioOutcome.NEUTRAL

    def _compute_paths(self, tree: ScenarioTree) -> List[ScenarioPath]:
        """Compute all paths from root to leaves."""
        paths = []

        def dfs(node_id: str, current_path: List[str]):
            node = tree.nodes.get(node_id)
            if not node:
                return

            current_path.append(node_id)

            if not node.children_ids:  # Leaf node
                path = ScenarioPath(
                    node_ids=current_path.copy(),
                    total_probability=node.cumulative_probability,
                    final_outcome=node.outcome or ScenarioOutcome.NEUTRAL,
                    final_metrics=node.metrics,
                    narrative=self._generate_narrative(tree, current_path),
                    key_events=[tree.nodes[nid].description for nid in current_path]
                )
                paths.append(path)
            else:
                for child_id in node.children_ids:
                    dfs(child_id, current_path)

            current_path.pop()

        dfs(tree.root_id, [])
        return paths

    def _generate_narrative(self, tree: ScenarioTree, path: List[str]) -> str:
        """Generate a narrative description of a path."""
        events = []
        for node_id in path:
            node = tree.nodes.get(node_id)
            if node and node.description:
                events.append(node.description)

        return " → ".join(events)

    def _cluster_paths(self, tree: ScenarioTree) -> List[ScenarioCluster]:
        """Cluster paths by outcome."""
        outcome_paths = defaultdict(list)

        for path in tree.paths:
            outcome_paths[path.final_outcome].append(path)

        clusters = []
        for outcome, paths in outcome_paths.items():
            if not paths:
                continue

            total_prob = sum(p.total_probability for p in paths)

            # Calculate average metrics
            avg_metrics = ScenarioMetrics(
                market_share=np.mean([p.final_metrics.market_share for p in paths]),
                revenue_impact=np.mean([p.final_metrics.revenue_impact for p in paths]),
                customer_retention=np.mean([p.final_metrics.customer_retention for p in paths]),
                competitive_position=np.mean([p.final_metrics.competitive_position for p in paths]),
                risk_exposure=np.mean([p.final_metrics.risk_exposure for p in paths])
            )

            cluster = ScenarioCluster(
                name=f"{outcome.value.title()} Outcomes",
                description=self._describe_outcome_cluster(outcome, len(paths)),
                outcome=outcome,
                path_ids=[p.id for p in paths],
                total_probability=total_prob,
                avg_metrics=avg_metrics,
                typical_narrative=paths[0].narrative if paths else ""
            )
            clusters.append(cluster)

        return sorted(clusters, key=lambda c: c.total_probability, reverse=True)

    def _describe_outcome_cluster(self, outcome: ScenarioOutcome, count: int) -> str:
        """Generate description for an outcome cluster."""
        descriptions = {
            ScenarioOutcome.FAVORABLE: f"{count} scenarios where you gain competitive advantage",
            ScenarioOutcome.NEUTRAL: f"{count} scenarios with status quo maintained",
            ScenarioOutcome.UNFAVORABLE: f"{count} scenarios where competitors gain ground",
            ScenarioOutcome.ESCALATION: f"{count} scenarios with competitive escalation",
            ScenarioOutcome.MARKET_SHIFT: f"{count} scenarios with external market disruption"
        }
        return descriptions.get(outcome, f"{count} scenarios")

    def _calculate_outcome_probabilities(self, tree: ScenarioTree) -> Dict[str, float]:
        """Calculate probability of each outcome category."""
        probs = defaultdict(float)

        for path in tree.paths:
            probs[path.final_outcome.value] += path.total_probability

        # Normalize
        total = sum(probs.values())
        if total > 0:
            for key in probs:
                probs[key] = round(probs[key] / total, 3)

        return dict(probs)

    def _calculate_expected_metrics(self, tree: ScenarioTree) -> ScenarioMetrics:
        """Calculate probability-weighted expected metrics."""
        if not tree.paths:
            return ScenarioMetrics()

        total_prob = sum(p.total_probability for p in tree.paths)
        if total_prob == 0:
            return ScenarioMetrics()

        expected = ScenarioMetrics(
            market_share=sum(p.final_metrics.market_share * p.total_probability for p in tree.paths) / total_prob,
            revenue_impact=sum(p.final_metrics.revenue_impact * p.total_probability for p in tree.paths) / total_prob,
            customer_retention=sum(p.final_metrics.customer_retention * p.total_probability for p in tree.paths) / total_prob,
            competitive_position=sum(p.final_metrics.competitive_position * p.total_probability for p in tree.paths) / total_prob,
            risk_exposure=sum(p.final_metrics.risk_exposure * p.total_probability for p in tree.paths) / total_prob
        )

        return expected

    def _find_dominant_scenarios(self, tree: ScenarioTree) -> List[str]:
        """Find the most likely paths."""
        sorted_paths = sorted(tree.paths, key=lambda p: p.total_probability, reverse=True)
        return [p.id for p in sorted_paths[:3]]

    def _find_critical_uncertainties(self, tree: ScenarioTree) -> List[str]:
        """Identify the most impactful decision points."""
        uncertainties = []

        # Find nodes with high variance in child outcomes
        for node_id, node in tree.nodes.items():
            if not node.children_ids:
                continue

            children = [tree.nodes[cid] for cid in node.children_ids if cid in tree.nodes]
            if len(children) < 2:
                continue

            # Calculate variance in outcomes
            outcomes = [c.outcome.value if c.outcome else "neutral" for c in children]
            if len(set(outcomes)) > 1:
                uncertainties.append(f"Uncertainty at: {node.description}")

        return uncertainties[:5]

    def _generate_hedges(self, tree: ScenarioTree) -> List[str]:
        """Generate recommended hedging strategies."""
        hedges = []

        # Based on outcome probabilities
        probs = tree.outcome_probabilities

        if probs.get("unfavorable", 0) > 0.2:
            hedges.append("Prepare contingency for competitive response")

        if probs.get("escalation", 0) > 0.15:
            hedges.append("Establish price floor to prevent race to bottom")

        if probs.get("market_shift", 0) > 0.1:
            hedges.append("Monitor external market indicators closely")

        if probs.get("favorable", 0) > 0.5:
            hedges.append("Prepare to capitalize on favorable conditions")

        return hedges or ["Monitor situation and maintain flexibility"]

    def generate_summary(
        self,
        tree: ScenarioTree,
        decision_title: str
    ) -> ScenarioSummary:
        """Generate a human-readable summary of the scenario analysis."""
        probs = tree.outcome_probabilities

        # Generate headline
        favorable_prob = probs.get("favorable", 0)
        unfavorable_prob = probs.get("unfavorable", 0)

        if favorable_prob > 0.5:
            headline = f"{int(favorable_prob * 100)}% chance of favorable outcome"
        elif unfavorable_prob > 0.3:
            headline = f"Caution: {int(unfavorable_prob * 100)}% chance of unfavorable outcome"
        else:
            headline = "Balanced outlook with moderate uncertainty"

        # Find best, worst, most likely cases
        sorted_paths = sorted(tree.paths, key=lambda p: p.total_probability, reverse=True)

        favorable_paths = [p for p in tree.paths if p.final_outcome == ScenarioOutcome.FAVORABLE]
        unfavorable_paths = [p for p in tree.paths if p.final_outcome == ScenarioOutcome.UNFAVORABLE]

        best_case = {}
        if favorable_paths:
            best = max(favorable_paths, key=lambda p: p.total_probability)
            best_case = {
                "probability": best.total_probability,
                "narrative": best.narrative,
                "metrics": best.final_metrics.model_dump()
            }

        worst_case = {}
        if unfavorable_paths:
            worst = max(unfavorable_paths, key=lambda p: p.total_probability)
            worst_case = {
                "probability": worst.total_probability,
                "narrative": worst.narrative,
                "metrics": worst.final_metrics.model_dump()
            }

        most_likely = {}
        if sorted_paths:
            likely = sorted_paths[0]
            most_likely = {
                "probability": likely.total_probability,
                "narrative": likely.narrative,
                "outcome": likely.final_outcome.value,
                "metrics": likely.final_metrics.model_dump()
            }

        # Gather risks and opportunities
        risks = set()
        opportunities = set()
        for node in tree.nodes.values():
            risks.update(node.risks)
            opportunities.update(node.opportunities)

        return ScenarioSummary(
            tree_id=tree.id,
            decision_title=decision_title,
            headline=headline,
            outcomes=[
                {"outcome": k, "probability": v, "description": self._describe_outcome_cluster(ScenarioOutcome(k), 0)}
                for k, v in sorted(probs.items(), key=lambda x: x[1], reverse=True)
            ],
            best_case=best_case,
            worst_case=worst_case,
            most_likely=most_likely,
            key_risks=list(risks)[:5],
            key_opportunities=list(opportunities)[:5],
            recommended_actions=tree.recommended_hedges,
            tree_visualization_data=self._prepare_visualization_data(tree)
        )

    def _prepare_visualization_data(self, tree: ScenarioTree) -> Dict[str, Any]:
        """Prepare data for D3 visualization."""
        nodes = []
        links = []

        for node_id, node in tree.nodes.items():
            nodes.append({
                "id": node.id,
                "label": node.description[:50] if node.description else node.action,
                "type": node.branch_type.value,
                "actor": node.actor,
                "probability": node.probability,
                "cumulative_probability": node.cumulative_probability,
                "outcome": node.outcome.value if node.outcome else None,
                "depth": node.depth,
                "time_offset_days": node.time_offset_days
            })

            if node.parent_id:
                links.append({
                    "source": node.parent_id,
                    "target": node.id,
                    "probability": node.probability
                })

        return {
            "nodes": nodes,
            "links": links,
            "outcome_probabilities": tree.outcome_probabilities,
            "clusters": [
                {
                    "name": c.name,
                    "outcome": c.outcome.value,
                    "probability": c.total_probability,
                    "path_count": len(c.path_ids)
                }
                for c in tree.clusters
            ]
        }

    async def run_monte_carlo(
        self,
        input_data: ScenarioBranchInput,
        competitors: List[CompetitorAgent],
        num_simulations: int = 100
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation to estimate outcome distributions.
        """
        outcome_counts = defaultdict(int)
        metric_samples = defaultdict(list)

        for i in range(num_simulations):
            # Generate a single path through random choices
            outcome, metrics = await self._simulate_single_path(
                input_data, competitors
            )
            outcome_counts[outcome.value] += 1

            metric_samples["market_share"].append(metrics.market_share)
            metric_samples["revenue_impact"].append(metrics.revenue_impact)
            metric_samples["customer_retention"].append(metrics.customer_retention)

        # Calculate statistics
        return {
            "num_simulations": num_simulations,
            "outcome_distribution": {
                k: v / num_simulations for k, v in outcome_counts.items()
            },
            "metric_statistics": {
                metric: {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "p5": np.percentile(values, 5),
                    "p50": np.percentile(values, 50),
                    "p95": np.percentile(values, 95)
                }
                for metric, values in metric_samples.items()
            }
        }

    async def _simulate_single_path(
        self,
        input_data: ScenarioBranchInput,
        competitors: List[CompetitorAgent]
    ) -> Tuple[ScenarioOutcome, ScenarioMetrics]:
        """Simulate a single random path through the scenario tree."""
        metrics = ScenarioMetrics(
            market_share=0.2,
            customer_retention=0.95,
            competitive_position=0.0
        )

        # Simulate competitor responses
        for competitor in competitors:
            response_probs = competitor.get_response_probability(input_data.your_move)

            # Weighted random choice
            choices = list(response_probs.keys())
            probs = list(response_probs.values())
            chosen = random.choices(choices, weights=probs, k=1)[0]

            # Update metrics based on response
            metrics = self._project_metrics_from_response(metrics, chosen, competitor)

        # Simulate customer reaction
        if random.random() < 0.3:
            metrics.customer_retention *= 0.95

        # Simulate market event
        if random.random() < 0.1:
            metrics.market_share *= 0.9
            metrics.risk_exposure = 0.5

        # Determine outcome
        outcome = self._determine_outcome(metrics, MarketState())

        return outcome, metrics
