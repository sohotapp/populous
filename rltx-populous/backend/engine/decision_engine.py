"""
Decision Engine - how agents make purchase decisions.
Hybrid approach: fast math for simulation, LLM for explanations.
"""

import random
from typing import List, Dict, Optional, Union

from backend.models import Agent, Product, Competitor, Strategy, DecisionEvent


class DecisionEngine:
    """
    Processes agent decisions each simulation step.

    The decision model:
    1. Awareness updates from market signals
    2. Stage progression based on awareness thresholds
    3. Product scoring based on fit
    4. Final decision with threshold
    """

    def __init__(
        self,
        awareness_threshold: float = 0.25,
        consideration_threshold: float = 0.50,
        evaluation_threshold: float = 0.70,
        purchase_threshold: float = 0.55
    ):
        self.awareness_threshold = awareness_threshold
        self.consideration_threshold = consideration_threshold
        self.evaluation_threshold = evaluation_threshold
        self.purchase_threshold = purchase_threshold
        self.client = None

    def _get_client(self):
        """Lazy load the Anthropic client"""
        if self.client is None:
            try:
                import anthropic
                self.client = anthropic.Anthropic()
            except Exception:
                pass
        return self.client

    def process_agent_day(
        self,
        agent: Agent,
        day: int,
        your_product: Product,
        competitors: List[Competitor],
        market_signals: Dict[str, float],
        strategy: Strategy
    ) -> Agent:
        """Process one day for one agent"""

        if agent.stage == "Decided":
            return agent

        # 1. Update awareness from signals
        agent = self._update_awareness(agent, market_signals, day)

        # 2. Progress through stages
        agent = self._update_stage(agent, your_product, competitors, day)

        # 3. If evaluating, maybe make decision
        if agent.stage == "Evaluating":
            agent = self._maybe_decide(
                agent, day, your_product, competitors, strategy
            )

        return agent

    def _update_awareness(
        self,
        agent: Agent,
        signals: Dict[str, float],
        day: int
    ) -> Agent:
        """Update product awareness based on market signals"""

        for product_id, signal_strength in signals.items():
            current = agent.awareness.get(product_id, 0.0)

            # Base impact from signal
            base_impact = signal_strength * 0.12

            # Modify by agent's susceptibility
            susceptibility_mod = 0.6 + agent.influencer_susceptibility * 0.4
            impact = base_impact * susceptibility_mod

            # Diminishing returns at high awareness
            impact *= (1 - current) ** 0.7

            new_awareness = min(1.0, current + impact)

            # Log significant changes
            if new_awareness - current > 0.05:
                agent.add_event(
                    day=day,
                    event_type="awareness",
                    description=f"Awareness of {product_id} increased",
                    inputs={"signal": signal_strength, "previous": round(current, 3)},
                    output=f"{new_awareness:.3f}"
                )

            agent.awareness[product_id] = new_awareness

        return agent

    def _update_stage(
        self,
        agent: Agent,
        your_product: Product,
        competitors: List[Competitor],
        day: int
    ) -> Agent:
        """Progress agent through funnel stages"""

        max_awareness = max(agent.awareness.values()) if agent.awareness else 0
        old_stage = agent.stage

        if agent.stage == "Unaware":
            if max_awareness >= self.awareness_threshold:
                agent.stage = "Aware"

        elif agent.stage == "Aware":
            if max_awareness >= self.consideration_threshold:
                agent.stage = "Considering"

        elif agent.stage == "Considering":
            if max_awareness >= self.evaluation_threshold:
                agent.stage = "Evaluating"

        # Build/update consideration set for agents who are Considering or Evaluating
        # Products can be added to consideration as awareness grows
        if agent.stage in ["Considering", "Evaluating"]:
            all_products = [your_product.id] + [c.id for c in competitors]
            for pid in all_products:
                awareness = agent.awareness.get(pid, 0)
                if awareness >= self.awareness_threshold:
                    if pid not in agent.consideration_set:
                        agent.consideration_set.append(pid)

        # Log stage changes
        if agent.stage != old_stage:
            agent.add_event(
                day=day,
                event_type="stage_change",
                description=f"Progressed from {old_stage} to {agent.stage}",
                inputs={"max_awareness": round(max_awareness, 3)},
                output=agent.stage
            )

        return agent

    def _maybe_decide(
        self,
        agent: Agent,
        day: int,
        your_product: Product,
        competitors: List[Competitor],
        strategy: Strategy
    ) -> Agent:
        """Evaluate products and potentially make a decision"""

        # Decision probability based on speed + time in stage
        base_prob = agent.decision_speed * 0.06
        time_pressure = min(0.04, day * 0.0005)  # Increases over time
        decision_prob = base_prob + time_pressure

        if random.random() > decision_prob:
            return agent

        # Score each product in consideration set
        all_products: Dict[str, Union[Product, Competitor]] = {your_product.id: your_product}
        for c in competitors:
            all_products[c.id] = c

        scores = {}
        for pid in agent.consideration_set:
            if pid in all_products:
                product = all_products[pid]
                scores[pid] = self._score_product(agent, product, strategy)

        if not scores:
            agent.stage = "Decided"
            agent.final_decision = None
            agent.decision_day = day
            agent.add_event(
                day=day,
                event_type="decision",
                description="No products in consideration - no purchase",
                inputs={},
                output="no_purchase"
            )
            return agent

        # Find best option
        best_id = max(scores, key=scores.get)
        best_score = scores[best_id]

        # Apply purchase threshold
        if best_score >= self.purchase_threshold:
            agent.final_decision = best_id
            agent.add_event(
                day=day,
                event_type="decision",
                description=f"Selected {best_id}",
                inputs={"scores": {k: round(v, 3) for k, v in scores.items()}},
                output=best_id
            )
        else:
            agent.final_decision = None
            agent.add_event(
                day=day,
                event_type="decision",
                description="No product met requirements",
                inputs={"scores": {k: round(v, 3) for k, v in scores.items()}},
                output="no_purchase"
            )

        agent.stage = "Decided"
        agent.decision_day = day

        return agent

    def _score_product(
        self,
        agent: Agent,
        product: Union[Product, Competitor],
        strategy: Strategy
    ) -> float:
        """
        Calculate fit score between agent and product.

        Score components:
        - Feature fit (40%): How well features match priorities
        - Price fit (30%): Price vs. price sensitivity
        - Brand fit (20%): Brand awareness vs. risk tolerance
        - Awareness (10%): Familiarity bonus
        """

        score = 0.0

        # Feature fit (40%)
        feature_score = 0.0
        total_weight = sum(agent.feature_priorities.values()) or 1

        for feature, importance in agent.feature_priorities.items():
            product_strength = product.features.get(feature, 0.5)
            feature_score += importance * product_strength

        feature_score /= total_weight
        score += feature_score * 0.40

        # Price fit (30%)
        # Price sensitivity affects how much price matters
        # Lower price = better fit for price-sensitive buyers
        price_penalty = agent.price_sensitivity * (product.price_point - 0.7)
        price_fit = 1.0 - max(0, min(0.5, price_penalty))
        score += price_fit * 0.30

        # Brand/risk fit (20%)
        # Risk-averse buyers prefer high brand awareness
        # Risk-tolerant buyers are ok with unknowns
        brand_fit = (
            product.brand_awareness * (1 - agent.risk_tolerance) +
            agent.risk_tolerance * 0.6  # Risk tolerant = ok with unknown
        )
        score += brand_fit * 0.20

        # Awareness bonus (10%)
        awareness = agent.awareness.get(product.id, 0)
        score += awareness * 0.10

        return score

    def explain_decision(self, agent: Agent) -> str:
        """Generate natural language explanation of agent's decision"""

        client = self._get_client()
        if not client:
            return "LLM explanation not available."

        # Build context from decision log
        journey = "\n".join([
            f"Day {e.day}: {e.description} (inputs: {e.inputs}, output: {e.output})"
            for e in agent.decision_log[-10:]  # Last 10 events
        ])

        persona_context = ""
        if agent.persona:
            persona_context = f"""
PERSONA:
- Name: {agent.persona.name}
- Role: {agent.persona.role}
- Company: {agent.persona.company_description}
- Challenges: {', '.join(agent.persona.current_challenges)}
- Buying style: {agent.persona.communication_style}
"""

        prompt = f"""Explain this B2B buyer's decision journey in 3-4 sentences.

{persona_context}
BEHAVIORAL PROFILE:
- Risk tolerance: {agent.risk_tolerance:.2f} (0=very cautious, 1=risk-seeking)
- Price sensitivity: {agent.price_sensitivity:.2f} (0=budget flexible, 1=cost-conscious)
- Decision speed: {agent.decision_speed:.2f} (0=deliberate, 1=fast)
- Feature priorities: {agent.feature_priorities}

DECISION JOURNEY:
{journey}

FINAL DECISION: {agent.final_decision or 'No purchase'}

Write a clear explanation of WHY they made this decision, referencing their
specific characteristics. Be specific, not generic. Explain the key factors."""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text
