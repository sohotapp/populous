"""
Social Network Effects Engine
Word-of-mouth, influence propagation, cascades
"""

import numpy as np
from typing import List, Dict

from backend.models.generative_agent import GenerativeAgent, AgentState, Relationship, Memory


class NetworkEngine:
    """Engine for social network effects"""

    def build_network(self, agents: List[GenerativeAgent], connectivity: float = 0.05):
        """Build social network connections between agents"""
        n = len(agents)

        for i, agent in enumerate(agents):
            # Each agent connects to ~5% of others (configurable)
            num_connections = int(n * connectivity)
            connection_indices = np.random.choice(
                [j for j in range(n) if j != i],
                size=min(num_connections, n - 1),
                replace=False
            )

            for j in connection_indices:
                other = agents[j]
                # Stronger connections within same segment
                same_segment = agent.segment_id == other.segment_id
                trust = np.random.uniform(0.5, 0.9) if same_segment else np.random.uniform(0.2, 0.5)

                agent.relationships.append(Relationship(
                    other_agent_id=other.id,
                    relationship_type="colleague" if same_segment else "acquaintance",
                    trust_level=trust,
                    influence_weight=trust * agent.social_influence
                ))

    def propagate_influence(self, agents: List[GenerativeAgent], day: int):
        """Propagate social influence through network"""
        agent_map = {a.id: a for a in agents}

        for agent in agents:
            if not agent.relationships:
                continue

            # Check if any connections have churned/retained
            for rel in agent.relationships:
                other = agent_map.get(rel.other_agent_id)
                if not other:
                    continue

                # Word of mouth from churned connections
                if other.state == AgentState.CHURNED:
                    if np.random.random() < rel.influence_weight * 0.3:
                        # Influence towards churning
                        agent.awareness += 0.1
                        if agent.state == AgentState.CONSIDERING:
                            mem = Memory(
                                id=f"mem_{len(agent.memory_stream)}",
                                timestamp=day,
                                description=f"Heard that {other.name} left for competitor",
                                importance=7.0,
                                type="social"
                            )
                            agent.memory_stream.append(mem)

                # Word of mouth from retained connections
                elif other.state == AgentState.RETAINED:
                    if np.random.random() < rel.influence_weight * 0.2:
                        # Influence towards retention
                        agent.brand_loyalty += 0.05

    def identify_influencers(self, agents: List[GenerativeAgent]) -> List[GenerativeAgent]:
        """Identify high-influence agents in the network"""
        influence_scores = []

        for agent in agents:
            total_influence = sum(r.influence_weight for r in agent.relationships)
            influence_scores.append((agent, total_influence))

        influence_scores.sort(key=lambda x: x[1], reverse=True)

        # Return top 10%
        top_n = max(1, len(agents) // 10)
        return [agent for agent, _ in influence_scores[:top_n]]

    def simulate_cascade(
        self,
        agents: List[GenerativeAgent],
        trigger_agent_ids: List[str],
        cascade_type: str  # "churn" or "adoption"
    ) -> Dict:
        """Simulate a cascade effect from trigger agents"""
        agent_map = {a.id: a for a in agents}
        affected = set(trigger_agent_ids)
        wave = 0
        cascade_log = []

        current_wave = set(trigger_agent_ids)

        while current_wave:
            next_wave = set()
            wave += 1

            for agent_id in current_wave:
                agent = agent_map.get(agent_id)
                if not agent:
                    continue

                for rel in agent.relationships:
                    if rel.other_agent_id in affected:
                        continue

                    other = agent_map.get(rel.other_agent_id)
                    if not other:
                        continue

                    # Probability of cascade
                    cascade_prob = rel.influence_weight * other.social_influence

                    if np.random.random() < cascade_prob:
                        next_wave.add(rel.other_agent_id)
                        affected.add(rel.other_agent_id)

            cascade_log.append({
                "wave": wave,
                "new_affected": len(next_wave),
                "total_affected": len(affected)
            })

            current_wave = next_wave

            # Safety limit
            if wave > 10:
                break

        return {
            "total_affected": len(affected),
            "waves": wave,
            "cascade_log": cascade_log,
            "multiplier": len(affected) / max(len(trigger_agent_ids), 1)
        }
