"""
Competitor Agent Model
Game-theoretic competitor agents that respond to strategic moves
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum
import math
import numpy as np

from backend.models.company import Company


class StrategyType(str, Enum):
    """Competitor strategy archetypes"""
    AGGRESSIVE = "aggressive"      # Maximizes market share, responds strongly
    DEFENSIVE = "defensive"        # Protects position, matches threats
    OPPORTUNISTIC = "opportunistic"  # Waits for weakness, then strikes
    PASSIVE = "passive"            # Focuses on own roadmap, ignores competitors


class ResponseSpeed(str, Enum):
    """How quickly competitor responds to market moves"""
    IMMEDIATE = "immediate"  # 1-3 days
    FAST = "fast"            # 1 week
    NORMAL = "normal"        # 2 weeks
    SLOW = "slow"            # 1 month


class MoveType(str, Enum):
    """Types of competitive moves"""
    PRICE_CHANGE = "price_change"
    FEATURE_LAUNCH = "feature_launch"
    MARKETING_CAMPAIGN = "marketing_campaign"
    PARTNERSHIP = "partnership"
    ACQUISITION = "acquisition"
    MARKET_EXPANSION = "market_expansion"


class CompetitorMove(BaseModel):
    """A move made by a competitor"""
    id: str = Field(default_factory=lambda: f"move_{datetime.now().timestamp()}")
    move_type: MoveType
    description: str
    parameters: Dict = {}  # e.g., {"price_change_percent": -10}
    rationale: str = ""
    delay_days: int = 7  # When the move happens
    impact_estimate: float = 0.0  # Estimated impact on market
    confidence: float = 0.7


class PayoffWeights(BaseModel):
    """Weights for calculating competitor payoff"""
    market_share: float = 0.3
    revenue: float = 0.25
    profit_margin: float = 0.2
    growth: float = 0.15
    risk_aversion: float = 0.1

    @classmethod
    def from_strategy(cls, strategy: StrategyType) -> 'PayoffWeights':
        """Get payoff weights based on strategy type"""
        weights = {
            StrategyType.AGGRESSIVE: cls(
                market_share=0.40, revenue=0.20, profit_margin=0.10,
                growth=0.25, risk_aversion=0.05
            ),
            StrategyType.DEFENSIVE: cls(
                market_share=0.30, revenue=0.25, profit_margin=0.20,
                growth=0.10, risk_aversion=0.15
            ),
            StrategyType.OPPORTUNISTIC: cls(
                market_share=0.20, revenue=0.30, profit_margin=0.25,
                growth=0.15, risk_aversion=0.10
            ),
            StrategyType.PASSIVE: cls(
                market_share=0.15, revenue=0.25, profit_margin=0.35,
                growth=0.10, risk_aversion=0.15
            )
        }
        return weights.get(strategy, cls())


class MarketState(BaseModel):
    """Current state of the market for payoff calculations"""
    our_share: float = 0.2
    our_revenue: float = 1.0  # Normalized
    our_margin: float = 0.3
    our_growth: float = 0.1
    competitor_shares: Dict[str, float] = {}
    total_market_size: float = 1.0
    market_growth: float = 0.1
    uncertainty: float = 0.2


class CompetitorBelief(BaseModel):
    """What the competitor believes about you"""
    your_strategy: str = "unknown"
    your_strategy_probabilities: Dict[str, float] = {
        "aggressive": 0.25,
        "defensive": 0.25,
        "opportunistic": 0.25,
        "passive": 0.25
    }
    your_next_move_prediction: Optional[str] = None
    your_resources: str = "moderate"
    your_risk_tolerance: float = 0.5


class CompetitorHistory(BaseModel):
    """Historical record of competitor behavior"""
    moves_made: List[CompetitorMove] = []
    responses_to_your_moves: List[Dict] = []
    average_response_time_days: float = 14.0
    aggression_score: float = 0.5
    predictability_score: float = 0.5
    cooperation_tendency: float = 0.5


class CompetitorAgent(BaseModel):
    """
    A game-theoretic competitor agent.
    Models a competitor company that observes and responds to your moves.
    """
    id: str = Field(default_factory=lambda: f"competitor_{datetime.now().timestamp()}")

    # Company info
    company: Company
    name: str = ""  # Convenience field

    # Strategy parameters
    strategy_type: StrategyType = StrategyType.DEFENSIVE
    risk_tolerance: float = 0.5  # 0-1, higher = more willing to take risks
    response_speed: ResponseSpeed = ResponseSpeed.NORMAL
    price_sensitivity: float = 0.7  # How likely to respond to price changes
    feature_sensitivity: float = 0.5  # How likely to respond to features

    # Resources
    marketing_budget: str = "medium"  # low, medium, high
    engineering_velocity: str = "medium"  # How fast they ship
    cash_reserves: str = "medium"

    # Game theory parameters
    payoff_weights: PayoffWeights = Field(default_factory=PayoffWeights)
    temperature: float = 1.0  # For softmax decisions (lower = more deterministic)

    # State
    beliefs: CompetitorBelief = Field(default_factory=CompetitorBelief)
    history: CompetitorHistory = Field(default_factory=CompetitorHistory)
    current_market_state: MarketState = Field(default_factory=MarketState)

    def __init__(self, **data):
        super().__init__(**data)
        if not self.name:
            self.name = self.company.name
        if self.payoff_weights == PayoffWeights():
            self.payoff_weights = PayoffWeights.from_strategy(self.strategy_type)

    def observe_move(self, move: Dict, market_state: MarketState):
        """
        Observe a competitor (your) move and update beliefs.
        """
        self.current_market_state = market_state
        self.history.responses_to_your_moves.append({
            "move": move,
            "market_state": market_state.model_dump(),
            "timestamp": datetime.now().isoformat()
        })

        # Update beliefs about your strategy
        self._update_beliefs(move)

    def _update_beliefs(self, move: Dict):
        """
        Bayesian update of beliefs about your strategy.
        """
        move_type = move.get("type", "")

        # Likelihood of this move given each strategy type
        likelihoods = {
            "aggressive": 0.25,
            "defensive": 0.25,
            "opportunistic": 0.25,
            "passive": 0.25
        }

        if move_type == "price_change":
            change = move.get("percent", 0)
            if change < -10:  # Big price cut
                likelihoods = {"aggressive": 0.5, "defensive": 0.1, "opportunistic": 0.3, "passive": 0.1}
            elif change < 0:  # Small price cut
                likelihoods = {"aggressive": 0.3, "defensive": 0.2, "opportunistic": 0.4, "passive": 0.1}
            elif change > 10:  # Big price increase
                likelihoods = {"aggressive": 0.1, "defensive": 0.3, "opportunistic": 0.2, "passive": 0.4}
            else:  # Small price increase
                likelihoods = {"aggressive": 0.2, "defensive": 0.4, "opportunistic": 0.2, "passive": 0.2}

        elif move_type == "feature_launch":
            likelihoods = {"aggressive": 0.35, "defensive": 0.25, "opportunistic": 0.25, "passive": 0.15}

        elif move_type == "marketing_campaign":
            intensity = move.get("intensity", "medium")
            if intensity == "high":
                likelihoods = {"aggressive": 0.45, "defensive": 0.2, "opportunistic": 0.25, "passive": 0.1}
            else:
                likelihoods = {"aggressive": 0.25, "defensive": 0.3, "opportunistic": 0.3, "passive": 0.15}

        # Bayes update
        prior = self.beliefs.your_strategy_probabilities
        total = sum(likelihoods[s] * prior.get(s, 0.25) for s in likelihoods)

        for strategy in likelihoods:
            posterior = (likelihoods[strategy] * prior.get(strategy, 0.25)) / total
            self.beliefs.your_strategy_probabilities[strategy] = posterior

        # Update dominant strategy belief
        self.beliefs.your_strategy = max(
            self.beliefs.your_strategy_probabilities,
            key=self.beliefs.your_strategy_probabilities.get
        )

    def decide_response(
        self,
        your_move: Dict,
        market_state: Optional[MarketState] = None
    ) -> Optional[CompetitorMove]:
        """
        Decide whether and how to respond to a move.
        Uses game-theoretic reasoning.
        """
        if market_state:
            self.current_market_state = market_state

        # Generate possible responses
        possible_responses = self._generate_possible_responses(your_move)

        if not possible_responses:
            return None

        # Calculate payoff for each response
        response_payoffs = []
        for response in possible_responses:
            future_state = self._simulate_future(response)
            payoff = self._calculate_payoff(future_state)
            response_payoffs.append((response, payoff))

        # Calculate payoff for no response
        no_response_state = self._simulate_future(None)
        no_response_payoff = self._calculate_payoff(no_response_state)

        # Use softmax to select response (or no response)
        all_options = response_payoffs + [(None, no_response_payoff)]
        probabilities = self._softmax_selection([p for _, p in all_options])

        # For now, select best response if it clearly beats no-response
        best_response, best_payoff = max(response_payoffs, key=lambda x: x[1])

        # Threshold based on risk tolerance
        threshold = 0.05 * (1 - self.risk_tolerance)

        if best_payoff > no_response_payoff + threshold:
            # Add timing
            best_response.delay_days = self._get_response_delay()
            self.history.moves_made.append(best_response)
            return best_response

        return None

    def _generate_possible_responses(self, your_move: Dict) -> List[CompetitorMove]:
        """
        Generate possible response moves based on your move type.
        """
        responses = []
        move_type = your_move.get("type", "")

        if move_type == "price_change":
            percent = your_move.get("percent", 0)

            # Match price
            responses.append(CompetitorMove(
                move_type=MoveType.PRICE_CHANGE,
                description=f"Match price change of {percent}%",
                parameters={"price_change_percent": percent},
                rationale="match_competitor"
            ))

            if percent > 0:  # You raised price
                # Hold and take share
                responses.append(CompetitorMove(
                    move_type=MoveType.PRICE_CHANGE,
                    description="Hold price to gain price-sensitive customers",
                    parameters={"price_change_percent": 0},
                    rationale="capture_share"
                ))

                # Undercut
                responses.append(CompetitorMove(
                    move_type=MoveType.PRICE_CHANGE,
                    description="Undercut with 5% reduction",
                    parameters={"price_change_percent": -5},
                    rationale="aggressive_capture"
                ))

            else:  # You lowered price
                # Match or undercut more
                responses.append(CompetitorMove(
                    move_type=MoveType.PRICE_CHANGE,
                    description="Undercut further",
                    parameters={"price_change_percent": percent - 5},
                    rationale="price_war"
                ))

            # Differentiate instead
            responses.append(CompetitorMove(
                move_type=MoveType.FEATURE_LAUNCH,
                description="Launch differentiating features instead of matching price",
                parameters={"features": ["enhanced_support", "new_integration"]},
                rationale="differentiate"
            ))

            # Marketing response
            responses.append(CompetitorMove(
                move_type=MoveType.MARKETING_CAMPAIGN,
                description="Value-focused marketing campaign",
                parameters={"intensity": "high", "message": "value_over_price"},
                rationale="perception_defense"
            ))

        elif move_type == "feature_launch":
            # Announce similar feature
            responses.append(CompetitorMove(
                move_type=MoveType.FEATURE_LAUNCH,
                description="Announce matching feature",
                parameters={"features": ["similar_feature"], "timeline": "soon"},
                rationale="feature_parity"
            ))

            # Compete on price instead
            responses.append(CompetitorMove(
                move_type=MoveType.PRICE_CHANGE,
                description="Price reduction to compete",
                parameters={"price_change_percent": -10},
                rationale="price_competition"
            ))

            # Double down on existing strengths
            responses.append(CompetitorMove(
                move_type=MoveType.MARKETING_CAMPAIGN,
                description="Highlight existing differentiators",
                parameters={"intensity": "medium", "message": "our_strengths"},
                rationale="reinforce_position"
            ))

        elif move_type == "marketing_campaign":
            # Counter-campaign
            responses.append(CompetitorMove(
                move_type=MoveType.MARKETING_CAMPAIGN,
                description="Counter marketing campaign",
                parameters={"intensity": "high", "message": "counter_narrative"},
                rationale="share_of_voice"
            ))

        return responses

    def _simulate_future(self, response: Optional[CompetitorMove]) -> MarketState:
        """
        Simulate market state after a response.
        """
        future = MarketState(
            our_share=self.current_market_state.our_share,
            our_revenue=self.current_market_state.our_revenue,
            our_margin=self.current_market_state.our_margin,
            our_growth=self.current_market_state.our_growth
        )

        if response is None:
            # No response - competitor gains from their move
            future.our_share *= 0.98
            return future

        if response.move_type == MoveType.PRICE_CHANGE:
            percent = response.parameters.get("price_change_percent", 0)
            if percent < 0:
                # Price reduction - gain share, lose margin
                share_gain = abs(percent) * 0.005
                future.our_share *= (1 + share_gain)
                future.our_margin *= (1 + percent / 100)
            else:
                # Price increase - lose share, gain margin
                share_loss = percent * 0.003
                future.our_share *= (1 - share_loss)
                future.our_margin *= (1 + percent / 200)

        elif response.move_type == MoveType.FEATURE_LAUNCH:
            future.our_share *= 1.03
            future.our_margin *= 0.98  # R&D cost

        elif response.move_type == MoveType.MARKETING_CAMPAIGN:
            intensity = response.parameters.get("intensity", "medium")
            if intensity == "high":
                future.our_share *= 1.04
                future.our_margin *= 0.95  # Campaign cost
            else:
                future.our_share *= 1.02
                future.our_margin *= 0.98

        return future

    def _calculate_payoff(self, future_state: MarketState) -> float:
        """
        Calculate payoff for a future state.
        """
        w = self.payoff_weights
        return (
            w.market_share * future_state.our_share +
            w.revenue * future_state.our_revenue +
            w.profit_margin * future_state.our_margin +
            w.growth * future_state.our_growth -
            w.risk_aversion * self.current_market_state.uncertainty
        )

    def _softmax_selection(self, payoffs: List[float]) -> List[float]:
        """
        Apply softmax to convert payoffs to probabilities.
        """
        exp_payoffs = [math.exp(p / self.temperature) for p in payoffs]
        total = sum(exp_payoffs)
        return [e / total for e in exp_payoffs]

    def _get_response_delay(self) -> int:
        """
        Get response delay in days based on response speed.
        """
        delays = {
            ResponseSpeed.IMMEDIATE: 2,
            ResponseSpeed.FAST: 7,
            ResponseSpeed.NORMAL: 14,
            ResponseSpeed.SLOW: 30
        }
        return delays.get(self.response_speed, 14)

    def get_response_probability(self, your_move: Dict) -> Dict[str, float]:
        """
        Get probability distribution over possible responses.
        """
        possible_responses = self._generate_possible_responses(your_move)
        if not possible_responses:
            return {"no_response": 1.0}

        # Calculate payoffs
        payoffs = []
        labels = []

        for response in possible_responses:
            future_state = self._simulate_future(response)
            payoff = self._calculate_payoff(future_state)
            payoffs.append(payoff)
            labels.append(response.description)

        # Add no-response option
        no_response_state = self._simulate_future(None)
        payoffs.append(self._calculate_payoff(no_response_state))
        labels.append("no_response")

        # Convert to probabilities
        probabilities = self._softmax_selection(payoffs)

        return dict(zip(labels, probabilities))


class GameTheoreticAnalysis(BaseModel):
    """
    Analysis of game-theoretic dynamics between you and competitors.
    """
    your_move: Dict
    competitors: List[str]

    # Per-competitor analysis
    competitor_responses: Dict[str, Dict] = {}  # competitor_id -> {response, probability}

    # Aggregate analysis
    most_likely_scenario: str = ""
    scenario_probabilities: Dict[str, float] = {}

    # Nash equilibrium if applicable
    nash_equilibrium: Optional[Dict] = None

    # Recommendations
    recommended_counter_strategies: List[str] = []
    risk_factors: List[str] = []
