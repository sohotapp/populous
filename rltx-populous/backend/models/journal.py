"""
Decision Journal Models
Tracking predictions vs outcomes for learning and accountability
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import uuid


class JournalEventType(str, Enum):
    """Types of journal events"""
    DECISION_CREATED = "decision_created"
    PREDICTION_MADE = "prediction_made"
    SIMULATION_RUN = "simulation_run"
    RECOMMENDATION_GENERATED = "recommendation_generated"
    DECISION_TAKEN = "decision_taken"
    OUTCOME_RECORDED = "outcome_recorded"
    REVIEW_CONDUCTED = "review_conducted"
    LESSON_LEARNED = "lesson_learned"


class PredictionAccuracy(str, Enum):
    """How accurate was a prediction"""
    VERY_ACCURATE = "very_accurate"     # Within 5%
    ACCURATE = "accurate"               # Within 15%
    CLOSE = "close"                     # Within 30%
    INACCURATE = "inaccurate"          # Off by more than 30%
    OPPOSITE = "opposite"               # Wrong direction


class JournalEntry(BaseModel):
    """A single entry in the decision journal"""
    id: str = Field(default_factory=lambda: f"entry_{uuid.uuid4().hex[:8]}")
    decision_id: str
    created_at: datetime = Field(default_factory=datetime.now)

    # Event details
    event_type: JournalEventType
    title: str = ""
    description: str = ""

    # Structured data
    data: Dict[str, Any] = {}

    # Attribution
    created_by: str = "system"         # system, user, etc.

    # For audit trail
    previous_entry_id: Optional[str] = None


class Prediction(BaseModel):
    """A recorded prediction for later validation"""
    id: str = Field(default_factory=lambda: f"pred_{uuid.uuid4().hex[:8]}")
    decision_id: str
    created_at: datetime = Field(default_factory=datetime.now)

    # What was predicted
    prediction_type: str               # e.g., "market_share", "competitor_response"
    predicted_value: Any               # The prediction itself
    confidence: float = 0.5           # 0-1

    # Context at time of prediction
    context: Dict[str, Any] = {}
    assumptions: List[str] = []

    # Outcome tracking
    due_date: Optional[datetime] = None
    outcome_recorded: bool = False
    actual_value: Optional[Any] = None
    accuracy: Optional[PredictionAccuracy] = None

    # Analysis
    error_magnitude: Optional[float] = None
    reasons_for_error: List[str] = []


class Outcome(BaseModel):
    """Recorded outcome for a prediction"""
    id: str = Field(default_factory=lambda: f"outcome_{uuid.uuid4().hex[:8]}")
    prediction_id: str
    recorded_at: datetime = Field(default_factory=datetime.now)

    actual_value: Any
    actual_context: Dict[str, Any] = {}

    # What happened
    description: str = ""

    # Evidence
    sources: List[str] = []            # Links, documents, etc.


class LessonLearned(BaseModel):
    """A lesson extracted from comparing predictions to outcomes"""
    id: str = Field(default_factory=lambda: f"lesson_{uuid.uuid4().hex[:8]}")
    decision_id: str
    created_at: datetime = Field(default_factory=datetime.now)

    # The insight
    title: str
    description: str
    category: str = "general"          # model, data, execution, market

    # Evidence
    supporting_predictions: List[str] = []  # Prediction IDs
    pattern_frequency: int = 1         # How often this pattern occurred

    # Actions
    recommended_changes: List[str] = []
    applied: bool = False


class DecisionReview(BaseModel):
    """A structured review of a past decision"""
    id: str = Field(default_factory=lambda: f"review_{uuid.uuid4().hex[:8]}")
    decision_id: str
    review_date: datetime = Field(default_factory=datetime.now)

    # Summary
    decision_summary: str = ""
    time_since_decision_days: int = 0

    # Prediction analysis
    predictions_made: int = 0
    predictions_accurate: int = 0
    accuracy_rate: float = 0.0

    # Key findings
    what_went_well: List[str] = []
    what_went_wrong: List[str] = []
    surprises: List[str] = []

    # Learnings
    lessons: List[LessonLearned] = []
    process_improvements: List[str] = []

    # Score
    overall_score: float = 0.0         # 0-1
    would_decide_same_again: bool = True


class DecisionJournal(BaseModel):
    """Complete journal for a decision"""
    id: str = Field(default_factory=lambda: f"journal_{uuid.uuid4().hex[:8]}")
    decision_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)

    # Timeline
    entries: List[JournalEntry] = []

    # Predictions and outcomes
    predictions: List[Prediction] = []
    outcomes: List[Outcome] = []

    # Reviews
    reviews: List[DecisionReview] = []

    # Learnings
    lessons: List[LessonLearned] = []

    # Status
    decision_complete: bool = False
    all_outcomes_recorded: bool = False

    # Aggregate metrics
    total_predictions: int = 0
    predictions_validated: int = 0
    overall_accuracy: float = 0.0


class JournalAnalytics(BaseModel):
    """Analytics across all decision journals"""
    total_decisions: int = 0
    total_predictions: int = 0
    predictions_validated: int = 0

    # Accuracy metrics
    overall_accuracy_rate: float = 0.0
    accuracy_by_type: Dict[str, float] = {}
    accuracy_trend: List[Dict[str, Any]] = []  # Over time

    # Common patterns
    frequent_errors: List[Dict[str, Any]] = []
    reliable_predictions: List[str] = []

    # Lessons
    all_lessons: List[LessonLearned] = []
    most_impactful_lessons: List[str] = []

    # Calibration
    calibration_data: Dict[str, Any] = {}  # confidence vs accuracy


class JournalExport(BaseModel):
    """Exportable journal format"""
    decision_title: str
    decision_date: datetime
    decision_summary: str

    # Timeline
    timeline: List[Dict[str, Any]] = []

    # Predictions and outcomes
    prediction_outcomes: List[Dict[str, Any]] = []

    # Key learnings
    lessons_learned: List[str] = []

    # Metadata
    export_date: datetime = Field(default_factory=datetime.now)
    format_version: str = "1.0"
