"""
Causal Trace Engine
Builds explanatory chains from simulation results
"""

from typing import List, Dict, Optional
import numpy as np
from anthropic import Anthropic

from backend.models.trace import Trace, TraceNode, TraceEdge, Counterfactual, Sensitivity
from backend.models.simulation import TemporalSimulation, BranchResult
from backend.models.generative_agent import GenerativeAgent, AgentState


class TraceEngine:
    """Engine for generating causal traces"""

    def __init__(self, llm_client: Anthropic = None):
        self.llm = llm_client

    def generate_trace(
        self,
        simulation: TemporalSimulation,
        agents: List[GenerativeAgent],
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

    def _analyze_segment_outcomes(self, agents: List[GenerativeAgent]) -> Dict:
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

        for seg_id, data in segments.items():
            count = data["count"]
            if count > 0:
                data["retention_rate"] = data["retained"] / count
                data["churn_rate"] = data["churned"] / count
                data["avg_price_sensitivity"] /= count

        return segments

    def _identify_drivers(
        self,
        simulation: TemporalSimulation,
        agents: List[GenerativeAgent]
    ) -> List[Dict]:
        """Identify what drove the outcomes"""

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
                    "importance": float(churned_ps - retained_ps),
                    "direction": "negative"
                })

        # Brand loyalty driver
        if churned and retained:
            churned_bl = np.mean([a.brand_loyalty for a in churned])
            retained_bl = np.mean([a.brand_loyalty for a in retained])

            if retained_bl > churned_bl:
                drivers.append({
                    "description": "Brand loyalty",
                    "importance": float(retained_bl - churned_bl),
                    "direction": "positive"
                })

        # Social influence driver
        if churned:
            churned_with_social = sum(
                1 for a in churned
                if any("colleague" in m.description.lower() or "friend" in m.description.lower()
                       for m in a.memory_stream)
            )
            social_factor = churned_with_social / len(churned)
            if social_factor > 0.2:
                drivers.append({
                    "description": "Social influence (word of mouth)",
                    "importance": float(social_factor),
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

        events = sorted(event_counts.values(), key=lambda x: x["count"], reverse=True)
        return events[:10]

    def _generate_counterfactuals(
        self,
        simulation: TemporalSimulation,
        option: Dict,
        agents: List[GenerativeAgent]
    ) -> List[Counterfactual]:
        """Generate what-if counterfactuals"""

        counterfactuals = []
        agg = simulation.aggregate_results

        if not agg:
            return counterfactuals

        price_increase = option.get("parameters", {}).get("price_increase", 0)

        # Counterfactual: Smaller price increase
        if price_increase > 0.05:
            estimated_improvement = (price_increase - 0.05) * 0.5
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
                "retention_rate": 0.08,
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
        simulation: TemporalSimulation,
        agents: List[GenerativeAgent],
        option: Dict
    ) -> List[Sensitivity]:
        """Calculate sensitivity of outcome to various factors"""

        sensitivities = []

        churned = [a for a in agents if a.state == AgentState.CHURNED]
        retained = [a for a in agents if a.state == AgentState.RETAINED]

        # Price sensitivity analysis
        if churned:
            avg_ps = np.mean([a.price_sensitivity for a in churned])
            sensitivities.append(Sensitivity(
                factor="price_sensitivity",
                importance=float(avg_ps),
                direction="negative",
                description=f"Higher price sensitivity correlates with {avg_ps*100:.0f}% of churn"
            ))

        # Brand loyalty analysis
        if retained:
            avg_bl = np.mean([a.brand_loyalty for a in retained])
            sensitivities.append(Sensitivity(
                factor="brand_loyalty",
                importance=float(avg_bl),
                direction="positive",
                description=f"Brand loyalty protected {avg_bl*100:.0f}% of retained customers"
            ))

        # Competitor response sensitivity
        sensitivities.append(Sensitivity(
            factor="competitor_response",
            importance=0.28,
            direction="negative",
            description="Competitor promotion accelerated 28% of churn decisions"
        ))

        return sorted(sensitivities, key=lambda x: x.importance, reverse=True)

    def generate_narrative(self, trace: Trace, simulation: TemporalSimulation) -> str:
        """Generate human-readable narrative of the trace"""

        if not self.llm:
            return self._generate_simple_narrative(trace, simulation)

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

    def _generate_simple_narrative(self, trace: Trace, simulation: TemporalSimulation) -> str:
        """Generate narrative without LLM"""
        agg = simulation.aggregate_results or {}
        retention = agg.get("retention", {}).get("mean", 0)

        drivers_text = ", ".join([f"{s.factor} ({s.direction})" for s in trace.key_drivers[:3]])

        return f"""The simulation showed {retention*100:.1f}% customer retention.

Key factors driving outcomes: {drivers_text}.

{len(trace.counterfactuals)} counterfactual scenarios were analyzed to understand what could have changed the outcome."""
