"""
Survey models for the Populous platform.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    RATING_SCALE = "rating_scale"
    OPEN_TEXT = "open_text"
    RANKING = "ranking"


class ScaleLabels(BaseModel):
    min: str
    max: str


class Question(BaseModel):
    """A survey question"""

    id: str
    type: QuestionType
    text: str
    options: List[str] = []
    scale_min: Optional[int] = None
    scale_max: Optional[int] = None
    scale_labels: Optional[ScaleLabels] = None
    required: bool = True
    order: int = 0


class Survey(BaseModel):
    """A survey attached to a project"""

    id: str
    project_id: str
    questions: List[Question] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class QuestionPrediction(BaseModel):
    """AI prediction for a single question"""
    question_id: str
    confidence: ConfidenceLevel
    predictions: Dict[str, float] = {}  # option -> percentage
    mean_score: Optional[float] = None
    distribution: Optional[str] = None


class SurveyPredictions(BaseModel):
    """AI predictions for an entire survey"""
    survey_id: str
    overall_confidence: ConfidenceLevel
    questions: List[QuestionPrediction] = []
    is_updating: bool = False


class AISuggestion(BaseModel):
    """AI-generated question suggestion"""
    id: str
    type: str  # "question" or "improvement"
    text: str
    reasoning: str
    suggested_question: Optional[Question] = None


class BiasWarning(BaseModel):
    """Warning about potential bias in a question"""
    question_id: str
    severity: str  # "warning" or "error"
    issue: str
    suggestion: str
