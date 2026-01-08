"""
Simulation Runner - Monte Carlo execution across branches.
"""

import random
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import copy

from backend.models import (
    Scenario, Strategy, Agent,
    SimulationResults, BranchResult, DailySnapshot,
    SegmentAnalysis, DriverAnalysis
)
from backend.engine.agent_factory import AgentFactory
from backend.engine.decision_engine import DecisionEngine
from backend.engine.market_dynamics import MarketDynamics


class SimulationRunner:
    """
    Runs parallel Monte Carlo simulation branches.
    """

    def __init__(
        self,
        scenario: Scenario,
        strategy: Strategy,
        num_agents: int = 10000,
        num_branches: int = 500,
        use_llm_personas: bool = False,
        parallel: bool = True
    ):
        self.scenario = scenario
        self.strategy = strategy
        self.num_agents = num_agents
        self.num_branches = num_branches
        self.use_llm_personas = use_llm_personas
        self.parallel = parallel

    def run(self) -> SimulationResults:
        """Execute full simulation and return aggregated results"""

        started_at = datetime.now()

        # Run branches
        if self.parallel and self.num_branches > 10:
            branch_results = self._run_parallel()
        else:
            branch_results = self._run_sequential()

        # Aggregate results
        results = self._aggregate_results(branch_results, started_at)

        return results

    def _run_parallel(self) -> List[BranchResult]:
        """Run branches in parallel using ProcessPoolExecutor"""

        results = []

        # Note: For multiprocessing, we pass serializable data
        # and reconstruct objects in worker
        scenario_dict = self.scenario.model_dump()
        strategy_dict = self.strategy.model_dump()

        with ProcessPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(
                    _run_branch_worker,
                    seed,
                    scenario_dict,
                    strategy_dict,
                    self.num_agents,
                    self.use_llm_personas
                ): seed
                for seed in range(self.num_branches)
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Branch failed: {e}")

        return results

    def _run_sequential(self) -> List[BranchResult]:
        """Run branches sequentially (for debugging)"""

        results = []
        for seed in range(self.num_branches):
            result = self._run_single_branch(seed)
            results.append(result)
        return results

    def _run_single_branch(self, seed: int) -> BranchResult:
        """Run a single simulation branch"""

        # Set random seeds for reproducibility
        random.seed(seed)
        np.random.seed(seed)

        # Create agents
        factory = AgentFactory(
            use_llm=self.use_llm_personas and seed == 0,  # LLM only for first branch
            llm_sample_size=20 if self.use_llm_personas else 0
        )
        agents = factory.create_population(
            self.scenario.segments,
            self.num_agents
        )

        # Create index for fast lookup
        agent_index = {a.id: i for i, a in enumerate(agents)}

        # Initialize dynamics
        market = MarketDynamics(self.scenario, self.strategy)
        engine = DecisionEngine()

        # Run simulation
        timeline = []

        for day in range(self.scenario.simulation_days):
            # Get market signals
            signals = market.get_signals(day, agents)

            # Process each agent
            for i, agent in enumerate(agents):
                if agent.stage != "Decided":
                    agents[i] = engine.process_agent_day(
                        agent,
                        day,
                        self.scenario.your_product,
                        self.scenario.competitors,
                        signals,
                        self.strategy
                    )

            # Record snapshot
            timeline.append(self._create_snapshot(agents, day, market))

        # Calculate final metrics
        return self._create_branch_result(
            seed, agents, timeline, market
        )

    def _create_snapshot(
        self,
        agents: List[Agent],
        day: int,
        market: MarketDynamics
    ) -> DailySnapshot:
        """Create daily snapshot of simulation state"""

        your_product_id = self.scenario.your_product.id
        competitor_ids = [c.id for c in self.scenario.competitors]

        # Count by stage
        stages = {"Unaware": 0, "Aware": 0, "Considering": 0, "Evaluating": 0, "Decided": 0}
        converted = 0
        competitor_converted = 0
        no_purchase = 0
        total_awareness = 0

        for agent in agents:
            stages[agent.stage] += 1
            total_awareness += agent.awareness.get(your_product_id, 0)

            if agent.stage == "Decided":
                if agent.final_decision == your_product_id:
                    converted += 1
                elif agent.final_decision in competitor_ids:
                    competitor_converted += 1
                else:
                    no_purchase += 1

        return DailySnapshot(
            day=day,
            unaware_count=stages["Unaware"],
            aware_count=stages["Aware"],
            considering_count=stages["Considering"],
            evaluating_count=stages["Evaluating"],
            decided_count=stages["Decided"],
            converted_count=converted,
            competitor_count=competitor_converted,
            no_purchase_count=no_purchase,
            avg_awareness=total_awareness / len(agents) if agents else 0,
            events=list(market.events_triggered)
        )

    def _create_branch_result(
        self,
        seed: int,
        agents: List[Agent],
        timeline: List[DailySnapshot],
        market: MarketDynamics
    ) -> BranchResult:
        """Create result object for a branch"""

        your_product_id = self.scenario.your_product.id

        # Count conversions
        converted = [a for a in agents if a.final_decision == your_product_id]
        decided = [a for a in agents if a.stage == "Decided"]

        conversion_rate = len(converted) / len(agents) if agents else 0

        # Awareness
        avg_awareness = np.mean([
            a.awareness.get(your_product_id, 0) for a in agents
        ])

        # Average decision day for those who decided
        decision_days = [a.decision_day for a in decided if a.decision_day]
        avg_decision_day = np.mean(decision_days) if decision_days else 0

        # By segment
        segment_conversions = {}
        for segment in self.scenario.segments:
            segment_agents = [a for a in agents if a.segment_id == segment.id]
            segment_converted = [a for a in segment_agents if a.final_decision == your_product_id]
            if segment_agents:
                segment_conversions[segment.id] = len(segment_converted) / len(segment_agents)

        return BranchResult(
            branch_id=seed,
            seed=seed,
            conversion_rate=conversion_rate,
            final_awareness=avg_awareness,
            avg_decision_day=avg_decision_day,
            segment_conversions=segment_conversions,
            timeline=timeline,
            competitor_responded=bool(market.competitor_responses),
            key_events=market.events_triggered
        )

    def _aggregate_results(
        self,
        branches: List[BranchResult],
        started_at: datetime
    ) -> SimulationResults:
        """Aggregate branch results into summary statistics"""

        conversions = [b.conversion_rate for b in branches]

        # Basic stats
        mean = np.mean(conversions)
        median = np.median(conversions)
        std = np.std(conversions)

        # Percentiles
        p5 = np.percentile(conversions, 5)
        p25 = np.percentile(conversions, 25)
        p75 = np.percentile(conversions, 75)
        p95 = np.percentile(conversions, 95)

        # Segment analysis
        segment_analysis = []
        for segment in self.scenario.segments:
            seg_conversions = [
                b.segment_conversions.get(segment.id, 0) for b in branches
            ]
            segment_analysis.append(SegmentAnalysis(
                segment_id=segment.id,
                segment_name=segment.name,
                conversion_rate=np.mean(seg_conversions),
                conversion_std=np.std(seg_conversions),
                avg_decision_day=0,  # TODO: calculate
                top_conversion_drivers=[],
                top_blockers=[]
            ))

        # Identify failure/success branches
        failure_threshold = np.percentile(conversions, 10)
        success_threshold = np.percentile(conversions, 90)

        failure_branches = [b.branch_id for b in branches if b.conversion_rate <= failure_threshold]
        success_branches = [b.branch_id for b in branches if b.conversion_rate >= success_threshold]

        # Analyze drivers
        top_drivers = self._analyze_drivers(branches, success_branches)
        top_blockers = self._analyze_blockers(branches, failure_branches)

        return SimulationResults(
            id=f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            scenario_id=self.scenario.id,
            strategy_id=self.strategy.id,
            num_agents=self.num_agents,
            num_branches=self.num_branches,
            started_at=started_at,
            completed_at=datetime.now(),
            mean_conversion=mean,
            median_conversion=median,
            std_conversion=std,
            p5=p5,
            p25=p25,
            p75=p75,
            p95=p95,
            segment_analysis=segment_analysis,
            top_drivers=top_drivers,
            top_blockers=top_blockers,
            branches=branches,
            failure_branches=failure_branches,
            success_branches=success_branches
        )

    def _analyze_drivers(
        self,
        branches: List[BranchResult],
        success_ids: List[int]
    ) -> List[DriverAnalysis]:
        """Analyze what drove success in top branches"""

        drivers = []

        # Check competitive response correlation
        success_branches = [b for b in branches if b.branch_id in success_ids]
        all_no_response = sum(1 for b in branches if not b.competitor_responded)
        success_no_response = sum(1 for b in success_branches if not b.competitor_responded)

        if all_no_response > 0:
            no_response_rate = success_no_response / len(success_branches) if success_branches else 0
            baseline_rate = all_no_response / len(branches) if branches else 0

            if no_response_rate > baseline_rate + 0.1:
                drivers.append(DriverAnalysis(
                    factor="No competitive response",
                    impact=no_response_rate - baseline_rate,
                    description="Success branches more likely when competitors didn't respond"
                ))

        # Segment performance
        for segment in self.scenario.segments:
            success_seg_conv = np.mean([
                b.segment_conversions.get(segment.id, 0) for b in success_branches
            ]) if success_branches else 0

            all_seg_conv = np.mean([
                b.segment_conversions.get(segment.id, 0) for b in branches
            ])

            if success_seg_conv > all_seg_conv + 0.02:
                drivers.append(DriverAnalysis(
                    factor=f"{segment.name} segment conversion",
                    impact=success_seg_conv - all_seg_conv,
                    description=f"Strong {segment.name} performance drove success"
                ))

        return sorted(drivers, key=lambda d: -d.impact)[:5]

    def _analyze_blockers(
        self,
        branches: List[BranchResult],
        failure_ids: List[int]
    ) -> List[DriverAnalysis]:
        """Analyze what blocked success in bottom branches"""

        blockers = []

        failure_branches = [b for b in branches if b.branch_id in failure_ids]

        # Competitive response correlation
        all_responded = sum(1 for b in branches if b.competitor_responded)
        failure_responded = sum(1 for b in failure_branches if b.competitor_responded)

        if failure_branches:
            failure_response_rate = failure_responded / len(failure_branches)
            baseline_rate = all_responded / len(branches) if branches else 0

            if failure_response_rate > baseline_rate + 0.1:
                blockers.append(DriverAnalysis(
                    factor="Competitive response",
                    impact=-(failure_response_rate - baseline_rate),
                    description="Failure branches more likely when competitors responded aggressively"
                ))

        return sorted(blockers, key=lambda d: d.impact)[:5]


# Worker function for multiprocessing
def _run_branch_worker(
    seed: int,
    scenario_dict: dict,
    strategy_dict: dict,
    num_agents: int,
    use_llm_personas: bool
) -> BranchResult:
    """Standalone worker function for parallel execution"""

    from backend.models import Scenario, Strategy

    scenario = Scenario(**scenario_dict)
    strategy = Strategy(**strategy_dict)

    runner = SimulationRunner(
        scenario=scenario,
        strategy=strategy,
        num_agents=num_agents,
        num_branches=1,
        use_llm_personas=use_llm_personas,
        parallel=False
    )

    return runner._run_single_branch(seed)
