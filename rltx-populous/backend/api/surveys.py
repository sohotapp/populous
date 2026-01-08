"""
Survey API routes with AI predictions.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict
import uuid
import random

from backend.models.survey import (
    Survey,
    Question,
    QuestionType,
    SurveyPredictions,
    QuestionPrediction,
    ConfidenceLevel,
    AISuggestion,
    BiasWarning,
)

router = APIRouter(tags=["surveys"])

# In-memory storage
surveys_db: dict[str, Survey] = {}


@router.get("/projects/{project_id}/survey", response_model=Survey)
def get_survey(project_id: str):
    """Get survey for a project"""
    survey = surveys_db.get(project_id)
    if not survey:
        # Create empty survey
        survey = Survey(
            id=str(uuid.uuid4()),
            project_id=project_id,
            questions=[],
        )
        surveys_db[project_id] = survey
    return survey


@router.put("/projects/{project_id}/survey", response_model=Survey)
def update_survey(project_id: str, questions: List[Question]):
    """Update survey questions"""
    survey = surveys_db.get(project_id)
    if not survey:
        survey = Survey(
            id=str(uuid.uuid4()),
            project_id=project_id,
            questions=[],
        )

    survey.questions = questions
    surveys_db[project_id] = survey
    return survey


@router.post("/projects/{project_id}/survey/predict", response_model=SurveyPredictions)
def predict_survey_responses(project_id: str):
    """Generate AI predictions for survey responses"""
    survey = surveys_db.get(project_id)
    if not survey:
        raise HTTPException(404, "Survey not found")

    if not survey.questions:
        raise HTTPException(400, "Survey has no questions")

    # Generate mock predictions
    question_predictions = []

    for question in survey.questions:
        if question.type == QuestionType.SINGLE_CHOICE or question.type == QuestionType.MULTIPLE_CHOICE:
            # Generate predictions for each option
            predictions = {}
            remaining = 100
            for i, option in enumerate(question.options):
                if i == len(question.options) - 1:
                    predictions[option] = remaining
                else:
                    val = random.randint(max(10, remaining // 3), min(remaining - 10, remaining // 2 + 20))
                    predictions[option] = val
                    remaining -= val

            question_predictions.append(QuestionPrediction(
                question_id=question.id,
                confidence=_calculate_confidence(len(survey.questions)),
                predictions=predictions,
            ))

        elif question.type == QuestionType.RATING_SCALE:
            question_predictions.append(QuestionPrediction(
                question_id=question.id,
                confidence=_calculate_confidence(len(survey.questions)),
                predictions={},
                mean_score=round(random.uniform(2.5, 4.5), 1),
                distribution="Slightly negative skew expected",
            ))

    return SurveyPredictions(
        survey_id=survey.id,
        overall_confidence=_calculate_confidence(len(survey.questions)),
        questions=question_predictions,
        is_updating=False,
    )


def _calculate_confidence(question_count: int) -> ConfidenceLevel:
    """Calculate confidence level based on survey complexity"""
    if question_count >= 5:
        return ConfidenceLevel.HIGH
    elif question_count >= 2:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW


# ============ AI Features ============

@router.post("/ai/suggest-question", response_model=AISuggestion)
def suggest_question(survey_id: str, goal: str = None):
    """Generate AI question suggestion based on survey context"""

    suggestions = [
        {
            "text": "Based on your goal to understand product usage, consider asking about price sensitivity to get deeper insights into purchasing decisions.",
            "reasoning": "This helps correlate satisfaction with price perception.",
            "suggested_question": Question(
                id=str(uuid.uuid4()),
                type=QuestionType.RATING_SCALE,
                text="How satisfied are you with the product's current pricing?",
                options=[],
                scale_min=1,
                scale_max=5,
                required=True,
                order=0,
            ),
        },
        {
            "text": "Consider adding a question about purchase frequency to understand usage patterns.",
            "reasoning": "Frequency data helps segment users by engagement level.",
            "suggested_question": Question(
                id=str(uuid.uuid4()),
                type=QuestionType.SINGLE_CHOICE,
                text="How often do you use our product?",
                options=["Daily", "Weekly", "Monthly", "Rarely"],
                required=True,
                order=0,
            ),
        },
    ]

    suggestion = random.choice(suggestions)

    return AISuggestion(
        id=str(uuid.uuid4()),
        type="question",
        text=suggestion["text"],
        reasoning=suggestion["reasoning"],
        suggested_question=suggestion["suggested_question"],
    )


@router.post("/ai/check-bias", response_model=BiasWarning)
def check_bias(question: Question):
    """Check a question for potential bias"""

    # Simple bias detection rules
    bias_triggers = [
        ("best", "This superlative may lead respondents toward positive answers"),
        ("worst", "This superlative may lead respondents toward negative answers"),
        ("amazing", "This adjective may bias responses positively"),
        ("terrible", "This adjective may bias responses negatively"),
        ("don't you think", "This phrasing suggests a preferred answer"),
        ("obviously", "This assumes agreement and may bias responses"),
    ]

    question_lower = question.text.lower()

    for trigger, issue in bias_triggers:
        if trigger in question_lower:
            return BiasWarning(
                question_id=question.id,
                severity="warning",
                issue=f"{issue}. The phrase '{trigger}' may influence responses.",
                suggestion=question.text.replace(trigger, "").strip(),
            )

    # No bias detected - return a minimal warning (in production, return None)
    return BiasWarning(
        question_id=question.id,
        severity="info",
        issue="No significant bias detected.",
        suggestion="",
    )
