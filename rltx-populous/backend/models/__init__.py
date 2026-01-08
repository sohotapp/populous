"""
RLTX Populous Data Models

This module defines the core data structures for the simulation platform:
- Scenario: The market environment (Layer 1: Data Foundation)
- Agent: Synthetic decision-makers (Layer 3: Behavioral Models)
- Strategy: Go-to-market interventions being tested
- Results: Simulation outputs (Layer 5: Prediction)
"""

from .scenario import (
    MarketType,
    Stakeholder,
    DecisionFramework,
    BehavioralProfile,
    Segment,
    Competitor,
    Product,
    Scenario,
)

from .agent import (
    Persona,
    Belief,
    DecisionEvent,
    Agent,
)

from .strategy import (
    Messaging,
    DiscountStrategy,
    Pricing,
    CompetitiveResponse,
    GoToMarket,
    Strategy,
)

from .results import (
    DailySnapshot,
    BranchResult,
    SegmentAnalysis,
    DriverAnalysis,
    SimulationResults,
)

__all__ = [
    # Scenario
    "MarketType",
    "Stakeholder",
    "DecisionFramework",
    "BehavioralProfile",
    "Segment",
    "Competitor",
    "Product",
    "Scenario",
    # Agent
    "Persona",
    "Belief",
    "DecisionEvent",
    "Agent",
    # Strategy
    "Messaging",
    "DiscountStrategy",
    "Pricing",
    "CompetitiveResponse",
    "GoToMarket",
    "Strategy",
    # Results
    "DailySnapshot",
    "BranchResult",
    "SegmentAnalysis",
    "DriverAnalysis",
    "SimulationResults",
]
