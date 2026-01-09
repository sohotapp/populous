"""
Chat Engine
Enables natural conversation with synthetic agents
"""

from typing import List, Dict, Optional
from anthropic import Anthropic
import json

from backend.models.generative_agent import GenerativeAgent, Memory


class ChatEngine:
    """Engine for conversing with synthetic agents"""

    def __init__(self, llm_client: Anthropic):
        self.llm = llm_client

    def chat(
        self,
        agent: GenerativeAgent,
        user_message: str,
        conversation_history: List[Dict] = None
    ) -> str:
        """Generate agent response to user message"""

        if conversation_history is None:
            conversation_history = []

        # Retrieve relevant memories
        relevant_memories = self._get_relevant_memories(agent, user_message)

        # Build agent context
        agent_context = self._build_agent_context(agent)

        # Build conversation
        system_prompt = f"""You are {agent.name}, a {agent.age}-year-old {agent.occupation}.

{agent_context}

IMPORTANT GUIDELINES:
- Stay completely in character as {agent.name}
- Reference your specific experiences and memories when relevant
- Be authentic to your personality and values
- Give specific, personal answers - not generic ones
- If asked about decisions you made, explain your actual reasoning
- Show your personality: {self._describe_personality(agent.personality)}

Your relevant experiences and memories:
{chr(10).join([f"- {m.description}" for m in relevant_memories[-15:]])}

Remember: You ARE this person. Speak as yourself, not about yourself."""

        messages = []

        # Add conversation history
        for msg in conversation_history[-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current message
        messages.append({
            "role": "user",
            "content": user_message
        })

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=system_prompt,
            messages=messages
        )

        return response.content[0].text

    def _build_agent_context(self, agent: GenerativeAgent) -> str:
        """Build context description for agent"""

        context_parts = []

        # Basic info
        context_parts.append(f"You live in {agent.location} and work as a {agent.occupation}.")
        context_parts.append(f"Your annual income is ${agent.income:,.0f}.")

        # Values and priorities
        if agent.values:
            context_parts.append(f"You deeply value: {', '.join(agent.values)}.")

        # Pain points
        if agent.pain_points:
            context_parts.append(f"Your main frustrations are: {', '.join(agent.pain_points)}.")

        # Decision style
        context_parts.append(f"When making decisions, you tend to be {agent.decision_style}.")

        # Behavioral traits
        if agent.price_sensitivity > 0.7:
            context_parts.append("You're very careful about money and compare prices diligently.")
        elif agent.price_sensitivity < 0.3:
            context_parts.append("Price isn't your main concern - you prioritize quality and convenience.")

        if agent.brand_loyalty > 0.7:
            context_parts.append("You tend to stick with brands you trust, even if alternatives exist.")
        elif agent.brand_loyalty < 0.3:
            context_parts.append("You're always open to trying new options if they're better.")

        if agent.risk_tolerance > 0.7:
            context_parts.append("You're comfortable taking risks and trying new things.")
        elif agent.risk_tolerance < 0.3:
            context_parts.append("You prefer safe, proven choices and avoid unnecessary risk.")

        # Recent state
        state_descriptions = {
            "churned": "You recently decided to leave/cancel your subscription.",
            "retained": "You decided to stay despite the changes.",
            "evaluating": "You're currently weighing your options.",
            "considering": "You're starting to think about alternatives."
        }
        if agent.state in state_descriptions:
            context_parts.append(state_descriptions[agent.state])

        return " ".join(context_parts)

    def _describe_personality(self, personality: Dict) -> str:
        """Describe personality traits in natural language"""

        descriptions = []

        if personality.get("openness", 0.5) > 0.7:
            descriptions.append("curious and open to new experiences")
        elif personality.get("openness", 0.5) < 0.3:
            descriptions.append("practical and prefer familiar things")

        if personality.get("conscientiousness", 0.5) > 0.7:
            descriptions.append("organized and thorough")
        elif personality.get("conscientiousness", 0.5) < 0.3:
            descriptions.append("flexible and spontaneous")

        if personality.get("extraversion", 0.5) > 0.7:
            descriptions.append("outgoing and energetic")
        elif personality.get("extraversion", 0.5) < 0.3:
            descriptions.append("reserved and thoughtful")

        if personality.get("agreeableness", 0.5) > 0.7:
            descriptions.append("cooperative and trusting")
        elif personality.get("agreeableness", 0.5) < 0.3:
            descriptions.append("straightforward and skeptical")

        return ", ".join(descriptions) if descriptions else "balanced"

    def _get_relevant_memories(
        self,
        agent: GenerativeAgent,
        query: str,
        k: int = 15
    ) -> List[Memory]:
        """Get memories relevant to the query"""

        if not agent.memory_stream:
            return []

        # Simple relevance scoring
        query_words = set(query.lower().split())

        scored = []
        for mem in agent.memory_stream:
            mem_words = set(mem.description.lower().split())
            overlap = len(query_words & mem_words)
            score = overlap + (mem.importance / 10)
            scored.append((score, mem))

        scored.sort(reverse=True, key=lambda x: x[0])

        return [mem for _, mem in scored[:k]]

    def get_decision_journey(self, agent: GenerativeAgent) -> List[Dict]:
        """Get the agent's decision journey for display"""

        journey = []

        for event in agent.decision_events:
            journey.append({
                "timestamp": event.timestamp,
                "type": event.decision_type,
                "choice": event.choice,
                "reasoning": event.reasoning,
                "confidence": event.confidence
            })

        # Add key memories
        key_memories = [m for m in agent.memory_stream if m.importance >= 7]
        for mem in key_memories[-10:]:
            journey.append({
                "timestamp": mem.timestamp,
                "type": "memory",
                "description": mem.description,
                "importance": mem.importance
            })

        # Sort by timestamp
        journey.sort(key=lambda x: x["timestamp"])

        return journey
