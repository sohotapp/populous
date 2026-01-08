"""
Agent Factory - creates synthetic decision-makers.
Uses optional LLM for rich persona generation.
"""

import random
import numpy as np
from typing import List, Optional, Dict
import json

from backend.models import Agent, Segment, Persona, Belief


class AgentFactory:
    """Creates agents with behavioral parameters sampled from segment profiles"""

    def __init__(self, use_llm: bool = False, llm_sample_size: int = 50):
        """
        Args:
            use_llm: Whether to generate LLM personas
            llm_sample_size: How many agents per segment get LLM personas
        """
        self.use_llm = use_llm
        self.llm_sample_size = llm_sample_size
        self.client = None

        if use_llm:
            try:
                import anthropic
                self.client = anthropic.Anthropic()
            except Exception as e:
                print(f"Warning: Could not initialize Anthropic client: {e}")
                self.use_llm = False

    def create_population(
        self,
        segments: List[Segment],
        total_agents: int
    ) -> List[Agent]:
        """Create full agent population across all segments"""

        agents = []

        for segment in segments:
            segment_count = int(total_agents * segment.size_pct)
            segment_agents = self._create_segment_agents(segment, segment_count)
            agents.extend(segment_agents)

        # Create social network
        agents = self._create_network(agents)

        return agents

    def _create_segment_agents(
        self,
        segment: Segment,
        count: int
    ) -> List[Agent]:
        """Create agents for a specific segment"""

        agents = []
        profile = segment.behavioral_profile

        for i in range(count):
            agent = Agent(
                id=f"{segment.id}_{i}",
                segment_id=segment.id,

                # Sample firmographics
                company_size=random.randint(*profile.company_size_range),
                budget=random.randint(*profile.budget_range),

                # Sample behavioral parameters
                risk_tolerance=self._sample_bounded(*profile.risk_tolerance),
                price_sensitivity=self._sample_bounded(*profile.price_sensitivity),
                decision_speed=self._sample_bounded(*profile.decision_speed),
                influencer_susceptibility=profile.influencer_susceptibility,

                # Sample feature priorities from stakeholders
                feature_priorities=self._sample_priorities(segment),

                # Initialize state
                stage="Unaware",
                awareness={},
                consideration_set=[],
                beliefs={},
                connections=[],
                influence_score=random.random(),
                decision_log=[]
            )

            # Generate LLM persona for sample
            if self.use_llm and i < self.llm_sample_size:
                agent.persona = self._generate_persona(segment, agent)

            agents.append(agent)

        return agents

    def _sample_bounded(self, mean: float, std: float) -> float:
        """Sample from normal distribution, bounded [0, 1]"""
        value = random.gauss(mean, std)
        return max(0.0, min(1.0, value))

    def _sample_priorities(self, segment: Segment) -> Dict[str, float]:
        """Sample feature priorities with noise from segment's stakeholder mix"""

        # Weighted average of stakeholder priorities
        priorities: Dict[str, float] = {}
        total_weight = sum(s.influence_weight for s in segment.decision_framework.stakeholders)

        for stakeholder in segment.decision_framework.stakeholders:
            weight = stakeholder.influence_weight / total_weight
            for feature, importance in stakeholder.priorities.items():
                if feature not in priorities:
                    priorities[feature] = 0
                priorities[feature] += importance * weight

        # Add noise
        return {
            k: max(0, min(1, v + random.gauss(0, 0.1)))
            for k, v in priorities.items()
        }

    def _create_network(self, agents: List[Agent]) -> List[Agent]:
        """Create social network using preferential attachment"""

        # Group by segment
        by_segment: Dict[str, List[Agent]] = {}
        for agent in agents:
            if agent.segment_id not in by_segment:
                by_segment[agent.segment_id] = []
            by_segment[agent.segment_id].append(agent)

        # Connect within segments (preferential attachment)
        for segment_id, segment_agents in by_segment.items():
            n = len(segment_agents)
            if n < 5:
                continue

            for i, agent in enumerate(segment_agents):
                if i < 3:
                    continue

                # Number of connections based on network density
                num_connections = min(random.randint(2, 5), i)

                # Weight by influence score (preferential attachment)
                candidates = segment_agents[:i]
                weights = np.array([a.influence_score for a in candidates])
                weights = weights / weights.sum()

                # Sample connections
                indices = np.random.choice(
                    len(candidates),
                    size=num_connections,
                    replace=False,
                    p=weights
                )

                agent.connections = [candidates[j].id for j in indices]

        return agents

    def _generate_persona(self, segment: Segment, agent: Agent) -> Optional[Persona]:
        """Use Claude to generate a rich persona"""

        if not self.client:
            return None

        prompt = f"""Generate a realistic B2B buyer persona.

SEGMENT: {segment.name}
DECISION FRAMEWORK:
- Average sales cycle: {segment.decision_framework.avg_cycle_days} days
- Key stakeholders: {[s.role for s in segment.decision_framework.stakeholders]}
- Common blockers: {segment.decision_framework.blockers}

AGENT BEHAVIORAL PROFILE:
- Company size: {agent.company_size} employees
- Budget: ${agent.budget:,}
- Risk tolerance: {agent.risk_tolerance:.2f} (0=very cautious, 1=risk-seeking)
- Price sensitivity: {agent.price_sensitivity:.2f} (0=budget doesn't matter, 1=very cost-conscious)
- Decision speed: {agent.decision_speed:.2f} (0=very deliberate, 1=quick decision maker)
- Feature priorities: {agent.feature_priorities}

Generate a persona with:
1. A realistic name
2. Job title that matches the segment
3. Company name and brief description
4. 2-sentence professional background
5. Top 3 current business challenges
6. 2-3 past software purchasing experiences
7. Their communication/buying style preference

Return ONLY valid JSON:
{{
    "name": "string",
    "role": "string",
    "company_name": "string",
    "company_description": "string",
    "background": "string",
    "current_challenges": ["string", "string", "string"],
    "buying_history": ["string", "string"],
    "communication_style": "string"
}}"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse JSON from response
            text = response.content[0].text
            # Handle potential markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            data = json.loads(text.strip())
            return Persona(**data)

        except Exception as e:
            # Fallback persona
            return Persona(
                name=f"Contact {agent.id}",
                role="Decision Maker",
                company_name=f"Company {agent.company_size}",
                company_description=f"A {agent.company_size}-person company",
                background="Experienced professional in the industry.",
                current_challenges=["Efficiency", "Growth", "Competition"],
                buying_history=["Previous software purchase"],
                communication_style="Professional and direct"
            )
