"""
Stanford Generative Agent Implementation
Memory Stream + Reflection + Planning
"""

from anthropic import Anthropic
from typing import List, Dict, Optional
import json

from backend.models.generative_agent import (
    GenerativeAgent, Memory, Reflection, AgentBelief, AgentDecisionEvent
)


class AgentEngine:
    """Engine for managing Stanford-architecture agents"""

    def __init__(self, llm_client: Anthropic):
        self.llm = llm_client

    # ==================== MEMORY ====================

    def perceive(self, agent: GenerativeAgent, observation: str, sim_time: float) -> GenerativeAgent:
        """Add an observation to the agent's memory stream"""
        # Rate importance
        importance = self._rate_importance(agent, observation)

        # Create memory
        memory = Memory(
            id=f"mem_{len(agent.memory_stream)}",
            timestamp=sim_time,
            description=observation,
            importance=importance,
            type="observation"
        )

        # Add to stream
        agent.memory_stream.append(memory)
        agent.accumulated_importance += importance

        # Check if reflection needed
        if agent.accumulated_importance >= agent.reflection_threshold:
            agent = self._reflect(agent, sim_time)
            agent.accumulated_importance = 0

        return agent

    def _rate_importance(self, agent: GenerativeAgent, observation: str) -> float:
        """LLM rates importance 1-10"""
        prompt = f"""Rate the importance of this observation for {agent.name},
a {agent.occupation} who is {agent.decision_style} in their decision-making.

Their values: {', '.join(agent.values)}
Their pain points: {', '.join(agent.pain_points)}

Observation: {observation}

Rate 1-10 where:
1 = Completely mundane, routine
5 = Moderately important, worth noting
10 = Critical, requires immediate attention

Return only the number."""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            return float(response.content[0].text.strip())
        except:
            return 5.0  # Default to moderate importance

    # ==================== REFLECTION ====================

    def _reflect(self, agent: GenerativeAgent, sim_time: float) -> GenerativeAgent:
        """Generate higher-level insights from recent memories"""
        recent_memories = agent.memory_stream[-50:]

        prompt = f"""You are {agent.name}, a {agent.age}-year-old {agent.occupation}.

Your personality: {json.dumps(agent.personality)}
Your values: {', '.join(agent.values)}

Recent experiences:
{chr(10).join([f"- {m.description} (importance: {m.importance})" for m in recent_memories])}

Based on these experiences, what are the 3 most important high-level insights
or realizations you would have? These should be synthesized conclusions, not
just repetitions of what happened.

Format: One insight per line, starting with "I realize..." or "I've noticed..." """

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        insights = response.content[0].text.strip().split('\n')

        for insight in insights:
            if insight.strip():
                reflection = Reflection(
                    id=f"ref_{len(agent.reflections)}",
                    timestamp=sim_time,
                    content=insight.strip(),
                    source_memory_ids=[m.id for m in recent_memories[-20:]],
                    importance=8.0  # Reflections are inherently important
                )
                agent.reflections.append(reflection)

                # Reflections become memories too (recursive)
                reflection_memory = Memory(
                    id=f"mem_{len(agent.memory_stream)}",
                    timestamp=sim_time,
                    description=f"[Reflection] {insight.strip()}",
                    importance=8.0,
                    type="reflection"
                )
                agent.memory_stream.append(reflection_memory)

        return agent

    # ==================== MEMORY RETRIEVAL ====================

    def retrieve_relevant_memories(
        self,
        agent: GenerativeAgent,
        query: str,
        sim_time: float,
        k: int = 20
    ) -> List[Memory]:
        """Retrieve memories by recency + importance + relevance"""
        scored_memories = []

        for mem in agent.memory_stream:
            # Recency score (exponential decay)
            time_diff = sim_time - mem.timestamp
            recency_score = 0.99 ** time_diff

            # Importance score (normalized)
            importance_score = mem.importance / 10.0

            # Relevance score (simple keyword matching for now)
            # In production: use embeddings
            query_words = set(query.lower().split())
            mem_words = set(mem.description.lower().split())
            overlap = len(query_words & mem_words)
            relevance_score = min(overlap / max(len(query_words), 1), 1.0)

            # Combined score
            total_score = (
                0.3 * recency_score +
                0.3 * importance_score +
                0.4 * relevance_score
            )

            scored_memories.append((total_score, mem))

        # Sort and return top k
        scored_memories.sort(reverse=True, key=lambda x: x[0])
        return [mem for _, mem in scored_memories[:k]]

    # ==================== PLANNING ====================

    def plan(self, agent: GenerativeAgent, goal: str, sim_time: float) -> List[str]:
        """Generate action plan for a goal"""
        relevant_memories = self.retrieve_relevant_memories(agent, goal, sim_time)
        recent_reflections = agent.reflections[-10:]

        prompt = f"""You are {agent.name}, a {agent.age}-year-old {agent.occupation}.

Your goal: {goal}

What you optimize for (utility function weights):
{json.dumps(agent.utility_weights)}

Your constraints and considerations:
- Price sensitivity: {agent.price_sensitivity} (0=insensitive, 1=very sensitive)
- Brand loyalty: {agent.brand_loyalty} (0=none, 1=very loyal)
- Risk tolerance: {agent.risk_tolerance} (0=risk-averse, 1=risk-seeking)

Relevant memories:
{chr(10).join([f"- {m.description}" for m in relevant_memories])}

Recent reflections:
{chr(10).join([f"- {r.content}" for r in recent_reflections])}

Generate a step-by-step action plan. Be specific and realistic for someone
with your profile. Format as numbered steps."""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        plan = response.content[0].text.strip().split('\n')
        agent.current_plan = [step.strip() for step in plan if step.strip()]

        return agent.current_plan

    # ==================== DECISION ====================

    def decide(
        self,
        agent: GenerativeAgent,
        options: List[Dict],
        context: str,
        sim_time: float
    ) -> AgentDecisionEvent:
        """Make a decision given options"""
        relevant_memories = self.retrieve_relevant_memories(agent, context, sim_time)

        prompt = f"""You are {agent.name}, a {agent.age}-year-old {agent.occupation}.

You need to make a decision.

Context: {context}

Options:
{json.dumps(options, indent=2)}

Your utility function (what you optimize for):
{json.dumps(agent.utility_weights)}

Your current beliefs:
{json.dumps({k: {"probability": v.probability, "confidence": v.confidence}
             for k, v in agent.beliefs.items()})}

Your decision style: {agent.decision_style}

Relevant past experiences:
{chr(10).join([f"- {m.description}" for m in relevant_memories])}

Make your decision. Explain your reasoning, then state your choice.

Format:
REASONING: [Your thought process]
CHOICE: [Option ID]
CONFIDENCE: [0.0 to 1.0]
KEY_FACTORS: [factor1: weight, factor2: weight, ...]"""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        result = self._parse_decision_response(response.content[0].text, options)

        decision_event = AgentDecisionEvent(
            timestamp=sim_time,
            decision_type=context,
            choice=result["choice"],
            reasoning=result["reasoning"],
            confidence=result["confidence"],
            factors=result["factors"]
        )

        agent.decision_events.append(decision_event)

        return decision_event

    def _parse_decision_response(self, text: str, options: List[Dict]) -> Dict:
        """Parse LLM decision response"""
        lines = text.strip().split('\n')
        result = {
            "reasoning": "",
            "choice": options[0]["id"] if options else "",
            "confidence": 0.5,
            "factors": {}
        }

        for line in lines:
            if line.startswith("REASONING:"):
                result["reasoning"] = line.replace("REASONING:", "").strip()
            elif line.startswith("CHOICE:"):
                result["choice"] = line.replace("CHOICE:", "").strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    result["confidence"] = float(line.replace("CONFIDENCE:", "").strip())
                except:
                    pass
            elif line.startswith("KEY_FACTORS:"):
                factors_str = line.replace("KEY_FACTORS:", "").strip()
                for factor in factors_str.split(","):
                    if ":" in factor:
                        k, v = factor.split(":")
                        try:
                            result["factors"][k.strip()] = float(v.strip())
                        except:
                            pass

        return result

    # ==================== BELIEF UPDATE ====================

    def update_beliefs(self, agent: GenerativeAgent, evidence: Dict, sim_time: float) -> GenerativeAgent:
        """Bayesian update on beliefs given evidence"""
        for subject, new_info in evidence.items():
            if subject in agent.beliefs:
                belief = agent.beliefs[subject]
                prior = belief.probability
                likelihood = new_info.get("likelihood", 0.5)

                # Update probability
                posterior = (prior * likelihood) / (
                    prior * likelihood + (1 - prior) * (1 - likelihood)
                )

                belief.probability = posterior
                belief.confidence = min(belief.confidence + 0.1, 1.0)
                belief.last_updated = sim_time
            else:
                agent.beliefs[subject] = AgentBelief(
                    subject=subject,
                    probability=new_info.get("probability", 0.5),
                    confidence=new_info.get("confidence", 0.3),
                    last_updated=sim_time
                )

        return agent
