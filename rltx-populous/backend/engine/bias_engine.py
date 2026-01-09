"""
Bias Detection Engine
Detects and suggests fixes for biased survey questions
"""

from typing import List, Dict, Optional
from anthropic import Anthropic
import re


class BiasEngine:
    """Engine for detecting bias in survey questions"""

    def __init__(self, llm_client: Anthropic = None):
        self.llm = llm_client

        # Common bias patterns
        self.leading_phrases = [
            "don't you agree",
            "wouldn't you say",
            "isn't it true",
            "surely you",
            "obviously",
            "clearly",
            "everyone knows"
        ]

        self.loaded_words = [
            "best", "worst", "amazing", "terrible",
            "love", "hate", "perfect", "awful",
            "must", "should", "always", "never"
        ]

    def check_bias(self, question: str, options: List[str] = None) -> Dict:
        """Check a question for potential bias"""

        if options is None:
            options = []

        issues = []

        question_lower = question.lower()

        # Check for leading phrases
        for phrase in self.leading_phrases:
            if phrase in question_lower:
                issues.append({
                    "type": "leading",
                    "description": f"Leading phrase detected: '{phrase}'",
                    "severity": "high"
                })

        # Check for loaded words
        for word in self.loaded_words:
            if re.search(r'\b' + word + r'\b', question_lower):
                issues.append({
                    "type": "loaded_language",
                    "description": f"Loaded word detected: '{word}'",
                    "severity": "medium"
                })

        # Check for double-barreled questions
        if " and " in question_lower and "?" in question:
            issues.append({
                "type": "double_barreled",
                "description": "Question may be asking two things at once",
                "severity": "medium"
            })

        # Check for missing neutral option
        if options:
            has_neutral = any(
                opt.lower() in ["neutral", "neither", "no opinion", "not sure", "n/a"]
                for opt in options
            )
            if not has_neutral and len(options) > 2:
                issues.append({
                    "type": "missing_neutral",
                    "description": "Consider adding a neutral option",
                    "severity": "low"
                })

        # If rule-based found nothing, do LLM check
        if not issues and self.llm:
            llm_check = self._llm_bias_check(question, options)
            if llm_check.get("has_bias"):
                issues.append({
                    "type": llm_check.get("bias_type", "subtle"),
                    "description": llm_check.get("explanation", "Potential subtle bias"),
                    "severity": "medium"
                })

        # Generate suggestion if issues found
        suggestion = None
        if issues:
            suggestion = self._generate_suggestion(question, issues)

        return {
            "has_bias": len(issues) > 0,
            "issues": issues,
            "suggestion": suggestion
        }

    def _llm_bias_check(self, question: str, options: List[str]) -> Dict:
        """Use LLM to check for subtle bias"""

        if not self.llm:
            return {"has_bias": False}

        prompt = f"""Analyze this survey question for potential bias:

Question: "{question}"
{f"Options: {options}" if options else ""}

Check for:
1. Leading language that suggests a "correct" answer
2. Loaded or emotionally charged words
3. Assumptions embedded in the question
4. Social desirability bias triggers
5. Framing effects

If there is bias, explain it briefly.
If there is no bias, say "No bias detected."

Format: BIAS: [yes/no] | TYPE: [type] | EXPLANATION: [brief explanation]"""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text.lower()

        if "bias: yes" in text or "bias detected" in text:
            bias_type = "subtle"
            explanation = text

            if "type:" in text:
                type_start = text.find("type:") + 5
                type_end = text.find("|", type_start) if "|" in text[type_start:] else len(text)
                bias_type = text[type_start:type_end].strip()

            if "explanation:" in text:
                exp_start = text.find("explanation:") + 12
                explanation = text[exp_start:].strip()

            return {
                "has_bias": True,
                "bias_type": bias_type,
                "explanation": explanation
            }

        return {"has_bias": False}

    def _generate_suggestion(self, question: str, issues: List[Dict]) -> str:
        """Generate improved question suggestion"""

        if not self.llm:
            return self._generate_simple_suggestion(question, issues)

        issue_descriptions = [i["description"] for i in issues]

        prompt = f"""Rewrite this survey question to remove bias.

Original question: "{question}"

Issues found:
{chr(10).join(['- ' + d for d in issue_descriptions])}

Provide a neutral, unbiased version that:
1. Removes leading language
2. Uses neutral wording
3. Doesn't suggest a preferred answer
4. Is clear and easy to understand

Return only the improved question, nothing else."""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text.strip().strip('"')

    def _generate_simple_suggestion(self, question: str, issues: List[Dict]) -> str:
        """Generate suggestion without LLM"""

        suggestion = question

        # Remove leading phrases
        for phrase in self.leading_phrases:
            suggestion = re.sub(r'\b' + phrase + r'\b', '', suggestion, flags=re.IGNORECASE)

        # Remove loaded words where possible
        for word in self.loaded_words:
            if word in ["best", "worst"]:
                suggestion = re.sub(r'\b' + word + r'\b', '', suggestion, flags=re.IGNORECASE)

        suggestion = re.sub(r'\s+', ' ', suggestion).strip()

        if suggestion == question:
            return "Consider rephrasing to remove bias."

        return suggestion

    def suggest_questions(
        self,
        survey_purpose: str,
        existing_questions: List[str],
        audience_description: str
    ) -> List[Dict]:
        """Suggest additional questions for the survey"""

        if not self.llm:
            return []

        prompt = f"""You are helping design a survey.

Purpose: {survey_purpose}
Target audience: {audience_description}

Existing questions:
{chr(10).join(['- ' + q for q in existing_questions]) if existing_questions else '(none yet)'}

Suggest 2-3 additional questions that would provide valuable insights.
For each suggestion, explain why it would be useful.

Format each as:
QUESTION: [the question]
TYPE: [single_choice/rating_scale/open_text]
RATIONALE: [why this helps]
OPTIONS: [if applicable, suggested options]"""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )

        suggestions = []
        text = response.content[0].text

        parts = text.split("QUESTION:")

        for part in parts[1:]:
            lines = part.strip().split("\n")
            question = lines[0].strip() if lines else ""

            question_type = "single_choice"
            rationale = ""
            options = []

            for line in lines[1:]:
                if line.startswith("TYPE:"):
                    question_type = line.replace("TYPE:", "").strip().lower()
                elif line.startswith("RATIONALE:"):
                    rationale = line.replace("RATIONALE:", "").strip()
                elif line.startswith("OPTIONS:"):
                    opts = line.replace("OPTIONS:", "").strip()
                    options = [o.strip() for o in opts.split(",")]

            if question:
                suggestions.append({
                    "question": question,
                    "type": question_type,
                    "rationale": rationale,
                    "options": options
                })

        return suggestions
