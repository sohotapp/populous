"""
RLTX Populous Data Models

This module defines the core data structures for the simulation platform:
- Scenario: The market environment (Layer 1: Data Foundation)
- Agent: Synthetic decision-makers (Layer 3: Behavioral Models)
- Strategy: Go-to-market interventions being tested
- Results: Simulation outputs (Layer 5: Prediction)
- Decision: Strategic decisions for analysis
- Company: Company profiles from research
- Competitor Agent: Game-theoretic competitor models
- Scenario Branch: Monte Carlo branching scenarios
- Confidence: Uncertainty decomposition
- Journal: Decision tracking and calibration
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

from .decision import (
    Decision,
    Option,
    Constraint,
    SuccessCriteria,
    DecisionStatus,
)

from .company import (
    Company,
    ResearchResult,
    Market,
    CompanyProduct,
    Leader,
)

from .competitor_agent import (
    CompetitorAgent,
    CompetitorMove,
    MarketState,
    StrategyType,
    GameTheoreticAnalysis,
)

from .scenario_branch import (
    ScenarioNode,
    ScenarioTree,
    ScenarioPath,
    ScenarioSummary,
    ScenarioBranchInput,
)

from .confidence import (
    UncertaintySource,
    ConfidenceLevel,
    UncertaintyComponent,
    ConfidenceDecomposition,
    ConfidenceReport,
)

from .journal import (
    JournalEntry,
    Prediction,
    Outcome,
    LessonLearned,
    DecisionJournal,
    JournalExport,
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
    # Decision
    "Decision",
    "Option",
    "Constraint",
    "SuccessCriteria",
    "DecisionStatus",
    # Company
    "Company",
    "ResearchResult",
    "Market",
    "CompanyProduct",
    "Leader",
    # Competitor Agent
    "CompetitorAgent",
    "CompetitorMove",
    "MarketState",
    "StrategyType",
    "GameTheoreticAnalysis",
    # Scenario Branch
    "ScenarioNode",
    "ScenarioTree",
    "ScenarioPath",
    "ScenarioSummary",
    "ScenarioBranchInput",
    # Confidence
    "UncertaintySource",
    "ConfidenceLevel",
    "UncertaintyComponent",
    "ConfidenceDecomposition",
    "ConfidenceReport",
    # Journal
    "JournalEntry",
    "Prediction",
    "Outcome",
    "LessonLearned",
    "DecisionJournal",
    "JournalExport",
]
