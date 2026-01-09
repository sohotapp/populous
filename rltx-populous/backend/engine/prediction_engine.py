"""
Prediction Engine
Real-time survey response predictions
"""

from typing import List, Dict, Optional
from anthropic import Anthropic
import json

from backend.models.generative_agent import GenerativeAgent


class PredictionEngine:
    """Engine for predicting survey responses"""

    def __init__(self, llm_client: Anthropic):
        self.llm = llm_client
        self._cache = {}

    def predict_responses(
        self,
        agents: List[GenerativeAgent],
        questions: List[Dict]
    ) -> Dict:
        """Predict how agents would respond to survey questions"""

        predictions = []

        for i, question in enumerate(questions):
            cache_key = self._make_cache_key(question, len(agents))
            if cache_key in self._cache:
                predictions.append(self._cache[cache_key])
                continue

            prediction = self._predict_single_question(agents, question)
            predictions.append(prediction)

            self._cache[cache_key] = prediction

        confidences = [p.get("confidence", 0.5) for p in predictions]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        return {
            "overall_confidence": self._classify_confidence(overall_confidence),
            "predictions": predictions
        }

    def _predict_single_question(
        self,
        agents: List[GenerativeAgent],
        question: Dict
    ) -> Dict:
        """Predict responses for a single question"""

        question_type = question.get("type", "single_choice")
        question_text = question.get("text", "")
        options = question.get("options", [])

        if question_type == "single_choice":
            return self._predict_single_choice(agents, question_text, options)
        elif question_type == "rating_scale":
            return self._predict_rating_scale(agents, question_text, question.get("scale", 5))
        elif question_type == "open_text":
            return self._predict_open_text(agents, question_text)
        else:
            return {"error": "Unknown question type"}

    def _predict_single_choice(
        self,
        agents: List[GenerativeAgent],
        question: str,
        options: List[str]
    ) -> Dict:
        """Predict single choice responses"""

        sample_size = min(50, len(agents))
        sample_agents = agents[:sample_size]

        segment_summary = self._summarize_segments(sample_agents)

        prompt = f"""Given this audience:
{segment_summary}

Predict how they would answer this survey question:
"{question}"

Options:
{chr(10).join([f"- {opt}" for opt in options])}

Provide predicted distribution as percentages that sum to 100.
Format as JSON: {{"option1": percent, "option2": percent, ...}}

Base your prediction on:
1. The audience's demographics and psychographics
2. Typical response patterns for similar audiences
3. The specific wording and framing of options"""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            text = response.content[0].text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                distribution = json.loads(text[start:end])
            else:
                distribution = {opt: 100/len(options) for opt in options}
        except:
            distribution = {opt: 100/len(options) for opt in options}

        # Normalize
        total = sum(distribution.values())
        if total > 0:
            distribution = {k: v/total for k, v in distribution.items()}

        return {
            "question": question,
            "type": "single_choice",
            "distribution": distribution,
            "confidence": self._estimate_confidence(sample_agents, question)
        }

    def _predict_rating_scale(
        self,
        agents: List[GenerativeAgent],
        question: str,
        scale: int
    ) -> Dict:
        """Predict rating scale responses"""

        segment_summary = self._summarize_segments(agents[:50])

        prompt = f"""Given this audience:
{segment_summary}

Predict how they would answer this rating question:
"{question}"

Scale: 1 to {scale} (1 = lowest/worst, {scale} = highest/best)

Provide:
1. Mean rating (to 1 decimal)
2. Distribution shape (normal, skewed_positive, skewed_negative, bimodal)
3. Standard deviation estimate

Format as JSON: {{"mean": X.X, "distribution": "shape", "std": X.X}}"""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            text = response.content[0].text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                result = json.loads(text[start:end])
            else:
                result = {"mean": scale/2, "distribution": "normal", "std": 1.0}
        except:
            result = {"mean": scale/2, "distribution": "normal", "std": 1.0}

        return {
            "question": question,
            "type": "rating_scale",
            "mean": result.get("mean", scale/2),
            "distribution_shape": result.get("distribution", "normal"),
            "std": result.get("std", 1.0),
            "scale": scale,
            "confidence": self._estimate_confidence(agents[:50], question)
        }

    def _predict_open_text(
        self,
        agents: List[GenerativeAgent],
        question: str
    ) -> Dict:
        """Predict themes in open text responses"""

        segment_summary = self._summarize_segments(agents[:50])

        prompt = f"""Given this audience:
{segment_summary}

If asked: "{question}"

What would be the 3-5 most common themes in their open-text responses?
For each theme, estimate what percentage would mention it.

Format as JSON: {{"themes": [{{"theme": "...", "percent": X}}, ...]}}"""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            text = response.content[0].text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                result = json.loads(text[start:end])
            else:
                result = {"themes": []}
        except:
            result = {"themes": []}

        return {
            "question": question,
            "type": "open_text",
            "themes": result.get("themes", []),
            "confidence": "low"
        }

    def _summarize_segments(self, agents: List[GenerativeAgent]) -> str:
        """Summarize agent segments for LLM context"""

        segments = {}
        for agent in agents:
            seg = agent.segment_id
            if seg not in segments:
                segments[seg] = {
                    "count": 0,
                    "avg_price_sensitivity": 0,
                    "avg_brand_loyalty": 0,
                    "occupations": []
                }
            segments[seg]["count"] += 1
            segments[seg]["avg_price_sensitivity"] += agent.price_sensitivity
            segments[seg]["avg_brand_loyalty"] += agent.brand_loyalty
            if agent.occupation not in segments[seg]["occupations"]:
                segments[seg]["occupations"].append(agent.occupation)

        summary_parts = []
        for seg, data in segments.items():
            count = data["count"]
            if count > 0:
                data["avg_price_sensitivity"] /= count
                data["avg_brand_loyalty"] /= count
            summary_parts.append(
                f"- {seg} ({count} people): "
                f"Price sensitivity {data['avg_price_sensitivity']:.1f}, "
                f"Brand loyalty {data['avg_brand_loyalty']:.1f}, "
                f"Occupations include: {', '.join(data['occupations'][:3])}"
            )

        return chr(10).join(summary_parts)

    def _estimate_confidence(self, agents: List[GenerativeAgent], question: str) -> str:
        """Estimate prediction confidence"""

        if len(agents) < 20:
            return "low"
        elif len(agents) < 100:
            return "medium"
        else:
            return "high"

    def _classify_confidence(self, score: float) -> str:
        """Classify confidence score"""
        if score > 0.7:
            return "high"
        elif score > 0.4:
            return "medium"
        else:
            return "low"

    def _make_cache_key(self, question: Dict, agent_count: int) -> str:
        """Create cache key for prediction"""
        return f"{question.get('text', '')}_{question.get('type', '')}_{agent_count}"
