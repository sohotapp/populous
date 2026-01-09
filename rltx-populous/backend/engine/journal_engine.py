"""
Decision Journal Engine
Tracks predictions vs outcomes for accountability and learning
"What did we predict? What happened? What did we learn?"
"""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from anthropic import Anthropic

from backend.models.journal import (
    DecisionJournal, JournalEntry, JournalEventType, Prediction,
    Outcome, LessonLearned, DecisionReview, PredictionAccuracy,
    JournalAnalytics, JournalExport
)
from backend.models.decision import Decision
from backend.db.supabase import get_database


class JournalEngine:
    """
    Engine for decision journaling and prediction tracking.
    Creates accountability and enables learning from past decisions.
    """

    def __init__(self, llm_client: Anthropic = None):
        self.llm = llm_client or Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.db = get_database()

    async def create_journal(self, decision: Decision) -> DecisionJournal:
        """
        Create a new decision journal.
        """
        journal = DecisionJournal(
            decision_id=decision.id
        )

        # Add creation entry
        entry = JournalEntry(
            decision_id=decision.id,
            event_type=JournalEventType.DECISION_CREATED,
            title="Decision Created",
            description=f"Decision '{decision.title}' created for analysis",
            data={
                "decision_title": decision.title,
                "options_count": len(decision.options),
                "context": decision.context
            }
        )
        journal.entries.append(entry)

        # Save to database
        await self.db.add_journal_entry(
            decision.id,
            entry.event_type.value,
            entry.model_dump()
        )

        return journal

    async def add_prediction(
        self,
        journal: DecisionJournal,
        prediction_type: str,
        predicted_value: Any,
        confidence: float,
        due_date: Optional[datetime] = None,
        context: Optional[Dict] = None,
        assumptions: Optional[List[str]] = None
    ) -> Prediction:
        """
        Record a prediction for later validation.
        """
        prediction = Prediction(
            decision_id=journal.decision_id,
            prediction_type=prediction_type,
            predicted_value=predicted_value,
            confidence=confidence,
            due_date=due_date or datetime.now() + timedelta(days=90),
            context=context or {},
            assumptions=assumptions or []
        )

        journal.predictions.append(prediction)
        journal.total_predictions += 1

        # Add journal entry
        entry = JournalEntry(
            decision_id=journal.decision_id,
            event_type=JournalEventType.PREDICTION_MADE,
            title=f"Prediction: {prediction_type}",
            description=f"Predicted {prediction_type}: {predicted_value} (confidence: {confidence:.0%})",
            data=prediction.model_dump()
        )
        journal.entries.append(entry)

        await self.db.add_journal_entry(
            journal.decision_id,
            entry.event_type.value,
            entry.model_dump()
        )

        return prediction

    async def record_outcome(
        self,
        journal: DecisionJournal,
        prediction_id: str,
        actual_value: Any,
        description: str = "",
        sources: Optional[List[str]] = None
    ) -> Outcome:
        """
        Record the actual outcome for a prediction.
        """
        # Find the prediction
        prediction = None
        for p in journal.predictions:
            if p.id == prediction_id:
                prediction = p
                break

        if not prediction:
            raise ValueError(f"Prediction {prediction_id} not found")

        # Create outcome record
        outcome = Outcome(
            prediction_id=prediction_id,
            actual_value=actual_value,
            description=description,
            sources=sources or []
        )

        # Update prediction
        prediction.outcome_recorded = True
        prediction.actual_value = actual_value
        prediction.accuracy = self._calculate_accuracy(
            prediction.predicted_value,
            actual_value,
            prediction.prediction_type
        )
        prediction.error_magnitude = self._calculate_error(
            prediction.predicted_value,
            actual_value,
            prediction.prediction_type
        )

        journal.outcomes.append(outcome)
        journal.predictions_validated += 1

        # Recalculate overall accuracy
        accurate_count = sum(
            1 for p in journal.predictions
            if p.accuracy in [PredictionAccuracy.VERY_ACCURATE, PredictionAccuracy.ACCURATE]
        )
        journal.overall_accuracy = accurate_count / max(1, journal.predictions_validated)

        # Add journal entry
        entry = JournalEntry(
            decision_id=journal.decision_id,
            event_type=JournalEventType.OUTCOME_RECORDED,
            title=f"Outcome: {prediction.prediction_type}",
            description=f"Actual: {actual_value} (predicted: {prediction.predicted_value}, accuracy: {prediction.accuracy.value})",
            data={
                "prediction_id": prediction_id,
                "predicted": prediction.predicted_value,
                "actual": actual_value,
                "accuracy": prediction.accuracy.value,
                "error": prediction.error_magnitude
            }
        )
        journal.entries.append(entry)

        await self.db.add_journal_entry(
            journal.decision_id,
            entry.event_type.value,
            entry.model_dump()
        )

        return outcome

    def _calculate_accuracy(
        self,
        predicted: Any,
        actual: Any,
        prediction_type: str
    ) -> PredictionAccuracy:
        """
        Calculate prediction accuracy category.
        """
        try:
            if isinstance(predicted, (int, float)) and isinstance(actual, (int, float)):
                # Numeric comparison
                if predicted == 0:
                    if actual == 0:
                        return PredictionAccuracy.VERY_ACCURATE
                    return PredictionAccuracy.INACCURATE

                error = abs(actual - predicted) / abs(predicted)

                if error <= 0.05:
                    return PredictionAccuracy.VERY_ACCURATE
                elif error <= 0.15:
                    return PredictionAccuracy.ACCURATE
                elif error <= 0.30:
                    return PredictionAccuracy.CLOSE
                else:
                    # Check if direction is right
                    if (predicted > 0) != (actual > 0):
                        return PredictionAccuracy.OPPOSITE
                    return PredictionAccuracy.INACCURATE

            elif isinstance(predicted, str) and isinstance(actual, str):
                # Categorical comparison
                if predicted.lower() == actual.lower():
                    return PredictionAccuracy.VERY_ACCURATE
                elif self._are_similar_categories(predicted, actual):
                    return PredictionAccuracy.CLOSE
                else:
                    return PredictionAccuracy.INACCURATE

            else:
                # Default comparison
                if predicted == actual:
                    return PredictionAccuracy.VERY_ACCURATE
                return PredictionAccuracy.INACCURATE

        except Exception:
            return PredictionAccuracy.INACCURATE

    def _calculate_error(
        self,
        predicted: Any,
        actual: Any,
        prediction_type: str
    ) -> Optional[float]:
        """Calculate numeric error magnitude."""
        try:
            if isinstance(predicted, (int, float)) and isinstance(actual, (int, float)):
                if predicted == 0:
                    return float('inf') if actual != 0 else 0.0
                return abs(actual - predicted) / abs(predicted)
        except Exception:
            pass
        return None

    def _are_similar_categories(self, a: str, b: str) -> bool:
        """Check if two categorical values are similar."""
        # Define similarity groups
        similar_groups = [
            ["favorable", "positive", "good", "win"],
            ["unfavorable", "negative", "bad", "lose"],
            ["neutral", "moderate", "unchanged"],
            ["aggressive", "strong", "escalate"],
            ["defensive", "passive", "retreat"]
        ]

        a_lower = a.lower()
        b_lower = b.lower()

        for group in similar_groups:
            if any(word in a_lower for word in group) and any(word in b_lower for word in group):
                return True

        return False

    async def conduct_review(
        self,
        journal: DecisionJournal,
        decision: Decision
    ) -> DecisionReview:
        """
        Conduct a structured review of a decision.
        """
        # Calculate metrics
        validated = [p for p in journal.predictions if p.outcome_recorded]
        accurate = [
            p for p in validated
            if p.accuracy in [PredictionAccuracy.VERY_ACCURATE, PredictionAccuracy.ACCURATE, PredictionAccuracy.CLOSE]
        ]

        # Generate findings using LLM
        findings = await self._analyze_decision_outcomes(journal, decision)

        # Extract lessons
        lessons = await self._extract_lessons(journal, findings)

        review = DecisionReview(
            decision_id=journal.decision_id,
            decision_summary=decision.title,
            time_since_decision_days=(datetime.now() - journal.created_at).days,
            predictions_made=len(journal.predictions),
            predictions_accurate=len(accurate),
            accuracy_rate=len(accurate) / max(1, len(validated)),
            what_went_well=findings.get("went_well", []),
            what_went_wrong=findings.get("went_wrong", []),
            surprises=findings.get("surprises", []),
            lessons=lessons,
            overall_score=len(accurate) / max(1, len(validated)),
            would_decide_same_again=findings.get("would_repeat", True)
        )

        journal.reviews.append(review)
        journal.lessons.extend(lessons)

        # Add journal entry
        entry = JournalEntry(
            decision_id=journal.decision_id,
            event_type=JournalEventType.REVIEW_CONDUCTED,
            title="Decision Review",
            description=f"Review conducted: {len(accurate)}/{len(validated)} predictions accurate",
            data=review.model_dump()
        )
        journal.entries.append(entry)

        await self.db.add_journal_entry(
            journal.decision_id,
            entry.event_type.value,
            entry.model_dump()
        )

        return review

    async def _analyze_decision_outcomes(
        self,
        journal: DecisionJournal,
        decision: Decision
    ) -> Dict[str, Any]:
        """Use LLM to analyze decision outcomes."""
        validated = [p for p in journal.predictions if p.outcome_recorded]

        if not validated:
            return {
                "went_well": ["Insufficient data for analysis"],
                "went_wrong": [],
                "surprises": [],
                "would_repeat": True
            }

        # Format predictions for analysis
        pred_summary = "\n".join([
            f"- {p.prediction_type}: Predicted {p.predicted_value}, Actual {p.actual_value}, Accuracy: {p.accuracy.value}"
            for p in validated
        ])

        prompt = f"""Analyze this decision's outcomes:

DECISION: {decision.title}
CONTEXT: {decision.context}

PREDICTIONS VS OUTCOMES:
{pred_summary}

Provide analysis in JSON format:
{{
    "went_well": ["list of things that went well"],
    "went_wrong": ["list of things that went wrong"],
    "surprises": ["unexpected outcomes"],
    "would_repeat": true/false,
    "key_insight": "main takeaway"
}}"""

        try:
            response = self.llm.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            text = response.content[0].text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])

        except Exception as e:
            print(f"Analysis failed: {e}")

        return {
            "went_well": [],
            "went_wrong": [],
            "surprises": [],
            "would_repeat": True
        }

    async def _extract_lessons(
        self,
        journal: DecisionJournal,
        findings: Dict[str, Any]
    ) -> List[LessonLearned]:
        """Extract lessons from review findings."""
        lessons = []

        # Create lessons from what went wrong
        for issue in findings.get("went_wrong", []):
            lesson = LessonLearned(
                decision_id=journal.decision_id,
                title=f"Issue: {issue[:50]}",
                description=issue,
                category="execution",
                recommended_changes=[f"Address: {issue}"]
            )
            lessons.append(lesson)

        # Create lessons from surprises
        for surprise in findings.get("surprises", []):
            lesson = LessonLearned(
                decision_id=journal.decision_id,
                title=f"Surprise: {surprise[:50]}",
                description=surprise,
                category="model",
                recommended_changes=["Update model to account for this factor"]
            )
            lessons.append(lesson)

        return lessons

    async def get_analytics(
        self,
        journals: List[DecisionJournal]
    ) -> JournalAnalytics:
        """
        Calculate analytics across multiple journals.
        """
        total_predictions = sum(j.total_predictions for j in journals)
        validated = sum(j.predictions_validated for j in journals)

        # Calculate accuracy by type
        type_accuracy = defaultdict(lambda: {"correct": 0, "total": 0})

        for journal in journals:
            for pred in journal.predictions:
                if pred.outcome_recorded:
                    type_accuracy[pred.prediction_type]["total"] += 1
                    if pred.accuracy in [PredictionAccuracy.VERY_ACCURATE, PredictionAccuracy.ACCURATE]:
                        type_accuracy[pred.prediction_type]["correct"] += 1

        accuracy_by_type = {
            t: data["correct"] / max(1, data["total"])
            for t, data in type_accuracy.items()
        }

        # Calculate calibration (confidence vs actual accuracy)
        calibration = self._calculate_calibration(journals)

        # Collect all lessons
        all_lessons = []
        for journal in journals:
            all_lessons.extend(journal.lessons)

        # Find common error patterns
        error_patterns = self._find_error_patterns(journals)

        return JournalAnalytics(
            total_decisions=len(journals),
            total_predictions=total_predictions,
            predictions_validated=validated,
            overall_accuracy_rate=sum(j.overall_accuracy for j in journals) / max(1, len(journals)),
            accuracy_by_type=accuracy_by_type,
            frequent_errors=error_patterns,
            all_lessons=all_lessons,
            calibration_data=calibration
        )

    def _calculate_calibration(self, journals: List[DecisionJournal]) -> Dict[str, Any]:
        """Calculate calibration data (confidence vs accuracy)."""
        # Group predictions by confidence buckets
        buckets = {
            "0.0-0.2": {"predictions": [], "accurate": 0, "total": 0},
            "0.2-0.4": {"predictions": [], "accurate": 0, "total": 0},
            "0.4-0.6": {"predictions": [], "accurate": 0, "total": 0},
            "0.6-0.8": {"predictions": [], "accurate": 0, "total": 0},
            "0.8-1.0": {"predictions": [], "accurate": 0, "total": 0}
        }

        for journal in journals:
            for pred in journal.predictions:
                if not pred.outcome_recorded:
                    continue

                conf = pred.confidence
                if conf < 0.2:
                    bucket = "0.0-0.2"
                elif conf < 0.4:
                    bucket = "0.2-0.4"
                elif conf < 0.6:
                    bucket = "0.4-0.6"
                elif conf < 0.8:
                    bucket = "0.6-0.8"
                else:
                    bucket = "0.8-1.0"

                buckets[bucket]["total"] += 1
                if pred.accuracy in [PredictionAccuracy.VERY_ACCURATE, PredictionAccuracy.ACCURATE]:
                    buckets[bucket]["accurate"] += 1

        # Calculate accuracy per bucket
        calibration_curve = {}
        for bucket, data in buckets.items():
            if data["total"] > 0:
                calibration_curve[bucket] = {
                    "expected_accuracy": float(bucket.split("-")[0]),
                    "actual_accuracy": data["accurate"] / data["total"],
                    "sample_size": data["total"]
                }

        return {
            "calibration_curve": calibration_curve,
            "is_overconfident": self._check_overconfidence(calibration_curve),
            "is_underconfident": self._check_underconfidence(calibration_curve)
        }

    def _check_overconfidence(self, calibration: Dict) -> bool:
        """Check if predictions tend to be overconfident."""
        overconfident_buckets = 0
        for bucket, data in calibration.items():
            if data.get("actual_accuracy", 0) < data.get("expected_accuracy", 0) - 0.1:
                overconfident_buckets += 1
        return overconfident_buckets >= 2

    def _check_underconfidence(self, calibration: Dict) -> bool:
        """Check if predictions tend to be underconfident."""
        underconfident_buckets = 0
        for bucket, data in calibration.items():
            if data.get("actual_accuracy", 0) > data.get("expected_accuracy", 0) + 0.1:
                underconfident_buckets += 1
        return underconfident_buckets >= 2

    def _find_error_patterns(self, journals: List[DecisionJournal]) -> List[Dict[str, Any]]:
        """Find common error patterns across journals."""
        error_types = defaultdict(int)
        error_details = defaultdict(list)

        for journal in journals:
            for pred in journal.predictions:
                if pred.outcome_recorded and pred.accuracy in [
                    PredictionAccuracy.INACCURATE, PredictionAccuracy.OPPOSITE
                ]:
                    error_types[pred.prediction_type] += 1
                    error_details[pred.prediction_type].append({
                        "predicted": pred.predicted_value,
                        "actual": pred.actual_value,
                        "confidence": pred.confidence
                    })

        patterns = []
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            patterns.append({
                "type": error_type,
                "frequency": count,
                "examples": error_details[error_type][:3]
            })

        return patterns[:5]

    def export_journal(
        self,
        journal: DecisionJournal,
        decision: Decision
    ) -> JournalExport:
        """
        Export journal to a portable format.
        """
        # Build timeline
        timeline = [
            {
                "timestamp": e.created_at.isoformat(),
                "event": e.event_type.value,
                "title": e.title,
                "description": e.description
            }
            for e in sorted(journal.entries, key=lambda x: x.created_at)
        ]

        # Build prediction outcomes
        prediction_outcomes = [
            {
                "type": p.prediction_type,
                "predicted": p.predicted_value,
                "actual": p.actual_value,
                "confidence": p.confidence,
                "accuracy": p.accuracy.value if p.accuracy else "pending",
                "date": p.created_at.isoformat()
            }
            for p in journal.predictions
        ]

        # Collect lessons
        lessons = [l.description for l in journal.lessons]

        return JournalExport(
            decision_title=decision.title,
            decision_date=journal.created_at,
            decision_summary=decision.context or decision.title,
            timeline=timeline,
            prediction_outcomes=prediction_outcomes,
            lessons_learned=lessons
        )

    async def add_manual_entry(
        self,
        journal: DecisionJournal,
        title: str,
        description: str,
        event_type: JournalEventType = JournalEventType.LESSON_LEARNED,
        data: Optional[Dict] = None
    ) -> JournalEntry:
        """
        Add a manual journal entry.
        """
        entry = JournalEntry(
            decision_id=journal.decision_id,
            event_type=event_type,
            title=title,
            description=description,
            data=data or {},
            created_by="user"
        )

        journal.entries.append(entry)

        await self.db.add_journal_entry(
            journal.decision_id,
            entry.event_type.value,
            entry.model_dump()
        )

        return entry
