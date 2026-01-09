"""
Supabase Database Layer
Handles all database operations for Populous
"""

import os
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

from backend.models.company import Company, Market, ResearchResult
from backend.models.decision import Decision
from backend.models.simulation import TemporalSimulation
from backend.models.generative_agent import GenerativeAgent


# Singleton database instance
_database_instance = None


def get_database() -> 'Database':
    """Get or create database singleton."""
    global _database_instance
    if _database_instance is None:
        _database_instance = Database()
    return _database_instance


class Database:
    """
    Supabase database operations for Populous.
    Falls back to in-memory storage if Supabase is not configured.
    """

    def __init__(self):
        self.client: Optional[Client] = None
        self.use_memory = True

        # In-memory fallback storage
        self._memory_store = {
            "companies": {},
            "decisions": {},
            "simulations": {},
            "agents": {},
            "branches": {},
            "journal_entries": {},
            "recommendations": {},
            "research_results": {}
        }

        # Try to initialize Supabase
        if SUPABASE_AVAILABLE:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            if url and key:
                try:
                    self.client = create_client(url, key)
                    self.use_memory = False
                    print("Supabase connected successfully")
                except Exception as e:
                    print(f"Supabase connection failed: {e}")
                    self.use_memory = True

        if self.use_memory:
            print("Using in-memory storage (Supabase not configured)")

    # ==================== COMPANIES ====================

    async def save_company(self, company: Company) -> str:
        """Save a company to the database."""
        company_id = company.id or str(uuid.uuid4())

        data = {
            "id": company_id,
            "name": company.name,
            "data": company.model_dump(),
            "research_sources": company.research_sources,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        if self.use_memory:
            self._memory_store["companies"][company_id] = data
        else:
            self.client.table("companies").upsert(data).execute()

        return company_id

    async def get_company(self, company_id: str) -> Optional[Company]:
        """Get a company by ID."""
        if self.use_memory:
            data = self._memory_store["companies"].get(company_id)
            if data:
                return Company(**data["data"])
            return None
        else:
            result = self.client.table("companies").select("*").eq("id", company_id).execute()
            if result.data:
                return Company(**result.data[0]["data"])
            return None

    async def list_companies(self, limit: int = 50) -> List[Company]:
        """List all companies."""
        if self.use_memory:
            companies = list(self._memory_store["companies"].values())[:limit]
            return [Company(**c["data"]) for c in companies]
        else:
            result = self.client.table("companies").select("*").limit(limit).execute()
            return [Company(**r["data"]) for r in result.data]

    async def search_companies(self, query: str) -> List[Company]:
        """Search companies by name."""
        if self.use_memory:
            matches = []
            for data in self._memory_store["companies"].values():
                if query.lower() in data["name"].lower():
                    matches.append(Company(**data["data"]))
            return matches
        else:
            result = self.client.table("companies").select("*").ilike("name", f"%{query}%").execute()
            return [Company(**r["data"]) for r in result.data]

    # ==================== RESEARCH RESULTS ====================

    async def save_research_result(self, result: ResearchResult) -> str:
        """Save a research result."""
        result_id = result.id or str(uuid.uuid4())

        data = {
            "id": result_id,
            "query": result.query,
            "data": result.model_dump(),
            "created_at": datetime.now().isoformat()
        }

        if self.use_memory:
            self._memory_store["research_results"][result_id] = data
        else:
            self.client.table("research_results").upsert(data).execute()

        # Also save the target company and competitors
        await self.save_company(result.target_company)
        for competitor in result.competitors:
            await self.save_company(competitor)

        return result_id

    async def get_research_result(self, result_id: str) -> Optional[ResearchResult]:
        """Get a research result by ID."""
        if self.use_memory:
            data = self._memory_store["research_results"].get(result_id)
            if data:
                return ResearchResult(**data["data"])
            return None
        else:
            result = self.client.table("research_results").select("*").eq("id", result_id).execute()
            if result.data:
                return ResearchResult(**result.data[0]["data"])
            return None

    # ==================== DECISIONS ====================

    async def save_decision(self, decision: Decision) -> str:
        """Save a decision."""
        decision_id = decision.id or str(uuid.uuid4())

        data = {
            "id": decision_id,
            "title": decision.title,
            "status": decision.status.value if hasattr(decision.status, 'value') else decision.status,
            "data": decision.model_dump(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        if self.use_memory:
            self._memory_store["decisions"][decision_id] = data
        else:
            self.client.table("decisions").upsert(data).execute()

        return decision_id

    async def get_decision(self, decision_id: str) -> Optional[Decision]:
        """Get a decision by ID."""
        if self.use_memory:
            data = self._memory_store["decisions"].get(decision_id)
            if data:
                return Decision(**data["data"])
            return None
        else:
            result = self.client.table("decisions").select("*").eq("id", decision_id).execute()
            if result.data:
                return Decision(**result.data[0]["data"])
            return None

    async def list_decisions(self, limit: int = 50) -> List[Decision]:
        """List all decisions."""
        if self.use_memory:
            decisions = list(self._memory_store["decisions"].values())[:limit]
            return [Decision(**d["data"]) for d in decisions]
        else:
            result = self.client.table("decisions").select("*").order("created_at", desc=True).limit(limit).execute()
            return [Decision(**r["data"]) for r in result.data]

    async def update_decision_status(self, decision_id: str, status: str) -> bool:
        """Update decision status."""
        if self.use_memory:
            if decision_id in self._memory_store["decisions"]:
                self._memory_store["decisions"][decision_id]["status"] = status
                self._memory_store["decisions"][decision_id]["data"]["status"] = status
                self._memory_store["decisions"][decision_id]["updated_at"] = datetime.now().isoformat()
                return True
            return False
        else:
            self.client.table("decisions").update({
                "status": status,
                "updated_at": datetime.now().isoformat()
            }).eq("id", decision_id).execute()
            return True

    # ==================== SIMULATIONS ====================

    async def save_simulation(self, simulation: TemporalSimulation) -> str:
        """Save a simulation."""
        sim_id = simulation.id or str(uuid.uuid4())

        data = {
            "id": sim_id,
            "decision_id": simulation.decision_id,
            "status": simulation.status.value if hasattr(simulation.status, 'value') else simulation.status,
            "progress": simulation.progress,
            "data": simulation.model_dump(),
            "created_at": datetime.now().isoformat()
        }

        if self.use_memory:
            self._memory_store["simulations"][sim_id] = data
        else:
            self.client.table("simulations").upsert(data).execute()

        return sim_id

    async def get_simulation(self, sim_id: str) -> Optional[TemporalSimulation]:
        """Get a simulation by ID."""
        if self.use_memory:
            data = self._memory_store["simulations"].get(sim_id)
            if data:
                return TemporalSimulation(**data["data"])
            return None
        else:
            result = self.client.table("simulations").select("*").eq("id", sim_id).execute()
            if result.data:
                return TemporalSimulation(**result.data[0]["data"])
            return None

    async def update_simulation_progress(
        self,
        sim_id: str,
        progress: float,
        status: Optional[str] = None
    ) -> bool:
        """Update simulation progress."""
        update_data = {
            "progress": progress,
            "updated_at": datetime.now().isoformat()
        }
        if status:
            update_data["status"] = status

        if self.use_memory:
            if sim_id in self._memory_store["simulations"]:
                self._memory_store["simulations"][sim_id].update(update_data)
                return True
            return False
        else:
            self.client.table("simulations").update(update_data).eq("id", sim_id).execute()
            return True

    # ==================== AGENTS ====================

    async def save_agents(self, simulation_id: str, agents: List[GenerativeAgent]) -> int:
        """Save agents for a simulation."""
        count = 0
        for agent in agents:
            data = {
                "id": agent.id,
                "simulation_id": simulation_id,
                "data": agent.model_dump(),
                "final_state": agent.state.value if hasattr(agent.state, 'value') else agent.state,
                "created_at": datetime.now().isoformat()
            }

            if self.use_memory:
                self._memory_store["agents"][agent.id] = data
            else:
                self.client.table("agents").upsert(data).execute()

            count += 1

        return count

    async def get_agents(
        self,
        simulation_id: str,
        limit: int = 100,
        state_filter: Optional[str] = None
    ) -> List[GenerativeAgent]:
        """Get agents for a simulation."""
        if self.use_memory:
            agents = []
            for data in self._memory_store["agents"].values():
                if data["simulation_id"] == simulation_id:
                    if state_filter is None or data.get("final_state") == state_filter:
                        agents.append(GenerativeAgent(**data["data"]))
                        if len(agents) >= limit:
                            break
            return agents
        else:
            query = self.client.table("agents").select("*").eq("simulation_id", simulation_id)
            if state_filter:
                query = query.eq("final_state", state_filter)
            result = query.limit(limit).execute()
            return [GenerativeAgent(**r["data"]) for r in result.data]

    async def get_agent(self, agent_id: str) -> Optional[GenerativeAgent]:
        """Get a single agent by ID."""
        if self.use_memory:
            data = self._memory_store["agents"].get(agent_id)
            if data:
                return GenerativeAgent(**data["data"])
            return None
        else:
            result = self.client.table("agents").select("*").eq("id", agent_id).execute()
            if result.data:
                return GenerativeAgent(**result.data[0]["data"])
            return None

    # ==================== JOURNAL ENTRIES ====================

    async def add_journal_entry(
        self,
        decision_id: str,
        event_type: str,
        data: Dict
    ) -> str:
        """Add a journal entry for audit trail."""
        entry_id = str(uuid.uuid4())

        entry = {
            "id": entry_id,
            "decision_id": decision_id,
            "event_type": event_type,
            "data": data,
            "created_at": datetime.now().isoformat()
        }

        if self.use_memory:
            self._memory_store["journal_entries"][entry_id] = entry
        else:
            self.client.table("journal_entries").insert(entry).execute()

        return entry_id

    async def get_journal(self, decision_id: str) -> List[Dict]:
        """Get all journal entries for a decision."""
        if self.use_memory:
            entries = [
                e for e in self._memory_store["journal_entries"].values()
                if e["decision_id"] == decision_id
            ]
            return sorted(entries, key=lambda x: x["created_at"])
        else:
            result = self.client.table("journal_entries").select("*").eq(
                "decision_id", decision_id
            ).order("created_at").execute()
            return result.data

    # ==================== RECOMMENDATIONS ====================

    async def save_recommendation(
        self,
        decision_id: str,
        simulation_id: str,
        recommendation: Dict
    ) -> str:
        """Save a recommendation."""
        rec_id = str(uuid.uuid4())

        data = {
            "id": rec_id,
            "decision_id": decision_id,
            "simulation_id": simulation_id,
            "recommended_option": recommendation.get("recommended_option_id"),
            "confidence": recommendation.get("confidence"),
            "data": recommendation,
            "created_at": datetime.now().isoformat()
        }

        if self.use_memory:
            self._memory_store["recommendations"][rec_id] = data
        else:
            self.client.table("recommendations").upsert(data).execute()

        return rec_id

    async def get_recommendation(self, decision_id: str) -> Optional[Dict]:
        """Get the latest recommendation for a decision."""
        if self.use_memory:
            recs = [
                r for r in self._memory_store["recommendations"].values()
                if r["decision_id"] == decision_id
            ]
            if recs:
                return sorted(recs, key=lambda x: x["created_at"], reverse=True)[0]["data"]
            return None
        else:
            result = self.client.table("recommendations").select("*").eq(
                "decision_id", decision_id
            ).order("created_at", desc=True).limit(1).execute()
            if result.data:
                return result.data[0]["data"]
            return None

    # ==================== UTILITY METHODS ====================

    async def health_check(self) -> Dict:
        """Check database health and return stats."""
        if self.use_memory:
            return {
                "status": "healthy",
                "mode": "in-memory",
                "companies": len(self._memory_store["companies"]),
                "decisions": len(self._memory_store["decisions"]),
                "simulations": len(self._memory_store["simulations"]),
                "agents": len(self._memory_store["agents"])
            }
        else:
            # Check Supabase connection
            try:
                self.client.table("companies").select("count").execute()
                return {
                    "status": "healthy",
                    "mode": "supabase",
                    "connected": True
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "mode": "supabase",
                    "error": str(e)
                }

    def clear_memory(self):
        """Clear in-memory storage (for testing)."""
        if self.use_memory:
            for key in self._memory_store:
                self._memory_store[key] = {}
