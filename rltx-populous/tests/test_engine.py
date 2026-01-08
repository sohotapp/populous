"""
Test simulation engine components.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import Agent, Segment, DecisionFramework, BehavioralProfile, Stakeholder
from backend.engine import AgentFactory, DecisionEngine, MarketDynamics, SimulationRunner
from backend.data.presets.b2b_saas import get_saas_launch_scenario, get_demo_strategies


class TestAgentFactory:
    """Tests for AgentFactory"""

    def test_creates_correct_number_of_agents(self):
        """Test that agent factory creates the requested number of agents"""
        scenario = get_saas_launch_scenario()
        factory = AgentFactory(use_llm=False)

        agents = factory.create_population(scenario.segments, 1000)

        assert len(agents) == 1000
        assert all(isinstance(a, Agent) for a in agents)

    def test_segment_distribution(self):
        """Test that agents are distributed correctly across segments"""
        scenario = get_saas_launch_scenario()
        factory = AgentFactory(use_llm=False)

        agents = factory.create_population(scenario.segments, 1000)

        # Count by segment
        smb_count = sum(1 for a in agents if a.segment_id == "smb")
        mid_market_count = sum(1 for a in agents if a.segment_id == "mid_market")
        enterprise_count = sum(1 for a in agents if a.segment_id == "enterprise")

        # SMB should be ~50%, mid-market ~35%, enterprise ~15%
        assert 400 < smb_count < 600  # ~50% with variance
        assert 250 < mid_market_count < 450  # ~35% with variance
        assert 100 < enterprise_count < 250  # ~15% with variance

    def test_behavioral_parameters_bounded(self):
        """Test that behavioral parameters are within bounds"""
        scenario = get_saas_launch_scenario()
        factory = AgentFactory(use_llm=False)

        agents = factory.create_population(scenario.segments, 100)

        for agent in agents:
            assert 0 <= agent.risk_tolerance <= 1
            assert 0 <= agent.price_sensitivity <= 1
            assert 0 <= agent.decision_speed <= 1
            assert 0 <= agent.influencer_susceptibility <= 1
            assert 0 <= agent.influence_score <= 1

    def test_network_creation(self):
        """Test that social network is created"""
        scenario = get_saas_launch_scenario()
        factory = AgentFactory(use_llm=False)

        agents = factory.create_population(scenario.segments, 100)

        # At least some agents should have connections
        connected_agents = sum(1 for a in agents if len(a.connections) > 0)
        assert connected_agents > 50  # Most agents should have connections


class TestDecisionEngine:
    """Tests for DecisionEngine"""

    def test_awareness_updates(self):
        """Test that awareness updates work correctly"""
        engine = DecisionEngine()

        agent = Agent(
            id="test_1",
            segment_id="smb",
            risk_tolerance=0.5,
            price_sensitivity=0.5,
            feature_priorities={"ease_of_use": 0.8},
            decision_speed=0.5,
            influencer_susceptibility=0.5,
            stage="Unaware",
            awareness={},
            consideration_set=[],
            connections=[]
        )

        signals = {"product_a": 0.5}

        agent = engine._update_awareness(agent, signals, day=1)

        assert "product_a" in agent.awareness
        assert agent.awareness["product_a"] > 0

    def test_stage_progression(self):
        """Test that agents progress through stages"""
        scenario = get_saas_launch_scenario()
        engine = DecisionEngine()

        agent = Agent(
            id="test_1",
            segment_id="smb",
            risk_tolerance=0.5,
            price_sensitivity=0.5,
            feature_priorities={"ease_of_use": 0.8},
            decision_speed=0.5,
            influencer_susceptibility=0.5,
            stage="Unaware",
            awareness={"product_a": 0.3},
            consideration_set=[],
            connections=[]
        )

        # Should progress to Aware
        agent = engine._update_stage(agent, scenario.your_product, [], day=1)
        assert agent.stage == "Aware"

        # Increase awareness further
        agent.awareness["product_a"] = 0.6
        agent = engine._update_stage(agent, scenario.your_product, [], day=2)
        assert agent.stage == "Considering"

    def test_score_product_returns_valid_range(self):
        """Test that product scoring returns values in expected range"""
        scenario = get_saas_launch_scenario()
        strategy = get_demo_strategies()[0]
        engine = DecisionEngine()

        agent = Agent(
            id="test_1",
            segment_id="smb",
            risk_tolerance=0.5,
            price_sensitivity=0.5,
            feature_priorities={"ease_of_use": 0.8, "security": 0.3},
            decision_speed=0.5,
            influencer_susceptibility=0.5,
            stage="Evaluating",
            awareness={"nexus": 0.8},
            consideration_set=["nexus"],
            connections=[]
        )

        score = engine._score_product(agent, scenario.your_product, strategy)

        # Score should be between 0 and 1
        assert 0 <= score <= 1


class TestMarketDynamics:
    """Tests for MarketDynamics"""

    def test_signals_for_all_products(self):
        """Test that signals are generated for all products"""
        scenario = get_saas_launch_scenario()
        strategy = get_demo_strategies()[0]

        market = MarketDynamics(scenario, strategy)

        signals = market.get_signals(day=30, agents=[])

        # Should have signal for your product
        assert scenario.your_product.id in signals

        # Should have signals for all competitors
        for competitor in scenario.competitors:
            assert competitor.id in signals

    def test_gtm_signal_before_launch(self):
        """Test that GTM signal is 0 before launch day"""
        scenario = get_saas_launch_scenario()
        strategy = get_demo_strategies()[0]
        strategy.launch_day = 10  # Launch on day 10

        market = MarketDynamics(scenario, strategy)

        # Before launch
        signal_before = market._calculate_gtm_signal(day=5)
        assert signal_before == 0

        # After launch
        signal_after = market._calculate_gtm_signal(day=15)
        assert signal_after > 0

    def test_competitive_response_not_immediate(self):
        """Test that competitors don't respond immediately"""
        scenario = get_saas_launch_scenario()
        strategy = get_demo_strategies()[0]

        market = MarketDynamics(scenario, strategy)

        # On day 1, no competitor should have responded
        competitor = scenario.competitors[0]
        assert not market._should_respond(competitor, day=1)


class TestSimulationRunner:
    """Tests for SimulationRunner"""

    def test_simulation_completes(self):
        """Test that simulation runs to completion"""
        scenario = get_saas_launch_scenario()
        strategy = get_demo_strategies()[0]

        runner = SimulationRunner(
            scenario=scenario,
            strategy=strategy,
            num_agents=500,
            num_branches=10,
            use_llm_personas=False,
            parallel=False
        )

        results = runner.run()

        assert results is not None
        assert results.mean_conversion >= 0
        assert results.mean_conversion <= 1
        assert len(results.branches) == 10

    def test_results_have_valid_statistics(self):
        """Test that results have valid statistical properties"""
        scenario = get_saas_launch_scenario()
        strategy = get_demo_strategies()[0]

        runner = SimulationRunner(
            scenario=scenario,
            strategy=strategy,
            num_agents=500,
            num_branches=20,
            use_llm_personas=False,
            parallel=False
        )

        results = runner.run()

        # Percentiles should be in order
        assert results.p5 <= results.p25
        assert results.p25 <= results.median_conversion
        assert results.median_conversion <= results.p75
        assert results.p75 <= results.p95

        # Standard deviation should be non-negative
        assert results.std_conversion >= 0

    def test_segment_analysis_complete(self):
        """Test that all segments are analyzed"""
        scenario = get_saas_launch_scenario()
        strategy = get_demo_strategies()[0]

        runner = SimulationRunner(
            scenario=scenario,
            strategy=strategy,
            num_agents=500,
            num_branches=10,
            use_llm_personas=False,
            parallel=False
        )

        results = runner.run()

        # Should have analysis for each segment
        assert len(results.segment_analysis) == len(scenario.segments)

        segment_ids = {s.segment_id for s in results.segment_analysis}
        expected_ids = {s.id for s in scenario.segments}
        assert segment_ids == expected_ids


class TestDemoScenario:
    """Tests for demo scenario data"""

    def test_scenario_loads(self):
        """Test that demo scenario loads correctly"""
        scenario = get_saas_launch_scenario()

        assert scenario.id == "saas_launch_2024"
        assert scenario.total_addressable_market == 50000
        assert len(scenario.segments) == 3
        assert len(scenario.competitors) == 3

    def test_strategies_load(self):
        """Test that demo strategies load correctly"""
        strategies = get_demo_strategies()

        assert len(strategies) == 3
        assert strategies[0].id == "value_play"
        assert strategies[1].id == "enterprise_premium"
        assert strategies[2].id == "market_blitz"

    def test_segment_sizes_sum_to_one(self):
        """Test that segment sizes sum to approximately 1"""
        scenario = get_saas_launch_scenario()

        total_size = sum(s.size_pct for s in scenario.segments)
        assert 0.99 <= total_size <= 1.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
