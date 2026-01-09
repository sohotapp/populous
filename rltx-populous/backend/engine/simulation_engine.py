"""
Temporal Multi-Agent Simulation Engine
Monte Carlo + Network Effects + Event Injection
"""

import numpy as np
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import List, Dict, Optional, Callable
import copy
from datetime import datetime

from backend.models.simulation import (
    TemporalSimulation, SimulationConfig, BranchResult,
    DailySnapshot, SimEvent, SimulationStatus
)
from backend.models.generative_agent import GenerativeAgent, AgentState, Memory
from backend.models.world import World


class SimulationEngine:
    """Engine for running temporal multi-agent simulations"""

    def __init__(self, agent_engine=None, network_engine=None):
        self.agent_engine = agent_engine
        self.network_engine = network_engine

    def run_simulation(
        self,
        config: SimulationConfig,
        agents: List[GenerativeAgent],
        world: World,
        option: Dict,
        progress_callback: Optional[Callable] = None
    ) -> TemporalSimulation:
        """Run complete Monte Carlo simulation"""

        simulation = TemporalSimulation(
            id=f"sim_{datetime.now().timestamp()}",
            config=config,
            status=SimulationStatus.RUNNING,
            started_at=datetime.now()
        )

        # Run branches (use ThreadPoolExecutor for simplicity)
        branch_results = []

        # For demo, run fewer branches
        actual_branches = min(config.num_branches, 100)

        for branch_id in range(actual_branches):
            result = self._run_branch(
                branch_id=branch_id,
                agents=copy.deepcopy(agents),
                world=world,
                option=option,
                config=config
            )
            branch_results.append(result)

            if progress_callback:
                progress_callback((branch_id + 1) / actual_branches)

        simulation.branch_results = branch_results
        simulation.aggregate_results = self._aggregate_results(branch_results)
        simulation.status = SimulationStatus.COMPLETED
        simulation.completed_at = datetime.now()
        simulation.progress = 1.0

        return simulation

    def _run_branch(
        self,
        branch_id: int,
        agents: List[GenerativeAgent],
        world: World,
        option: Dict,
        config: SimulationConfig
    ) -> BranchResult:
        """Run a single simulation branch"""

        # Set random seed for reproducibility
        np.random.seed(branch_id)

        daily_snapshots = []
        key_events = []

        # Apply the option/intervention at day 0
        self._apply_intervention(agents, option, world, day=0)
        key_events.append({
            "day": 0,
            "event": f"Intervention applied: {option.get('name', 'Unknown')}"
        })

        # Run simulation day by day
        for day in range(config.duration_days):
            # Check for scheduled events
            for event in config.events:
                if event.day == day:
                    self._inject_event(agents, event, world)
                    key_events.append({
                        "day": day,
                        "event": event.description
                    })

            # Process each agent
            for agent in agents:
                self._process_agent_day(agent, world, option, day)

            # Process network effects (social influence)
            if self.network_engine:
                self.network_engine.propagate_influence(agents, day)

            # Take snapshot
            snapshot = self._take_snapshot(agents, day)
            daily_snapshots.append(snapshot)

            # Check for competitive response
            if self._should_competitor_respond(world, agents, day):
                self._trigger_competitor_response(agents, world, day)
                key_events.append({
                    "day": day,
                    "event": "Competitor response triggered"
                })

        # Calculate final metrics
        final_metrics = self._calculate_final_metrics(agents, world)

        return BranchResult(
            branch_id=branch_id,
            seed=branch_id,
            final_metrics=final_metrics,
            daily_snapshots=daily_snapshots,
            key_events=key_events,
            outcome=self._classify_outcome(final_metrics, config)
        )

    def _process_agent_day(
        self,
        agent: GenerativeAgent,
        world: World,
        option: Dict,
        day: int
    ):
        """Process one day for one agent"""

        # Generate daily observations based on state
        observations = self._generate_daily_observations(agent, world, option, day)

        for obs in observations:
            if self.agent_engine:
                self.agent_engine.perceive(agent, obs, sim_time=day)
            else:
                # Simple memory addition without LLM
                mem = Memory(
                    id=f"mem_{len(agent.memory_stream)}",
                    timestamp=day,
                    description=obs,
                    importance=5.0,
                    type="observation"
                )
                agent.memory_stream.append(mem)

        # State transitions based on accumulated experience
        self._update_agent_state(agent, world, option, day)

    def _generate_daily_observations(
        self,
        agent: GenerativeAgent,
        world: World,
        option: Dict,
        day: int
    ) -> List[str]:
        """Generate observations an agent would have on a given day"""
        observations = []

        # Awareness phase observations
        if agent.state == AgentState.UNAWARE:
            if np.random.random() < 0.1:
                observations.append(
                    f"Heard about {world.your_product.name} changing their pricing"
                )

        # Active consideration observations
        elif agent.state in [AgentState.AWARE, AgentState.CONSIDERING]:
            if np.random.random() < 0.3:
                observations.append(
                    f"Looked up {world.your_product.name} reviews online"
                )
            if np.random.random() < 0.2 and world.competitors:
                competitor = np.random.choice(world.competitors)
                observations.append(
                    f"Compared pricing with {competitor.name}"
                )

        # Social observations (from network)
        if agent.relationships and np.random.random() < 0.15:
            observations.append(
                "Colleague mentioned their experience with the product"
            )

        return observations

    def _update_agent_state(
        self,
        agent: GenerativeAgent,
        world: World,
        option: Dict,
        day: int
    ):
        """Update agent state based on accumulated experience"""

        # Calculate current sentiment from recent memories
        recent_memories = agent.memory_stream[-20:]
        sentiment = self._calculate_sentiment(recent_memories)

        # Calculate product score
        product_score = self._calculate_product_score(agent, world, option)

        # State machine transitions
        if agent.state == AgentState.UNAWARE:
            if agent.awareness > 0.25:
                agent.state = AgentState.AWARE

        elif agent.state == AgentState.AWARE:
            if agent.awareness > 0.50:
                agent.state = AgentState.CONSIDERING

        elif agent.state == AgentState.CONSIDERING:
            if agent.awareness > 0.70:
                agent.state = AgentState.EVALUATING

        elif agent.state == AgentState.EVALUATING:
            decision_threshold = 0.55
            if product_score > decision_threshold:
                agent.state = AgentState.RETAINED
            elif product_score < (1 - decision_threshold):
                agent.state = AgentState.CHURNED

        # Update awareness
        awareness_gain = len([m for m in recent_memories if "product" in m.description.lower()]) * 0.05
        agent.awareness = min(agent.awareness + awareness_gain, 1.0)

    def _calculate_product_score(
        self,
        agent: GenerativeAgent,
        world: World,
        option: Dict
    ) -> float:
        """Calculate how favorably agent views the product"""

        # Feature fit (40%)
        feature_score = sum(
            world.your_product.features.values()
        ) / max(len(world.your_product.features), 1)

        # Price fit (30%)
        price_change = option.get("parameters", {}).get("price_increase", 0)
        price_score = 1 - (price_change * agent.price_sensitivity)

        # Brand fit (20%)
        brand_score = agent.brand_loyalty

        # Awareness bonus (10%)
        awareness_score = agent.awareness

        total_score = (
            0.40 * feature_score +
            0.30 * price_score +
            0.20 * brand_score +
            0.10 * awareness_score
        )

        return total_score

    def _calculate_sentiment(self, memories: List[Memory]) -> float:
        """Calculate sentiment from memories"""
        if not memories:
            return 0.5

        positive_words = ["good", "great", "excellent", "love", "happy", "satisfied"]
        negative_words = ["bad", "poor", "terrible", "hate", "angry", "frustrated"]

        positive_count = sum(
            1 for m in memories
            for word in positive_words
            if word in m.description.lower()
        )
        negative_count = sum(
            1 for m in memories
            for word in negative_words
            if word in m.description.lower()
        )

        total = positive_count + negative_count
        if total == 0:
            return 0.5

        return positive_count / total

    def _should_competitor_respond(
        self,
        world: World,
        agents: List[GenerativeAgent],
        day: int
    ) -> bool:
        """Check if competitors should respond"""
        churned_count = sum(1 for a in agents if a.state == AgentState.CHURNED)
        churn_rate = churned_count / len(agents) if agents else 0

        for competitor in world.competitors:
            if churn_rate > 0.05 and np.random.random() < competitor.aggression:
                return True

        return False

    def _trigger_competitor_response(
        self,
        agents: List[GenerativeAgent],
        world: World,
        day: int
    ):
        """Trigger a competitor response"""
        for agent in agents:
            if agent.state in [AgentState.CONSIDERING, AgentState.EVALUATING]:
                mem = Memory(
                    id=f"mem_{len(agent.memory_stream)}",
                    timestamp=day,
                    description="Saw competitor promotion: 'Switch & Save - 3 months free'",
                    importance=7.0,
                    type="observation"
                )
                agent.memory_stream.append(mem)

    def _inject_event(
        self,
        agents: List[GenerativeAgent],
        event: SimEvent,
        world: World
    ):
        """Inject an external event into the simulation"""
        for agent in agents:
            mem = Memory(
                id=f"mem_{len(agent.memory_stream)}",
                timestamp=event.day,
                description=event.description,
                importance=6.0,
                type="event"
            )
            agent.memory_stream.append(mem)

    def _apply_intervention(
        self,
        agents: List[GenerativeAgent],
        option: Dict,
        world: World,
        day: int
    ):
        """Apply the decision option as an intervention"""
        intervention_desc = option.get("description", "Change announced")
        for agent in agents:
            mem = Memory(
                id=f"mem_{len(agent.memory_stream)}",
                timestamp=day,
                description=intervention_desc,
                importance=8.0,
                type="intervention"
            )
            agent.memory_stream.append(mem)

    def _take_snapshot(self, agents: List[GenerativeAgent], day: int) -> DailySnapshot:
        """Take a snapshot of simulation state"""
        state_counts = {}
        for state in AgentState:
            state_counts[state.value] = sum(1 for a in agents if a.state == state)

        retained = state_counts.get(AgentState.RETAINED.value, 0)
        churned = state_counts.get(AgentState.CHURNED.value, 0)
        total = len(agents)

        return DailySnapshot(
            day=day,
            metrics={
                "retention_rate": retained / total if total > 0 else 0,
                "churn_rate": churned / total if total > 0 else 0,
                "awareness_avg": sum(a.awareness for a in agents) / total if total > 0 else 0
            },
            agent_states=state_counts,
            segment_metrics={},
            events_triggered=[]
        )

    def _calculate_final_metrics(
        self,
        agents: List[GenerativeAgent],
        world: World
    ) -> Dict[str, float]:
        """Calculate final simulation metrics"""
        total = len(agents)
        retained = sum(1 for a in agents if a.state == AgentState.RETAINED)
        churned = sum(1 for a in agents if a.state == AgentState.CHURNED)

        return {
            "retention_rate": retained / total if total > 0 else 0,
            "churn_rate": churned / total if total > 0 else 0,
            "net_promoter_estimate": (retained - churned) / total if total > 0 else 0
        }

    def _classify_outcome(
        self,
        metrics: Dict[str, float],
        config: SimulationConfig
    ) -> str:
        """Classify the outcome as success/failure/mixed"""
        retention = metrics.get("retention_rate", 0)

        if retention > 0.90:
            return "success"
        elif retention < 0.80:
            return "failure"
        else:
            return "mixed"

    def _aggregate_results(self, branch_results: List[BranchResult]) -> Dict:
        """Aggregate results across all Monte Carlo branches"""
        if not branch_results:
            return {}

        retention_rates = [b.final_metrics["retention_rate"] for b in branch_results]
        churn_rates = [b.final_metrics["churn_rate"] for b in branch_results]

        return {
            "retention": {
                "mean": float(np.mean(retention_rates)),
                "std": float(np.std(retention_rates)),
                "p5": float(np.percentile(retention_rates, 5)),
                "p25": float(np.percentile(retention_rates, 25)),
                "p50": float(np.percentile(retention_rates, 50)),
                "p75": float(np.percentile(retention_rates, 75)),
                "p95": float(np.percentile(retention_rates, 95))
            },
            "churn": {
                "mean": float(np.mean(churn_rates)),
                "std": float(np.std(churn_rates)),
                "p5": float(np.percentile(churn_rates, 5)),
                "p95": float(np.percentile(churn_rates, 95))
            },
            "outcome_distribution": {
                "success": sum(1 for b in branch_results if b.outcome == "success") / len(branch_results),
                "mixed": sum(1 for b in branch_results if b.outcome == "mixed") / len(branch_results),
                "failure": sum(1 for b in branch_results if b.outcome == "failure") / len(branch_results)
            },
            "confidence": 1 - float(np.std(retention_rates))
        }
