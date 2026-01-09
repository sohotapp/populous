"""
Competitor Engine
Game-theoretic analysis and competitor response prediction
"""

import os
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from itertools import product
from anthropic import Anthropic

from backend.models.company import Company
from backend.models.competitor_agent import (
    CompetitorAgent, StrategyType, ResponseSpeed, PayoffWeights,
    MarketState, CompetitorMove, MoveType, GameTheoreticAnalysis
)


class CompetitorEngine:
    """
    Engine for game-theoretic competitor analysis.
    """

    def __init__(self, llm_client: Anthropic = None):
        self.llm = llm_client or Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def generate_competitor_agents(
        self,
        companies: List[Company],
        your_company: Optional[Company] = None
    ) -> List[CompetitorAgent]:
        """
        Generate competitor agents from company profiles.
        Uses LLM to infer strategy parameters.
        """
        agents = []

        for company in companies:
            # Infer strategy from company profile
            strategy_params = self._infer_strategy(company, your_company)

            agent = CompetitorAgent(
                company=company,
                name=company.name,
                strategy_type=strategy_params["strategy_type"],
                risk_tolerance=strategy_params["risk_tolerance"],
                response_speed=strategy_params["response_speed"],
                price_sensitivity=strategy_params["price_sensitivity"],
                feature_sensitivity=strategy_params["feature_sensitivity"],
                marketing_budget=strategy_params["marketing_budget"],
                engineering_velocity=strategy_params["engineering_velocity"]
            )

            agents.append(agent)

        return agents

    def _infer_strategy(
        self,
        company: Company,
        your_company: Optional[Company] = None
    ) -> Dict:
        """
        Use LLM to infer competitor strategy from company profile.
        """
        prompt = f"""Analyze this company and infer their competitive strategy:

COMPANY: {company.name}
Industry: {company.industry}
Market Position: {company.market_position.value if hasattr(company.market_position, 'value') else company.market_position}
Strengths: {', '.join(company.strengths[:3]) if company.strengths else 'Unknown'}
Weaknesses: {', '.join(company.weaknesses[:3]) if company.weaknesses else 'Unknown'}
Pricing Strategy: {company.pricing_strategy or 'Unknown'}
Growth Strategy: {company.growth_strategy or 'Unknown'}
Funding: {company.funding_stage.value if company.funding_stage else 'Unknown'}

Based on this profile, classify their competitive behavior:

Return JSON:
{{
    "strategy_type": "aggressive" | "defensive" | "opportunistic" | "passive",
    "risk_tolerance": 0.0-1.0,
    "response_speed": "immediate" | "fast" | "normal" | "slow",
    "price_sensitivity": 0.0-1.0,
    "feature_sensitivity": 0.0-1.0,
    "marketing_budget": "low" | "medium" | "high",
    "engineering_velocity": "low" | "medium" | "high",
    "reasoning": "Brief explanation"
}}

Consider:
- Market leaders often defensive
- Well-funded startups often aggressive
- Cash-strapped companies often passive
- Companies with strong products often opportunistic"""

        try:
            response = self.llm.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            text = response.content[0].text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(text[start:end])
                return {
                    "strategy_type": StrategyType(data.get("strategy_type", "defensive")),
                    "risk_tolerance": float(data.get("risk_tolerance", 0.5)),
                    "response_speed": ResponseSpeed(data.get("response_speed", "normal")),
                    "price_sensitivity": float(data.get("price_sensitivity", 0.5)),
                    "feature_sensitivity": float(data.get("feature_sensitivity", 0.5)),
                    "marketing_budget": data.get("marketing_budget", "medium"),
                    "engineering_velocity": data.get("engineering_velocity", "medium")
                }
        except Exception as e:
            print(f"Strategy inference failed: {e}")

        # Default values
        return {
            "strategy_type": StrategyType.DEFENSIVE,
            "risk_tolerance": 0.5,
            "response_speed": ResponseSpeed.NORMAL,
            "price_sensitivity": 0.5,
            "feature_sensitivity": 0.5,
            "marketing_budget": "medium",
            "engineering_velocity": "medium"
        }

    def predict_responses(
        self,
        your_move: Dict,
        competitors: List[CompetitorAgent],
        market_state: Optional[MarketState] = None
    ) -> GameTheoreticAnalysis:
        """
        Predict how competitors will respond to your move.
        """
        if market_state is None:
            market_state = MarketState()

        competitor_responses = {}
        all_scenarios = []

        for competitor in competitors:
            # Get response probability distribution
            response_probs = competitor.get_response_probability(your_move)

            # Get most likely response
            most_likely = max(response_probs, key=response_probs.get)
            most_likely_prob = response_probs[most_likely]

            # Get actual response decision
            actual_response = competitor.decide_response(your_move, market_state)

            competitor_responses[competitor.id] = {
                "name": competitor.name,
                "most_likely_response": most_likely,
                "probability": most_likely_prob,
                "all_probabilities": response_probs,
                "predicted_response": actual_response.model_dump() if actual_response else None,
                "response_delay_days": actual_response.delay_days if actual_response else None,
                "strategy_type": competitor.strategy_type.value
            }

        # Calculate scenario probabilities
        scenario_probs = self._calculate_scenario_probabilities(competitor_responses)

        # Find Nash equilibrium if applicable
        nash = self._find_nash_equilibrium(your_move, competitors, market_state)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            your_move, competitor_responses, scenario_probs
        )

        return GameTheoreticAnalysis(
            your_move=your_move,
            competitors=[c.name for c in competitors],
            competitor_responses=competitor_responses,
            most_likely_scenario=max(scenario_probs, key=scenario_probs.get) if scenario_probs else "",
            scenario_probabilities=scenario_probs,
            nash_equilibrium=nash,
            recommended_counter_strategies=recommendations["strategies"],
            risk_factors=recommendations["risks"]
        )

    def _calculate_scenario_probabilities(
        self,
        competitor_responses: Dict[str, Dict]
    ) -> Dict[str, float]:
        """
        Calculate probabilities for different competitive scenarios.
        """
        if not competitor_responses:
            return {"no_competition": 1.0}

        scenarios = {}

        # Simplified scenario calculation
        all_respond = 1.0
        none_respond = 1.0
        some_respond = 0.0

        for comp_id, data in competitor_responses.items():
            respond_prob = 1 - data["all_probabilities"].get("no_response", 0.3)
            all_respond *= respond_prob
            none_respond *= (1 - respond_prob)

        some_respond = 1 - all_respond - none_respond

        scenarios["all_competitors_respond"] = round(all_respond, 3)
        scenarios["no_competitor_responds"] = round(none_respond, 3)
        scenarios["partial_response"] = round(some_respond, 3)

        # More detailed scenarios based on response types
        price_war_prob = 0.0
        feature_race_prob = 0.0

        for comp_id, data in competitor_responses.items():
            probs = data["all_probabilities"]
            # Check for price-related responses
            for key, prob in probs.items():
                if "price" in key.lower():
                    price_war_prob += prob * 0.3
                if "feature" in key.lower():
                    feature_race_prob += prob * 0.3

        scenarios["price_war_escalation"] = round(min(price_war_prob, 0.5), 3)
        scenarios["feature_race"] = round(min(feature_race_prob, 0.4), 3)

        return scenarios

    def _find_nash_equilibrium(
        self,
        your_move: Dict,
        competitors: List[CompetitorAgent],
        market_state: MarketState
    ) -> Optional[Dict]:
        """
        Find Nash equilibrium for the competitive game.
        Simplified 2-player version for now.
        """
        if len(competitors) == 0:
            return None

        # Focus on the primary competitor
        competitor = competitors[0]

        # Define strategy spaces
        your_strategies = ["maintain", "escalate", "de-escalate"]
        their_strategies = ["match", "undercut", "ignore", "differentiate"]

        # Build payoff matrix
        # your_payoff[your_strategy][their_strategy]
        # Simplified payoffs based on game theory principles

        payoff_matrix = np.array([
            #          match   undercut  ignore  differentiate
            [0.5, 0.3, 0.7, 0.5],     # maintain
            [0.4, 0.2, 0.8, 0.4],     # escalate
            [0.6, 0.5, 0.5, 0.6],     # de-escalate
        ])

        their_payoff_matrix = np.array([
            #          match   undercut  ignore  differentiate
            [0.5, 0.6, 0.3, 0.5],     # maintain
            [0.7, 0.4, 0.2, 0.6],     # escalate
            [0.4, 0.5, 0.5, 0.4],     # de-escalate
        ])

        # Find pure strategy Nash equilibrium
        nash = self._find_pure_nash(payoff_matrix, their_payoff_matrix)

        if nash:
            return {
                "type": "pure_strategy",
                "your_strategy": your_strategies[nash[0]],
                "their_strategy": their_strategies[nash[1]],
                "your_payoff": float(payoff_matrix[nash[0], nash[1]]),
                "their_payoff": float(their_payoff_matrix[nash[0], nash[1]]),
                "interpretation": self._interpret_nash(
                    your_strategies[nash[0]],
                    their_strategies[nash[1]]
                )
            }

        # If no pure Nash, calculate mixed strategy
        mixed = self._find_mixed_nash(payoff_matrix, their_payoff_matrix)
        if mixed:
            return {
                "type": "mixed_strategy",
                "your_probabilities": dict(zip(your_strategies, mixed[0].tolist())),
                "their_probabilities": dict(zip(their_strategies, mixed[1].tolist())),
                "interpretation": "No dominant strategy - optimal play involves randomization"
            }

        return None

    def _find_pure_nash(
        self,
        your_payoffs: np.ndarray,
        their_payoffs: np.ndarray
    ) -> Optional[Tuple[int, int]]:
        """
        Find pure strategy Nash equilibrium.
        """
        n_your = your_payoffs.shape[0]
        n_their = your_payoffs.shape[1]

        for i in range(n_your):
            for j in range(n_their):
                # Check if i is best response to j
                your_best_response = True
                for i2 in range(n_your):
                    if your_payoffs[i2, j] > your_payoffs[i, j]:
                        your_best_response = False
                        break

                # Check if j is best response to i
                their_best_response = True
                for j2 in range(n_their):
                    if their_payoffs[i, j2] > their_payoffs[i, j]:
                        their_best_response = False
                        break

                if your_best_response and their_best_response:
                    return (i, j)

        return None

    def _find_mixed_nash(
        self,
        your_payoffs: np.ndarray,
        their_payoffs: np.ndarray
    ) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Find mixed strategy Nash equilibrium (simplified).
        """
        # For simplicity, return uniform distribution
        n_your = your_payoffs.shape[0]
        n_their = your_payoffs.shape[1]

        return (
            np.ones(n_your) / n_your,
            np.ones(n_their) / n_their
        )

    def _interpret_nash(self, your_strategy: str, their_strategy: str) -> str:
        """
        Generate interpretation of Nash equilibrium.
        """
        interpretations = {
            ("maintain", "match"): "Stable equilibrium - both sides maintain current positions",
            ("maintain", "undercut"): "They will undercut - consider pre-emptive action",
            ("maintain", "ignore"): "Favorable outcome - they ignore your move",
            ("maintain", "differentiate"): "They differentiate - competition shifts to features",
            ("escalate", "match"): "Escalation matched - risk of price war",
            ("escalate", "undercut"): "Price war likely - reconsider escalation",
            ("escalate", "ignore"): "Escalation succeeds - but monitor for delayed response",
            ("de-escalate", "match"): "De-escalation matched - stable outcome",
            ("de-escalate", "ignore"): "Peaceful equilibrium achieved",
        }

        return interpretations.get(
            (your_strategy, their_strategy),
            "Complex equilibrium - monitor closely"
        )

    def _generate_recommendations(
        self,
        your_move: Dict,
        competitor_responses: Dict[str, Dict],
        scenario_probs: Dict[str, float]
    ) -> Dict:
        """
        Generate strategic recommendations based on analysis.
        """
        strategies = []
        risks = []

        # Analyze responses
        aggressive_responders = []
        for comp_id, data in competitor_responses.items():
            if data.get("strategy_type") == "aggressive":
                aggressive_responders.append(data["name"])

        if aggressive_responders:
            risks.append(f"Aggressive competitors ({', '.join(aggressive_responders)}) may escalate")
            strategies.append("Prepare contingency for competitive escalation")

        # Check scenario probabilities
        if scenario_probs.get("price_war_escalation", 0) > 0.3:
            risks.append("Elevated risk of price war")
            strategies.append("Pre-commit to price floor to prevent race to bottom")

        if scenario_probs.get("all_competitors_respond", 0) > 0.5:
            risks.append("High likelihood of coordinated competitive response")
            strategies.append("Consider timing your move to maximize first-mover advantage")

        if scenario_probs.get("no_competitor_responds", 0) > 0.6:
            strategies.append("Favorable conditions - execute confidently")

        # Move-specific recommendations
        move_type = your_move.get("type", "")
        if move_type == "price_change":
            percent = your_move.get("percent", 0)
            if percent > 15:
                risks.append("Large price increase may trigger customer churn before competitors respond")
                strategies.append("Consider phased rollout to test customer sensitivity")
            elif percent < -15:
                risks.append("Large price cut may be difficult to reverse")
                strategies.append("Ensure margin can sustain aggressive pricing")

        return {
            "strategies": strategies or ["Monitor competitor behavior closely"],
            "risks": risks or ["Standard competitive risk - no elevated concerns"]
        }

    def simulate_game(
        self,
        your_moves: List[Dict],
        competitors: List[CompetitorAgent],
        rounds: int = 3
    ) -> List[Dict]:
        """
        Simulate multiple rounds of competitive game.
        """
        history = []
        market_state = MarketState()

        for round_num in range(rounds):
            round_result = {
                "round": round_num + 1,
                "your_move": your_moves[min(round_num, len(your_moves) - 1)],
                "competitor_responses": {},
                "market_state_after": None
            }

            your_move = round_result["your_move"]

            for competitor in competitors:
                # Competitor observes and responds
                competitor.observe_move(your_move, market_state)
                response = competitor.decide_response(your_move, market_state)

                round_result["competitor_responses"][competitor.name] = (
                    response.model_dump() if response else None
                )

                # Update market state based on response
                if response:
                    market_state = self._update_market_state(
                        market_state, response, competitor
                    )

            round_result["market_state_after"] = market_state.model_dump()
            history.append(round_result)

        return history

    def _update_market_state(
        self,
        state: MarketState,
        response: CompetitorMove,
        competitor: CompetitorAgent
    ) -> MarketState:
        """
        Update market state based on a competitive response.
        """
        new_state = MarketState(**state.model_dump())

        if response.move_type == MoveType.PRICE_CHANGE:
            percent = response.parameters.get("price_change_percent", 0)
            if percent < 0:
                # Competitor cuts price - their share increases
                new_state.competitor_shares[competitor.id] = (
                    state.competitor_shares.get(competitor.id, 0.2) * 1.05
                )
                new_state.our_share *= 0.97
            elif percent > 0:
                new_state.our_share *= 1.02

        elif response.move_type == MoveType.MARKETING_CAMPAIGN:
            new_state.competitor_shares[competitor.id] = (
                state.competitor_shares.get(competitor.id, 0.2) * 1.03
            )

        return new_state
