"""
RLTX Populous Simulation Engine

The core simulation components:
- AgentFactory: Creates synthetic decision-makers with optional LLM personas
- DecisionEngine: Hybrid LLM + mathematical decision logic
- MarketDynamics: GTM signals, competitive response, network effects
- SimulationRunner: Monte Carlo parallel branch execution
- ResearchEngine: Live web research with Exa API
- CompetitorEngine: Game-theoretic competitor simulation
- ScenarioEngine: Monte Carlo scenario branching
- ConfidenceEngine: Uncertainty decomposition
- JournalEngine: Decision tracking and calibration
- ExportEngine: Markdown and PDF exports
"""

from .agent_factory import AgentFactory
from .decision_engine import DecisionEngine
from .market_dynamics import MarketDynamics
from .runner import SimulationRunner
from .research_engine import ResearchEngine
from .competitor_engine import CompetitorEngine
from .scenario_engine import ScenarioEngine
from .confidence_engine import ConfidenceEngine
from .journal_engine import JournalEngine
from .export_engine import ExportEngine

__all__ = [
    "AgentFactory",
    "DecisionEngine",
    "MarketDynamics",
    "SimulationRunner",
    "ResearchEngine",
    "CompetitorEngine",
    "ScenarioEngine",
    "ConfidenceEngine",
    "JournalEngine",
    "ExportEngine",
]
