# SURGICAL BUILD PLAN - Part 2
## Engines (continued), API Layer, Frontend Components

---

# PART 2 (continued): BACKEND ENGINES

## 2.3 Trace Engine

### File: `backend/engine/trace_engine.py`
```python
"""
Causal Trace Engine
Builds explanatory chains from simulation results
"""

from typing import List, Dict
import numpy as np
from anthropic import Anthropic

from backend.models.trace import Trace, TraceNode, TraceEdge, Counterfactual, Sensitivity
from backend.models.simulation import Simulation, BranchResult
from backend.models.agent import Agent, AgentState

class TraceEngine:
    """Engine for generating causal traces"""

    def __init__(self, llm_client: Anthropic):
        self.llm = llm_client

    def generate_trace(
        self,
        simulation: Simulation,
        agents: List[Agent],
        option: Dict
    ) -> Trace:
        """Generate complete causal trace from simulation"""

        nodes = []
        edges = []

        # 1. Root node: The intervention
        root = TraceNode(
            id="root",
            type="event",
            description=f"Intervention: {option.get('name', 'Unknown')}",
            timestamp=0,
            metrics={"price_change": option.get("parameters", {}).get("price_increase", 0)}
        )
        nodes.append(root)

        # 2. Analyze outcomes by segment
        segment_outcomes = self._analyze_segment_outcomes(agents)
        for segment_id, outcome in segment_outcomes.items():
            segment_node = TraceNode(
                id=f"segment_{segment_id}",
                type="outcome",
                description=f"Segment {segment_id} response",
                metrics=outcome,
                agent_count=outcome.get("count", 0)
            )
            nodes.append(segment_node)

            # Edge from root to segment
            edges.append(TraceEdge(
                source_id="root",
                target_id=segment_node.id,
                weight=1.0,
                description="Intervention affects segment"
            ))

        # 3. Identify key drivers
        drivers = self._identify_drivers(simulation, agents)

        for i, driver in enumerate(drivers):
            driver_node = TraceNode(
                id=f"driver_{i}",
                type="factor",
                description=driver["description"],
                metrics={"importance": driver["importance"]}
            )
            nodes.append(driver_node)

        # 4. Analyze event impacts
        key_events = self._aggregate_key_events(simulation.branch_results)
        for i, event in enumerate(key_events):
            event_node = TraceNode(
                id=f"event_{i}",
                type="event",
                description=event["event"],
                timestamp=event["day"],
                metrics={"impact": event.get("impact", 0.5)}
            )
            nodes.append(event_node)

        # 5. Generate counterfactuals
        counterfactuals = self._generate_counterfactuals(simulation, option, agents)

        # 6. Calculate sensitivities
        sensitivities = self._calculate_sensitivities(simulation, agents, option)

        return Trace(
            id=f"trace_{simulation.id}",
            simulation_id=simulation.id,
            option_id=option.get("id", ""),
            nodes=nodes,
            edges=edges,
            root_causes=["root"],
            key_drivers=sensitivities,
            counterfactuals=counterfactuals
        )

    def _analyze_segment_outcomes(self, agents: List[Agent]) -> Dict:
        """Analyze outcomes by segment"""
        segments = {}

        for agent in agents:
            seg_id = agent.segment_id
            if seg_id not in segments:
                segments[seg_id] = {
                    "count": 0,
                    "retained": 0,
                    "churned": 0,
                    "avg_price_sensitivity": 0
                }

            segments[seg_id]["count"] += 1
            segments[seg_id]["avg_price_sensitivity"] += agent.price_sensitivity

            if agent.state == AgentState.RETAINED:
                segments[seg_id]["retained"] += 1
            elif agent.state == AgentState.CHURNED:
                segments[seg_id]["churned"] += 1

        # Calculate rates
        for seg_id, data in segments.items():
            count = data["count"]
            if count > 0:
                data["retention_rate"] = data["retained"] / count
                data["churn_rate"] = data["churned"] / count
                data["avg_price_sensitivity"] /= count

        return segments

    def _identify_drivers(
        self,
        simulation: Simulation,
        agents: List[Agent]
    ) -> List[Dict]:
        """Identify what drove the outcomes"""

        # Analyze churned vs retained agents
        churned = [a for a in agents if a.state == AgentState.CHURNED]
        retained = [a for a in agents if a.state == AgentState.RETAINED]

        drivers = []

        # Price sensitivity driver
        if churned and retained:
            churned_ps = np.mean([a.price_sensitivity for a in churned])
            retained_ps = np.mean([a.price_sensitivity for a in retained])

            if churned_ps > retained_ps:
                drivers.append({
                    "description": "Price sensitivity",
                    "importance": churned_ps - retained_ps,
                    "direction": "negative"
                })

        # Brand loyalty driver
        if churned and retained:
            churned_bl = np.mean([a.brand_loyalty for a in churned])
            retained_bl = np.mean([a.brand_loyalty for a in retained])

            if retained_bl > churned_bl:
                drivers.append({
                    "description": "Brand loyalty",
                    "importance": retained_bl - churned_bl,
                    "direction": "positive"
                })

        # Social influence driver
        churned_with_social = sum(
            1 for a in churned
            if any("colleague" in m.description.lower() or "friend" in m.description.lower()
                   for m in a.memory_stream)
        )
        if churned:
            social_factor = churned_with_social / len(churned)
            if social_factor > 0.2:
                drivers.append({
                    "description": "Social influence (word of mouth)",
                    "importance": social_factor,
                    "direction": "negative"
                })

        return sorted(drivers, key=lambda x: x["importance"], reverse=True)

    def _aggregate_key_events(self, branch_results: List[BranchResult]) -> List[Dict]:
        """Aggregate key events across branches"""
        event_counts = {}

        for branch in branch_results:
            for event in branch.key_events:
                key = f"{event['day']}_{event['event']}"
                if key not in event_counts:
                    event_counts[key] = {
                        "day": event["day"],
                        "event": event["event"],
                        "count": 0
                    }
                event_counts[key]["count"] += 1

        # Sort by frequency
        events = sorted(event_counts.values(), key=lambda x: x["count"], reverse=True)

        # Return top events
        return events[:10]

    def _generate_counterfactuals(
        self,
        simulation: Simulation,
        option: Dict,
        agents: List[Agent]
    ) -> List[Counterfactual]:
        """Generate what-if counterfactuals"""

        counterfactuals = []
        agg = simulation.aggregate_results

        if not agg:
            return counterfactuals

        base_retention = agg.get("retention", {}).get("mean", 0)
        price_increase = option.get("parameters", {}).get("price_increase", 0)

        # Counterfactual: Smaller price increase
        if price_increase > 0.05:
            estimated_improvement = (price_increase - 0.05) * 0.5  # Rough estimate
            counterfactuals.append(Counterfactual(
                id="cf_1",
                description="If price increase was 5% instead",
                changed_factor="price_increase",
                original_value=price_increase,
                counterfactual_value=0.05,
                outcome_change={
                    "retention_rate": estimated_improvement,
                    "churn_rate": -estimated_improvement
                }
            ))

        # Counterfactual: Grandfather existing customers
        counterfactuals.append(Counterfactual(
            id="cf_2",
            description="If existing customers were grandfathered",
            changed_factor="grandfather_policy",
            original_value=0,
            counterfactual_value=1,
            outcome_change={
                "retention_rate": 0.08,  # Estimated improvement
                "churn_rate": -0.08
            }
        ))

        # Counterfactual: No competitor response
        counterfactuals.append(Counterfactual(
            id="cf_3",
            description="If competitor hadn't launched promo",
            changed_factor="competitor_promo",
            original_value=1,
            counterfactual_value=0,
            outcome_change={
                "retention_rate": 0.05,
                "churn_rate": -0.05
            }
        ))

        return counterfactuals

    def _calculate_sensitivities(
        self,
        simulation: Simulation,
        agents: List[Agent],
        option: Dict
    ) -> List[Sensitivity]:
        """Calculate sensitivity of outcome to various factors"""

        sensitivities = []

        # Price sensitivity analysis
        churned = [a for a in agents if a.state == AgentState.CHURNED]
        if churned:
            avg_ps = np.mean([a.price_sensitivity for a in churned])
            sensitivities.append(Sensitivity(
                factor="price_sensitivity",
                importance=avg_ps,
                direction="negative",
                description=f"Higher price sensitivity correlates with {avg_ps*100:.0f}% of churn"
            ))

        # Brand loyalty analysis
        retained = [a for a in agents if a.state == AgentState.RETAINED]
        if retained:
            avg_bl = np.mean([a.brand_loyalty for a in retained])
            sensitivities.append(Sensitivity(
                factor="brand_loyalty",
                importance=avg_bl,
                direction="positive",
                description=f"Brand loyalty protected {avg_bl*100:.0f}% of retained customers"
            ))

        # Competitor response sensitivity
        sensitivities.append(Sensitivity(
            factor="competitor_response",
            importance=0.28,  # From analysis
            direction="negative",
            description="Competitor promotion accelerated 28% of churn decisions"
        ))

        return sorted(sensitivities, key=lambda x: x.importance, reverse=True)

    def generate_narrative(self, trace: Trace, simulation: Simulation) -> str:
        """Generate human-readable narrative of the trace"""

        prompt = f"""Based on this simulation trace, write a clear narrative explanation.

Trace summary:
- Nodes: {len(trace.nodes)}
- Key drivers: {[s.factor for s in trace.key_drivers]}
- Counterfactuals analyzed: {len(trace.counterfactuals)}

Key drivers with importance:
{chr(10).join([f"- {s.factor}: {s.importance:.2f} ({s.direction}) - {s.description}" for s in trace.key_drivers])}

Counterfactuals:
{chr(10).join([f"- {c.description}: Would change retention by {c.outcome_change.get('retention_rate', 0)*100:.1f}%" for c in trace.counterfactuals])}

Write a 3-paragraph narrative that:
1. Explains what happened and why
2. Identifies the key causal factors
3. Describes what could have changed the outcome

Use specific numbers and be concrete."""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text
```

## 2.4 Decision Engine (Recommendations)

### File: `backend/engine/decision_engine.py`
```python
"""
Decision Engine
Generates recommendations and execution plans
"""

from typing import List, Dict, Optional
from datetime import date, timedelta
from anthropic import Anthropic
import json

from backend.models.action import (
    Recommendation, ActionItem, Contingency, ApprovalGate
)
from backend.models.simulation import Simulation
from backend.models.trace import Trace

class DecisionEngine:
    """Engine for generating decision recommendations"""

    def __init__(self, llm_client: Anthropic):
        self.llm = llm_client

    def generate_recommendation(
        self,
        decision_id: str,
        simulations: Dict[str, Simulation],  # option_id -> simulation
        traces: Dict[str, Trace],  # option_id -> trace
        options: List[Dict],
        constraints: List[Dict]
    ) -> Recommendation:
        """Generate complete recommendation from simulation results"""

        # 1. Rank options by expected utility
        rankings = self._rank_options(simulations, constraints)
        best_option_id = rankings[0]["option_id"]
        best_option = next((o for o in options if o["id"] == best_option_id), options[0])
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
        simulations: Dict[str, Simulation],
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
                if constraint["metric"] == "retention_rate":
                    if constraint["operator"] == ">=" and retention < constraint["value"]:
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
        simulation: Simulation,
        rankings: List[Dict]
    ) -> float:
        """Calculate confidence in recommendation"""

        if not simulation or not simulation.aggregate_results:
            return 0.5

        agg = simulation.aggregate_results

        # Factors:
        # 1. Low variance = high confidence
        std = agg.get("retention", {}).get("std", 0.5)
        variance_factor = max(0, 1 - std * 2)

        # 2. Clear winner = high confidence
        if len(rankings) >= 2:
            gap = rankings[0]["utility"] - rankings[1]["utility"]
            gap_factor = min(gap * 5, 1)  # Larger gap = more confident
        else:
            gap_factor = 0.5

        # 3. Sample size (branches)
        branch_count = len(simulation.branch_results)
        sample_factor = min(branch_count / 1000, 1)

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
        simulation: Simulation,
        trace: Optional[Trace],
        rankings: List[Dict]
    ) -> List[Contingency]:
        """Identify contingency plans"""

        contingencies = []

        # Contingency 1: Competitor response
        contingencies.append(Contingency(
            id="contingency_1",
            trigger="Competitor launches aggressive promotion (>20% discount)",
            detection="Monitor competitor pricing and promotions daily",
            response="Pause rollout to price-sensitive segments, activate retention offers",
            escalation="VP Marketing within 24 hours",
            timeframe="Within 48 hours of detection"
        ))

        # Contingency 2: High churn
        contingencies.append(Contingency(
            id="contingency_2",
            trigger="Week-over-week churn exceeds 3% in any segment",
            detection="Automated alert from churn dashboard",
            response="Trigger win-back campaign, analyze exit survey patterns",
            escalation="CEO for potential rollback decision",
            timeframe="Within 24 hours"
        ))

        # Contingency 3: Sentiment collapse
        contingencies.append(Contingency(
            id="contingency_3",
            trigger="Social media sentiment drops >30%",
            detection="Sentiment monitoring tool alert",
            response="Accelerate value communication, prepare PR response",
            escalation="Communications team within 12 hours",
            timeframe="Same day"
        ))

        # Contingency 4: Enterprise risk
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

        # Standard approval gates
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
        simulations: Dict[str, Simulation],
        traces: Dict[str, Trace]
    ) -> str:
        """Generate reasoning for recommendation"""

        if not rankings:
            return "Insufficient data for recommendation."

        best = rankings[0]
        best_sim = simulations.get(best["option_id"])

        reasoning_parts = []

        # Why this option
        reasoning_parts.append(
            f"This option achieves {best['retention']*100:.0f}% retention with {best['confidence']*100:.0f}% confidence."
        )

        # Comparison to alternatives
        if len(rankings) > 1:
            second = rankings[1]
            gap = (best["retention"] - second["retention"]) * 100
            reasoning_parts.append(
                f"It outperforms the next best option by {gap:.1f} percentage points in retention."
            )

        # Constraint satisfaction
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
        simulations: Dict[str, Simulation]
    ) -> List[Dict]:
        """Generate comparison to alternatives"""

        comparison = []

        for rank in rankings[1:4]:  # Top 3 alternatives
            sim = simulations.get(rank["option_id"])
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

        risks = [
            "Competitor response could accelerate churn beyond projections",
            "Network effects may amplify negative word-of-mouth",
            "Price-sensitive segment at highest risk",
            "Timing coincides with competitor product launch"
        ]

        return risks[:4]

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
        simulation: Simulation,
        contingencies: List[Contingency]
    ) -> str:
        """Generate board-ready executive summary"""

        agg = simulation.aggregate_results if simulation else {}
        retention = agg.get("retention", {}).get("mean", 0)
        retention_range = f"{agg.get('retention', {}).get('p25', 0)*100:.0f}%-{agg.get('retention', {}).get('p75', 0)*100:.0f}%"

        summary = f"""Based on simulation of {len(simulation.branch_results) if simulation else 0} scenarios with synthetic customer population, we recommend: {option.get('name', 'the proposed option')}.

Expected outcome: {retention*100:.0f}% retention (range: {retention_range}).
Confidence level: {confidence*100:.0f}%.

Key risk factors have been identified and contingency playbooks prepared for: competitor response, elevated churn, and sentiment deterioration. Approval gates and monitoring cadence are defined.

This recommendation balances revenue optimization against customer retention risk, with specific execution timelines and escalation procedures."""

        return summary
```

## 2.5 Chat Engine (Agent Interviews)

### File: `backend/engine/chat_engine.py`
```python
"""
Chat Engine
Enables natural conversation with synthetic agents
"""

from typing import List, Dict, Optional
from anthropic import Anthropic
import json

from backend.models.agent import Agent, Memory

class ChatEngine:
    """Engine for conversing with synthetic agents"""

    def __init__(self, llm_client: Anthropic):
        self.llm = llm_client

    def chat(
        self,
        agent: Agent,
        user_message: str,
        conversation_history: List[Dict] = []
    ) -> str:
        """Generate agent response to user message"""

        # Retrieve relevant memories
        relevant_memories = self._get_relevant_memories(agent, user_message)

        # Build agent context
        agent_context = self._build_agent_context(agent)

        # Build conversation
        system_prompt = f"""You are {agent.name}, a {agent.age}-year-old {agent.occupation}.

{agent_context}

IMPORTANT GUIDELINES:
- Stay completely in character as {agent.name}
- Reference your specific experiences and memories when relevant
- Be authentic to your personality and values
- Give specific, personal answers - not generic ones
- If asked about decisions you made, explain your actual reasoning
- Show your personality: {self._describe_personality(agent.personality)}

Your relevant experiences and memories:
{chr(10).join([f"- {m.description}" for m in relevant_memories[-15:]])}

Remember: You ARE this person. Speak as yourself, not about yourself."""

        messages = []

        # Add conversation history
        for msg in conversation_history[-10:]:  # Last 10 messages
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current message
        messages.append({
            "role": "user",
            "content": user_message
        })

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=system_prompt,
            messages=messages
        )

        return response.content[0].text

    def _build_agent_context(self, agent: Agent) -> str:
        """Build context description for agent"""

        context_parts = []

        # Basic info
        context_parts.append(f"You live in {agent.location} and work as a {agent.occupation}.")
        context_parts.append(f"Your annual income is ${agent.income:,.0f}.")

        # Values and priorities
        if agent.values:
            context_parts.append(f"You deeply value: {', '.join(agent.values)}.")

        # Pain points
        if agent.pain_points:
            context_parts.append(f"Your main frustrations are: {', '.join(agent.pain_points)}.")

        # Decision style
        context_parts.append(f"When making decisions, you tend to be {agent.decision_style}.")

        # Behavioral traits
        if agent.price_sensitivity > 0.7:
            context_parts.append("You're very careful about money and compare prices diligently.")
        elif agent.price_sensitivity < 0.3:
            context_parts.append("Price isn't your main concern - you prioritize quality and convenience.")

        if agent.brand_loyalty > 0.7:
            context_parts.append("You tend to stick with brands you trust, even if alternatives exist.")
        elif agent.brand_loyalty < 0.3:
            context_parts.append("You're always open to trying new options if they're better.")

        if agent.risk_tolerance > 0.7:
            context_parts.append("You're comfortable taking risks and trying new things.")
        elif agent.risk_tolerance < 0.3:
            context_parts.append("You prefer safe, proven choices and avoid unnecessary risk.")

        # Recent state
        state_descriptions = {
            "churned": "You recently decided to leave/cancel your subscription.",
            "retained": "You decided to stay despite the changes.",
            "evaluating": "You're currently weighing your options.",
            "considering": "You're starting to think about alternatives."
        }
        if agent.state.value in state_descriptions:
            context_parts.append(state_descriptions[agent.state.value])

        return " ".join(context_parts)

    def _describe_personality(self, personality: Dict) -> str:
        """Describe personality traits in natural language"""

        descriptions = []

        if personality.get("openness", 0.5) > 0.7:
            descriptions.append("curious and open to new experiences")
        elif personality.get("openness", 0.5) < 0.3:
            descriptions.append("practical and prefer familiar things")

        if personality.get("conscientiousness", 0.5) > 0.7:
            descriptions.append("organized and thorough")
        elif personality.get("conscientiousness", 0.5) < 0.3:
            descriptions.append("flexible and spontaneous")

        if personality.get("extraversion", 0.5) > 0.7:
            descriptions.append("outgoing and energetic")
        elif personality.get("extraversion", 0.5) < 0.3:
            descriptions.append("reserved and thoughtful")

        if personality.get("agreeableness", 0.5) > 0.7:
            descriptions.append("cooperative and trusting")
        elif personality.get("agreeableness", 0.5) < 0.3:
            descriptions.append("straightforward and skeptical")

        return ", ".join(descriptions) if descriptions else "balanced"

    def _get_relevant_memories(
        self,
        agent: Agent,
        query: str,
        k: int = 15
    ) -> List[Memory]:
        """Get memories relevant to the query"""

        if not agent.memory_stream:
            return []

        # Simple relevance scoring (in production: use embeddings)
        query_words = set(query.lower().split())

        scored = []
        for mem in agent.memory_stream:
            mem_words = set(mem.description.lower().split())
            overlap = len(query_words & mem_words)
            score = overlap + (mem.importance / 10)
            scored.append((score, mem))

        scored.sort(reverse=True, key=lambda x: x[0])

        return [mem for _, mem in scored[:k]]

    def get_decision_journey(self, agent: Agent) -> List[Dict]:
        """Get the agent's decision journey for display"""

        journey = []

        for event in agent.decision_events:
            journey.append({
                "timestamp": event.timestamp,
                "type": event.decision_type,
                "choice": event.choice,
                "reasoning": event.reasoning,
                "confidence": event.confidence
            })

        # Add key memories
        key_memories = [m for m in agent.memory_stream if m.importance >= 7]
        for mem in key_memories[-10:]:
            journey.append({
                "timestamp": mem.timestamp,
                "type": "memory",
                "description": mem.description,
                "importance": mem.importance
            })

        # Sort by timestamp
        journey.sort(key=lambda x: x["timestamp"])

        return journey
```

## 2.6 Prediction Engine (Real-time Survey Predictions)

### File: `backend/engine/prediction_engine.py`
```python
"""
Prediction Engine
Real-time survey response predictions
"""

from typing import List, Dict, Optional
from anthropic import Anthropic
import json

from backend.models.agent import Agent

class PredictionEngine:
    """Engine for predicting survey responses"""

    def __init__(self, llm_client: Anthropic):
        self.llm = llm_client
        self._cache = {}  # Simple cache

    def predict_responses(
        self,
        agents: List[Agent],
        questions: List[Dict]
    ) -> Dict:
        """Predict how agents would respond to survey questions"""

        predictions = []

        for i, question in enumerate(questions):
            # Check cache
            cache_key = self._make_cache_key(question, len(agents))
            if cache_key in self._cache:
                predictions.append(self._cache[cache_key])
                continue

            # Generate prediction
            prediction = self._predict_single_question(agents, question)
            predictions.append(prediction)

            # Cache it
            self._cache[cache_key] = prediction

        # Calculate overall confidence
        confidences = [p.get("confidence", 0.5) for p in predictions]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        return {
            "overall_confidence": self._classify_confidence(overall_confidence),
            "predictions": predictions
        }

    def _predict_single_question(
        self,
        agents: List[Agent],
        question: Dict
    ) -> Dict:
        """Predict responses for a single question"""

        question_type = question.get("type", "single_choice")
        question_text = question.get("text", "")
        options = question.get("options", [])

        if question_type == "single_choice":
            return self._predict_single_choice(agents, question_text, options)
        elif question_type == "rating_scale":
            return self._predict_rating_scale(agents, question_text, question.get("scale", 5))
        elif question_type == "open_text":
            return self._predict_open_text(agents, question_text)
        else:
            return {"error": "Unknown question type"}

    def _predict_single_choice(
        self,
        agents: List[Agent],
        question: str,
        options: List[str]
    ) -> Dict:
        """Predict single choice responses"""

        # Sample agents for prediction (for speed)
        sample_size = min(50, len(agents))
        sample_agents = agents[:sample_size]

        # Build agent summary
        segment_summary = self._summarize_segments(sample_agents)

        prompt = f"""Given this audience:
{segment_summary}

Predict how they would answer this survey question:
"{question}"

Options:
{chr(10).join([f"- {opt}" for opt in options])}

Provide predicted distribution as percentages that sum to 100.
Format as JSON: {{"option1": percent, "option2": percent, ...}}

Base your prediction on:
1. The audience's demographics and psychographics
2. Typical response patterns for similar audiences
3. The specific wording and framing of options"""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            # Parse response
            text = response.content[0].text
            # Find JSON in response
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                distribution = json.loads(text[start:end])
            else:
                # Default distribution
                distribution = {opt: 100/len(options) for opt in options}
        except:
            distribution = {opt: 100/len(options) for opt in options}

        # Normalize to ensure sum is 100
        total = sum(distribution.values())
        if total > 0:
            distribution = {k: v/total for k, v in distribution.items()}

        return {
            "question": question,
            "type": "single_choice",
            "distribution": distribution,
            "confidence": self._estimate_confidence(sample_agents, question)
        }

    def _predict_rating_scale(
        self,
        agents: List[Agent],
        question: str,
        scale: int
    ) -> Dict:
        """Predict rating scale responses"""

        segment_summary = self._summarize_segments(agents[:50])

        prompt = f"""Given this audience:
{segment_summary}

Predict how they would answer this rating question:
"{question}"

Scale: 1 to {scale} (1 = lowest/worst, {scale} = highest/best)

Provide:
1. Mean rating (to 1 decimal)
2. Distribution shape (normal, skewed_positive, skewed_negative, bimodal)
3. Standard deviation estimate

Format as JSON: {{"mean": X.X, "distribution": "shape", "std": X.X}}"""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            text = response.content[0].text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                result = json.loads(text[start:end])
            else:
                result = {"mean": scale/2, "distribution": "normal", "std": 1.0}
        except:
            result = {"mean": scale/2, "distribution": "normal", "std": 1.0}

        return {
            "question": question,
            "type": "rating_scale",
            "mean": result.get("mean", scale/2),
            "distribution_shape": result.get("distribution", "normal"),
            "std": result.get("std", 1.0),
            "scale": scale,
            "confidence": self._estimate_confidence(agents[:50], question)
        }

    def _predict_open_text(
        self,
        agents: List[Agent],
        question: str
    ) -> Dict:
        """Predict themes in open text responses"""

        segment_summary = self._summarize_segments(agents[:50])

        prompt = f"""Given this audience:
{segment_summary}

If asked: "{question}"

What would be the 3-5 most common themes in their open-text responses?
For each theme, estimate what percentage would mention it.

Format as JSON: {{"themes": [{{"theme": "...", "percent": X}}, ...]}}"""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            text = response.content[0].text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                result = json.loads(text[start:end])
            else:
                result = {"themes": []}
        except:
            result = {"themes": []}

        return {
            "question": question,
            "type": "open_text",
            "themes": result.get("themes", []),
            "confidence": "low"  # Open text is harder to predict
        }

    def _summarize_segments(self, agents: List[Agent]) -> str:
        """Summarize agent segments for LLM context"""

        segments = {}
        for agent in agents:
            seg = agent.segment_id
            if seg not in segments:
                segments[seg] = {
                    "count": 0,
                    "avg_price_sensitivity": 0,
                    "avg_brand_loyalty": 0,
                    "occupations": []
                }
            segments[seg]["count"] += 1
            segments[seg]["avg_price_sensitivity"] += agent.price_sensitivity
            segments[seg]["avg_brand_loyalty"] += agent.brand_loyalty
            if agent.occupation not in segments[seg]["occupations"]:
                segments[seg]["occupations"].append(agent.occupation)

        summary_parts = []
        for seg, data in segments.items():
            count = data["count"]
            if count > 0:
                data["avg_price_sensitivity"] /= count
                data["avg_brand_loyalty"] /= count
            summary_parts.append(
                f"- {seg} ({count} people): "
                f"Price sensitivity {data['avg_price_sensitivity']:.1f}, "
                f"Brand loyalty {data['avg_brand_loyalty']:.1f}, "
                f"Occupations include: {', '.join(data['occupations'][:3])}"
            )

        return chr(10).join(summary_parts)

    def _estimate_confidence(self, agents: List[Agent], question: str) -> str:
        """Estimate prediction confidence"""

        # Simple heuristic based on sample size and homogeneity
        if len(agents) < 20:
            return "low"
        elif len(agents) < 100:
            return "medium"
        else:
            return "high"

    def _classify_confidence(self, score: float) -> str:
        """Classify confidence score"""
        if score > 0.7:
            return "high"
        elif score > 0.4:
            return "medium"
        else:
            return "low"

    def _make_cache_key(self, question: Dict, agent_count: int) -> str:
        """Create cache key for prediction"""
        return f"{question.get('text', '')}_{question.get('type', '')}_{agent_count}"
```

## 2.7 Bias Detection Engine

### File: `backend/engine/bias_engine.py`
```python
"""
Bias Detection Engine
Detects and suggests fixes for biased survey questions
"""

from typing import List, Dict, Optional
from anthropic import Anthropic
import re

class BiasEngine:
    """Engine for detecting bias in survey questions"""

    def __init__(self, llm_client: Anthropic):
        self.llm = llm_client

        # Common bias patterns
        self.leading_phrases = [
            "don't you agree",
            "wouldn't you say",
            "isn't it true",
            "surely you",
            "obviously",
            "clearly",
            "everyone knows"
        ]

        self.loaded_words = [
            "best", "worst", "amazing", "terrible",
            "love", "hate", "perfect", "awful",
            "must", "should", "always", "never"
        ]

    def check_bias(self, question: str, options: List[str] = []) -> Dict:
        """Check a question for potential bias"""

        issues = []

        # Rule-based checks
        question_lower = question.lower()

        # Check for leading phrases
        for phrase in self.leading_phrases:
            if phrase in question_lower:
                issues.append({
                    "type": "leading",
                    "description": f"Leading phrase detected: '{phrase}'",
                    "severity": "high"
                })

        # Check for loaded words
        for word in self.loaded_words:
            if re.search(r'\b' + word + r'\b', question_lower):
                issues.append({
                    "type": "loaded_language",
                    "description": f"Loaded word detected: '{word}'",
                    "severity": "medium"
                })

        # Check for double-barreled questions
        if " and " in question_lower and "?" in question:
            issues.append({
                "type": "double_barreled",
                "description": "Question may be asking two things at once",
                "severity": "medium"
            })

        # Check for missing neutral option (if options provided)
        if options:
            has_neutral = any(
                opt.lower() in ["neutral", "neither", "no opinion", "not sure", "n/a"]
                for opt in options
            )
            if not has_neutral and len(options) > 2:
                issues.append({
                    "type": "missing_neutral",
                    "description": "Consider adding a neutral option",
                    "severity": "low"
                })

        # If rule-based found nothing, do LLM check
        if not issues:
            llm_check = self._llm_bias_check(question, options)
            if llm_check.get("has_bias"):
                issues.append({
                    "type": llm_check.get("bias_type", "subtle"),
                    "description": llm_check.get("explanation", "Potential subtle bias"),
                    "severity": "medium"
                })

        # Generate suggestion if issues found
        suggestion = None
        if issues:
            suggestion = self._generate_suggestion(question, issues)

        return {
            "has_bias": len(issues) > 0,
            "issues": issues,
            "suggestion": suggestion
        }

    def _llm_bias_check(self, question: str, options: List[str]) -> Dict:
        """Use LLM to check for subtle bias"""

        prompt = f"""Analyze this survey question for potential bias:

Question: "{question}"
{f"Options: {options}" if options else ""}

Check for:
1. Leading language that suggests a "correct" answer
2. Loaded or emotionally charged words
3. Assumptions embedded in the question
4. Social desirability bias triggers
5. Framing effects

If there is bias, explain it briefly.
If there is no bias, say "No bias detected."

Format: BIAS: [yes/no] | TYPE: [type] | EXPLANATION: [brief explanation]"""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text.lower()

        if "bias: yes" in text or "bias detected" in text:
            # Extract type and explanation
            bias_type = "subtle"
            explanation = text

            if "type:" in text:
                type_start = text.find("type:") + 5
                type_end = text.find("|", type_start) if "|" in text[type_start:] else len(text)
                bias_type = text[type_start:type_end].strip()

            if "explanation:" in text:
                exp_start = text.find("explanation:") + 12
                explanation = text[exp_start:].strip()

            return {
                "has_bias": True,
                "bias_type": bias_type,
                "explanation": explanation
            }

        return {"has_bias": False}

    def _generate_suggestion(self, question: str, issues: List[Dict]) -> str:
        """Generate improved question suggestion"""

        issue_descriptions = [i["description"] for i in issues]

        prompt = f"""Rewrite this survey question to remove bias.

Original question: "{question}"

Issues found:
{chr(10).join(['- ' + d for d in issue_descriptions])}

Provide a neutral, unbiased version that:
1. Removes leading language
2. Uses neutral wording
3. Doesn't suggest a preferred answer
4. Is clear and easy to understand

Return only the improved question, nothing else."""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text.strip().strip('"')

    def suggest_questions(
        self,
        survey_purpose: str,
        existing_questions: List[str],
        audience_description: str
    ) -> List[Dict]:
        """Suggest additional questions for the survey"""

        prompt = f"""You are helping design a survey.

Purpose: {survey_purpose}
Target audience: {audience_description}

Existing questions:
{chr(10).join(['- ' + q for q in existing_questions]) if existing_questions else '(none yet)'}

Suggest 2-3 additional questions that would provide valuable insights.
For each suggestion, explain why it would be useful.

Format each as:
QUESTION: [the question]
TYPE: [single_choice/rating_scale/open_text]
RATIONALE: [why this helps]
OPTIONS: [if applicable, suggested options]"""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse suggestions
        suggestions = []
        text = response.content[0].text

        # Split by QUESTION:
        parts = text.split("QUESTION:")

        for part in parts[1:]:  # Skip first empty part
            lines = part.strip().split("\n")
            question = lines[0].strip() if lines else ""

            question_type = "single_choice"
            rationale = ""
            options = []

            for line in lines[1:]:
                if line.startswith("TYPE:"):
                    question_type = line.replace("TYPE:", "").strip().lower()
                elif line.startswith("RATIONALE:"):
                    rationale = line.replace("RATIONALE:", "").strip()
                elif line.startswith("OPTIONS:"):
                    opts = line.replace("OPTIONS:", "").strip()
                    options = [o.strip() for o in opts.split(",")]

            if question:
                suggestions.append({
                    "question": question,
                    "type": question_type,
                    "rationale": rationale,
                    "options": options
                })

        return suggestions
```

---

This continues in Part 3 with the API Layer and Frontend Components.
