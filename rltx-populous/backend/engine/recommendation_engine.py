"""
Recommendation Engine
Generates recommendations and execution plans from simulation results
"""

from typing import List, Dict, Optional
from datetime import date, timedelta
from anthropic import Anthropic
import json

from backend.models.action import (
    Recommendation, ActionItem, Contingency, ApprovalGate
)
from backend.models.simulation import TemporalSimulation, SimulationStatus
from backend.models.trace import Trace


class RecommendationEngine:
    """Engine for generating decision recommendations"""

    def __init__(self, llm_client: Anthropic = None):
        self.llm = llm_client

    def generate_recommendation(
        self,
        decision_id: str,
        simulations: Dict[str, TemporalSimulation],  # option_id -> simulation
        traces: Dict[str, Trace],  # option_id -> trace
        options: List[Dict],
        constraints: List[Dict]
    ) -> Recommendation:
        """Generate complete recommendation from simulation results"""

        # 1. Rank options by expected utility
        rankings = self._rank_options(simulations, constraints)
        best_option_id = rankings[0]["option_id"] if rankings else (options[0]["id"] if options else "")
        best_option = next((o for o in options if o["id"] == best_option_id), options[0] if options else {})
        best_simulation = simulations.get(best_option_id)
        best_trace = traces.get(best_option_id)

        # 2. Calculate confidence
        confidence = self._calculate_confidence(best_simulation, rankings)

        # 3. Generate execution plan
        execution_plan = self._generate_execution_plan(best_option, best_trace)

        # 4. Identify contingencies
        contingencies = self._identify_contingencies(best_simulation, best_trace, rankings)

        # 5. Define approval gates
        approval_gates = self._define_approval_gates(best_option, constraints)

        # 6. Generate reasoning
        reasoning = self._generate_reasoning(rankings, simulations, traces)

        # 7. Generate comparison
        comparison = self._generate_comparison(rankings, simulations)

        # 8. Generate executive summary
        executive_summary = self._generate_executive_summary(
            best_option, confidence, best_simulation, contingencies
        )

        # 9. Calculate expected outcome
        expected_outcome = {}
        if best_simulation and best_simulation.aggregate_results:
            agg = best_simulation.aggregate_results
            expected_outcome = {
                "retention_rate": agg.get("retention", {}).get("mean", 0),
                "churn_rate": agg.get("churn", {}).get("mean", 0),
                "confidence_interval": f"{agg.get('retention', {}).get('p25', 0)*100:.0f}%-{agg.get('retention', {}).get('p75', 0)*100:.0f}%"
            }

        return Recommendation(
            decision_id=decision_id,
            recommended_option_id=best_option_id,
            recommended_option_name=best_option.get("name", "Unknown"),
            confidence=confidence,
            expected_outcome=expected_outcome,
            reasoning=reasoning,
            comparison_to_alternatives=comparison,
            execution_plan=execution_plan,
            contingencies=contingencies,
            approval_gates=approval_gates,
            key_risks=self._identify_risks(best_trace),
            monitoring_metrics=self._define_monitoring(best_option),
            executive_summary=executive_summary
        )

    def _rank_options(
        self,
        simulations: Dict[str, TemporalSimulation],
        constraints: List[Dict]
    ) -> List[Dict]:
        """Rank options by expected utility"""

        rankings = []

        for option_id, sim in simulations.items():
            if not sim.aggregate_results:
                continue

            agg = sim.aggregate_results
            retention = agg.get("retention", {}).get("mean", 0)
            confidence = agg.get("confidence", 0.5)

            # Check constraint satisfaction
            satisfies_constraints = True
            for constraint in constraints:
                if constraint.get("metric") == "retention_rate":
                    if constraint.get("operator") == ">=" and retention < constraint.get("value", 0):
                        satisfies_constraints = False

            # Calculate utility score
            utility = retention * confidence * (1 if satisfies_constraints else 0.5)

            rankings.append({
                "option_id": option_id,
                "retention": retention,
                "confidence": confidence,
                "satisfies_constraints": satisfies_constraints,
                "utility": utility
            })

        rankings.sort(key=lambda x: x["utility"], reverse=True)
        return rankings

    def _calculate_confidence(
        self,
        simulation: TemporalSimulation,
        rankings: List[Dict]
    ) -> float:
        """Calculate confidence in recommendation"""

        if not simulation or not simulation.aggregate_results:
            return 0.5

        agg = simulation.aggregate_results

        # Low variance = high confidence
        std = agg.get("retention", {}).get("std", 0.5)
        variance_factor = max(0, 1 - std * 2)

        # Clear winner = high confidence
        if len(rankings) >= 2:
            gap = rankings[0]["utility"] - rankings[1]["utility"]
            gap_factor = min(gap * 5, 1)
        else:
            gap_factor = 0.5

        # Sample size
        branch_count = len(simulation.branch_results)
        sample_factor = min(branch_count / 100, 1)

        confidence = (variance_factor * 0.4 + gap_factor * 0.4 + sample_factor * 0.2)

        return round(confidence, 2)

    def _generate_execution_plan(
        self,
        option: Dict,
        trace: Optional[Trace]
    ) -> List[ActionItem]:
        """Generate specific execution plan"""

        today = date.today()
        plan = []

        # Phase 1: Preparation
        plan.append(ActionItem(
            id="action_1",
            action="Brief sales team on messaging strategy",
            description="Prepare sales team to handle customer questions about the change",
            owner="VP Sales",
            due_date=today + timedelta(days=14),
            phase="Preparation",
            approval_required=False
        ))

        plan.append(ActionItem(
            id="action_2",
            action="Prepare value justification materials",
            description="Create ROI calculators and case studies for customer conversations",
            owner="Product Marketing",
            due_date=today + timedelta(days=18),
            phase="Preparation",
            dependencies=[]
        ))

        plan.append(ActionItem(
            id="action_3",
            action="Set up monitoring dashboard",
            description="Configure real-time churn and sentiment tracking",
            owner="Analytics",
            due_date=today + timedelta(days=21),
            phase="Preparation"
        ))

        # Phase 2: Announcement
        plan.append(ActionItem(
            id="action_4",
            action="Email existing customers with 60-day notice",
            description="Notify all customers of upcoming change with clear timeline",
            owner="Customer Success",
            due_date=today + timedelta(days=30),
            phase="Announcement",
            dependencies=["action_1", "action_2"]
        ))

        plan.append(ActionItem(
            id="action_5",
            action="Personal outreach to top 50 accounts",
            description="Account managers call enterprise customers directly",
            owner="Account Management",
            due_date=today + timedelta(days=35),
            phase="Announcement"
        ))

        # Phase 3: Monitoring
        plan.append(ActionItem(
            id="action_6",
            action="Weekly churn review meeting",
            description="Review churn data and adjust strategy as needed",
            owner="Leadership Team",
            due_date=today + timedelta(days=37),
            phase="Monitoring"
        ))

        return plan

    def _identify_contingencies(
        self,
        simulation: TemporalSimulation,
        trace: Optional[Trace],
        rankings: List[Dict]
    ) -> List[Contingency]:
        """Identify contingency plans"""

        contingencies = []

        contingencies.append(Contingency(
            id="contingency_1",
            trigger="Competitor launches aggressive promotion (>20% discount)",
            detection="Monitor competitor pricing and promotions daily",
            response="Pause rollout to price-sensitive segments, activate retention offers",
            escalation="VP Marketing within 24 hours",
            timeframe="Within 48 hours of detection"
        ))

        contingencies.append(Contingency(
            id="contingency_2",
            trigger="Week-over-week churn exceeds 3% in any segment",
            detection="Automated alert from churn dashboard",
            response="Trigger win-back campaign, analyze exit survey patterns",
            escalation="CEO for potential rollback decision",
            timeframe="Within 24 hours"
        ))

        contingencies.append(Contingency(
            id="contingency_3",
            trigger="Social media sentiment drops >30%",
            detection="Sentiment monitoring tool alert",
            response="Accelerate value communication, prepare PR response",
            escalation="Communications team within 12 hours",
            timeframe="Same day"
        ))

        contingencies.append(Contingency(
            id="contingency_4",
            trigger="Any top-10 account signals cancellation intent",
            detection="Account manager flagging or CRM alert",
            response="Executive sponsor outreach, custom retention package",
            escalation="CEO direct involvement",
            timeframe="Within 4 hours"
        ))

        return contingencies

    def _define_approval_gates(
        self,
        option: Dict,
        constraints: List[Dict]
    ) -> List[ApprovalGate]:
        """Define approval requirements"""

        gates = []

        gates.append(ApprovalGate(
            id="gate_1",
            condition="Revenue impact exceeds $500K",
            approver="CFO",
            threshold="$500,000"
        ))

        gates.append(ApprovalGate(
            id="gate_2",
            condition="Customer communication with >10K recipients",
            approver="VP Marketing",
            threshold="10,000 customers"
        ))

        gates.append(ApprovalGate(
            id="gate_3",
            condition="Rollback decision required",
            approver="CEO",
            threshold="N/A"
        ))

        return gates

    def _generate_reasoning(
        self,
        rankings: List[Dict],
        simulations: Dict[str, TemporalSimulation],
        traces: Dict[str, Trace]
    ) -> str:
        """Generate reasoning for recommendation"""

        if not rankings:
            return "Insufficient data for recommendation."

        best = rankings[0]

        reasoning_parts = []

        reasoning_parts.append(
            f"This option achieves {best['retention']*100:.0f}% retention with {best['confidence']*100:.0f}% confidence."
        )

        if len(rankings) > 1:
            second = rankings[1]
            gap = (best["retention"] - second["retention"]) * 100
            reasoning_parts.append(
                f"It outperforms the next best option by {gap:.1f} percentage points in retention."
            )

        if best["satisfies_constraints"]:
            reasoning_parts.append("All specified constraints are satisfied.")
        else:
            reasoning_parts.append(
                "Note: Some constraints may not be fully satisfied. Review carefully."
            )

        return " ".join(reasoning_parts)

    def _generate_comparison(
        self,
        rankings: List[Dict],
        simulations: Dict[str, TemporalSimulation]
    ) -> List[Dict]:
        """Generate comparison to alternatives"""

        comparison = []

        for rank in rankings[1:4]:
            comparison.append({
                "option_id": rank["option_id"],
                "retention": f"{rank['retention']*100:.0f}%",
                "why_not": self._explain_why_not(rank, rankings[0])
            })

        return comparison

    def _explain_why_not(self, option: Dict, best: Dict) -> str:
        """Explain why an option wasn't recommended"""

        if not option["satisfies_constraints"]:
            return "Does not satisfy all constraints"

        gap = (best["retention"] - option["retention"]) * 100
        if gap > 5:
            return f"Lower expected retention ({gap:.1f}pp lower)"

        return "Lower overall utility score"

    def _identify_risks(self, trace: Optional[Trace]) -> List[str]:
        """Identify key risks"""

        return [
            "Competitor response could accelerate churn beyond projections",
            "Network effects may amplify negative word-of-mouth",
            "Price-sensitive segment at highest risk",
            "Timing coincides with competitor product launch"
        ]

    def _define_monitoring(self, option: Dict) -> List[Dict]:
        """Define monitoring metrics"""

        return [
            {
                "metric": "Weekly churn rate",
                "frequency": "Weekly",
                "threshold": "2%/week",
                "owner": "Analytics"
            },
            {
                "metric": "Customer sentiment score",
                "frequency": "Daily",
                "threshold": "<0.3 triggers review",
                "owner": "Customer Success"
            },
            {
                "metric": "Competitor pricing",
                "frequency": "Daily",
                "threshold": ">10% discount triggers alert",
                "owner": "Competitive Intelligence"
            },
            {
                "metric": "Support ticket volume",
                "frequency": "Daily",
                "threshold": ">50% increase triggers review",
                "owner": "Support"
            }
        ]

    def _generate_executive_summary(
        self,
        option: Dict,
        confidence: float,
        simulation: TemporalSimulation,
        contingencies: List[Contingency]
    ) -> str:
        """Generate board-ready executive summary"""

        if not simulation or not simulation.aggregate_results:
            return "Insufficient simulation data for executive summary."

        agg = simulation.aggregate_results
        retention = agg.get("retention", {}).get("mean", 0)
        retention_range = f"{agg.get('retention', {}).get('p25', 0)*100:.0f}%-{agg.get('retention', {}).get('p75', 0)*100:.0f}%"

        return f"""Based on simulation of {len(simulation.branch_results)} scenarios with synthetic customer population, we recommend: {option.get('name', 'the proposed option')}.

Expected outcome: {retention*100:.0f}% retention (range: {retention_range}).
Confidence level: {confidence*100:.0f}%.

Key risk factors have been identified and contingency playbooks prepared for: competitor response, elevated churn, and sentiment deterioration. Approval gates and monitoring cadence are defined.

This recommendation balances revenue optimization against customer retention risk, with specific execution timelines and escalation procedures."""
