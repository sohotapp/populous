"""
Market Dynamics - external forces affecting agents.
Handles GTM activities, competitive response, network effects.
"""

import random
from typing import List, Dict

from backend.models import Scenario, Strategy, Agent, Competitor


class MarketDynamics:
    """
    Manages market-level effects each simulation day.
    """

    def __init__(self, scenario: Scenario, strategy: Strategy):
        self.scenario = scenario
        self.strategy = strategy

        # Track competitive responses
        self.competitor_responses: Dict[str, int] = {}  # competitor_id -> response_day

        # Track key events
        self.events_triggered: List[str] = []

    def get_signals(
        self,
        day: int,
        agents: List[Agent]
    ) -> Dict[str, float]:
        """
        Calculate market signals for all products on a given day.
        Returns product_id -> signal_strength mapping.
        """

        signals = {}

        # Your product signal from GTM
        signals[self.scenario.your_product.id] = self._calculate_gtm_signal(day)

        # Competitor signals
        for competitor in self.scenario.competitors:
            signals[competitor.id] = self._calculate_competitor_signal(
                competitor, day
            )

        # Network effects (word of mouth)
        network_boost = self._calculate_network_effects(agents)
        for product_id, boost in network_boost.items():
            signals[product_id] = signals.get(product_id, 0) + boost

        return signals

    def _calculate_gtm_signal(self, day: int) -> float:
        """Calculate signal strength from your GTM activities"""

        # Not active before launch
        if day < self.strategy.launch_day:
            return 0.0

        days_since_launch = day - self.strategy.launch_day

        # Base signal from intensity
        base = self.strategy.gtm.intensity

        # Channel effectiveness curve
        # Ramp up over first 2 weeks, sustain, then gradual decay
        if days_since_launch < 14:
            time_factor = 0.5 + (days_since_launch / 14) * 0.5
        elif days_since_launch < 60:
            time_factor = 1.0
        else:
            time_factor = max(0.4, 1.0 - (days_since_launch - 60) * 0.008)

        # Channel mix effect (more channels = better coverage)
        active_channels = sum(1 for v in self.strategy.gtm.channels.values() if v > 0.1)
        channel_bonus = 1.0 + (active_channels - 3) * 0.05

        return base * time_factor * channel_bonus

    def _calculate_competitor_signal(
        self,
        competitor: Competitor,
        day: int
    ) -> float:
        """Calculate competitor's market signal"""

        # Base signal from existing presence - competitors have established presence
        # They should have significant baseline awareness from existing market share
        base = competitor.market_share * competitor.brand_awareness * 0.8

        # Add ongoing marketing presence (competitors don't just stop marketing)
        ongoing_marketing = competitor.market_share * 0.3

        # Check for competitive response
        if competitor.id not in self.competitor_responses:
            if self._should_respond(competitor, day):
                self.competitor_responses[competitor.id] = day
                self.events_triggered.append(
                    f"Day {day}: {competitor.name} launched competitive response"
                )

        # Response boost
        if competitor.id in self.competitor_responses:
            response_day = self.competitor_responses[competitor.id]
            days_responding = day - response_day

            if 0 <= days_responding < 30:
                # Strong response for first 30 days
                response_boost = competitor.aggression * 0.4
                base += response_boost

        return base + ongoing_marketing

    def _should_respond(self, competitor: Competitor, day: int) -> bool:
        """Determine if competitor triggers a response"""

        # Only respond after your launch + some delay
        min_response_day = self.strategy.launch_day + 14
        if day < min_response_day:
            return False

        # Daily probability based on aggression
        daily_prob = competitor.aggression * 0.04

        # Higher probability if you're doing well
        if self.strategy.gtm.intensity > 0.7:
            daily_prob *= 1.3

        return random.random() < daily_prob

    def _calculate_network_effects(
        self,
        agents: List[Agent]
    ) -> Dict[str, float]:
        """Word of mouth from decided agents"""

        boost: Dict[str, float] = {}

        decided_agents = [
            a for a in agents
            if a.stage == "Decided" and a.final_decision
        ]

        # Count influence by product
        for agent in decided_agents:
            product_id = agent.final_decision
            # Agent's influence spreads to their network
            spread = agent.influence_score * 0.008 * len(agent.connections)
            boost[product_id] = boost.get(product_id, 0) + spread

        return boost
