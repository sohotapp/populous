"""
Confidence Decomposition Engine
Breaks down prediction confidence into interpretable components
"Why is this prediction 73% confident? What would make it 90%?"
"""

import os
import numpy as np
from typing import List, Dict, Optional, Any
from datetime import datetime
from anthropic import Anthropic

from backend.models.confidence import (
    ConfidenceDecomposition, UncertaintyComponent, ConfidenceLevel,
    UncertaintySource, SensitivityAnalysis, DataQualityAssessment,
    ConfidenceReport
)
from backend.models.scenario_branch import ScenarioTree, ScenarioMetrics
from backend.models.company import ResearchResult


class ConfidenceEngine:
    """
    Engine for decomposing and explaining prediction confidence.
    Makes AI confidence interpretable and actionable.
    """

    def __init__(self, llm_client: Anthropic = None):
        self.llm = llm_client or Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Base uncertainty weights by source
        self.base_weights = {
            UncertaintySource.DATA_QUALITY: 0.15,
            UncertaintySource.MODEL_ACCURACY: 0.10,
            UncertaintySource.MARKET_VOLATILITY: 0.20,
            UncertaintySource.COMPETITOR_BEHAVIOR: 0.20,
            UncertaintySource.CUSTOMER_RESPONSE: 0.15,
            UncertaintySource.EXECUTION_RISK: 0.10,
            UncertaintySource.TEMPORAL_DECAY: 0.05,
            UncertaintySource.ASSUMPTION_SENSITIVITY: 0.05,
        }

    def decompose_confidence(
        self,
        prediction: Dict[str, Any],
        scenario_tree: Optional[ScenarioTree] = None,
        research_result: Optional[ResearchResult] = None,
        time_horizon_days: int = 90
    ) -> ConfidenceDecomposition:
        """
        Decompose a prediction's confidence into component uncertainties.
        """
        components = []

        # 1. Data Quality Uncertainty
        data_quality = self._assess_data_quality(research_result)
        components.append(UncertaintyComponent(
            source=UncertaintySource.DATA_QUALITY,
            name="Data Quality",
            description="Uncertainty from incomplete or stale data",
            contribution=self._calculate_data_uncertainty(data_quality),
            reducible=True,
            reduction_actions=[
                "Gather more recent competitor data",
                "Verify market size estimates",
                "Update customer feedback data"
            ],
            reduction_potential=0.4,
            evidence_strength="moderate" if data_quality.reliability_score > 0.7 else "weak",
            data_sources=research_result.sources[:3] if research_result else []
        ))

        # 2. Model Accuracy Uncertainty
        model_uncertainty = self._estimate_model_uncertainty(prediction)
        components.append(UncertaintyComponent(
            source=UncertaintySource.MODEL_ACCURACY,
            name="Model Limitations",
            description="Inherent limitations of prediction models",
            contribution=model_uncertainty,
            reducible=False,
            reduction_actions=[
                "This uncertainty is inherent to forecasting",
                "Cross-validate with historical data"
            ],
            reduction_potential=0.1,
            evidence_strength="moderate"
        ))

        # 3. Market Volatility
        market_volatility = self._estimate_market_volatility(research_result)
        components.append(UncertaintyComponent(
            source=UncertaintySource.MARKET_VOLATILITY,
            name="Market Volatility",
            description="External market factors and macroeconomic conditions",
            contribution=market_volatility,
            reducible=False,
            reduction_actions=[
                "Monitor macroeconomic indicators",
                "Prepare contingency plans for market shifts"
            ],
            reduction_potential=0.0,
            impact_if_wrong="high"
        ))

        # 4. Competitor Behavior
        competitor_uncertainty = self._estimate_competitor_uncertainty(
            scenario_tree, research_result
        )
        components.append(UncertaintyComponent(
            source=UncertaintySource.COMPETITOR_BEHAVIOR,
            name="Competitor Response",
            description="Uncertainty in how competitors will react",
            contribution=competitor_uncertainty,
            reducible=True,
            reduction_actions=[
                "Gather more competitive intelligence",
                "Analyze competitor historical responses",
                "Monitor competitor announcements closely"
            ],
            reduction_potential=0.3,
            impact_if_wrong="high"
        ))

        # 5. Customer Response
        customer_uncertainty = self._estimate_customer_uncertainty(prediction)
        components.append(UncertaintyComponent(
            source=UncertaintySource.CUSTOMER_RESPONSE,
            name="Customer Behavior",
            description="How customers will react to changes",
            contribution=customer_uncertainty,
            reducible=True,
            reduction_actions=[
                "Run customer surveys",
                "A/B test with segment",
                "Analyze historical customer response patterns"
            ],
            reduction_potential=0.5,
            impact_if_wrong="moderate"
        ))

        # 6. Execution Risk
        execution_risk = self._estimate_execution_risk(prediction)
        components.append(UncertaintyComponent(
            source=UncertaintySource.EXECUTION_RISK,
            name="Execution Risk",
            description="Risk that implementation differs from plan",
            contribution=execution_risk,
            reducible=True,
            reduction_actions=[
                "Define clear success metrics",
                "Create detailed implementation plan",
                "Assign accountability"
            ],
            reduction_potential=0.6,
            impact_if_wrong="moderate"
        ))

        # 7. Temporal Decay
        temporal_decay = self._calculate_temporal_decay(time_horizon_days)
        components.append(UncertaintyComponent(
            source=UncertaintySource.TEMPORAL_DECAY,
            name="Time Horizon",
            description="Predictions become less certain over time",
            contribution=temporal_decay,
            reducible=False,
            reduction_actions=[
                "Shorten planning horizon",
                "Build in review checkpoints"
            ],
            reduction_potential=0.0,
            evidence_strength="strong"
        ))

        # 8. Assumption Sensitivity
        assumption_sensitivity = self._assess_assumptions(prediction)
        components.append(UncertaintyComponent(
            source=UncertaintySource.ASSUMPTION_SENSITIVITY,
            name="Key Assumptions",
            description="Sensitivity to underlying assumptions",
            contribution=assumption_sensitivity,
            reducible=True,
            reduction_actions=[
                "Validate key assumptions with data",
                "Test sensitivity of major assumptions"
            ],
            reduction_potential=0.4
        ))

        # Normalize contributions
        total_contribution = sum(c.contribution for c in components)
        if total_contribution > 0:
            for c in components:
                c.contribution = c.contribution / total_contribution
                c.variance_explained = c.contribution

        # Calculate overall confidence
        total_uncertainty = sum(c.contribution * self.base_weights[c.source]
                               for c in components)
        overall_confidence = max(0.1, min(0.95, 1 - total_uncertainty))

        # Determine confidence level
        confidence_level = self._to_confidence_level(overall_confidence)

        # Find primary uncertainty and most reducible
        sorted_by_contribution = sorted(components, key=lambda c: c.contribution, reverse=True)
        reducible_sorted = sorted(
            [c for c in components if c.reducible],
            key=lambda c: c.reduction_potential * c.contribution,
            reverse=True
        )

        # Generate improvement actions
        improvement_actions = []
        for c in reducible_sorted[:3]:
            improvement_actions.extend(c.reduction_actions[:1])

        return ConfidenceDecomposition(
            prediction_id=prediction.get("id", ""),
            overall_confidence=round(overall_confidence, 2),
            confidence_level=confidence_level,
            confidence_interval=(
                round(overall_confidence - 0.1, 2),
                round(min(0.95, overall_confidence + 0.1), 2)
            ),
            components=components,
            primary_uncertainty=sorted_by_contribution[0].name if sorted_by_contribution else "",
            most_reducible=reducible_sorted[0].name if reducible_sorted else "",
            critical_assumptions=self._extract_assumptions(prediction),
            confidence_improvement_actions=improvement_actions,
            breakdown_chart_data=self._prepare_chart_data(components)
        )

    def _assess_data_quality(
        self,
        research_result: Optional[ResearchResult]
    ) -> DataQualityAssessment:
        """Assess quality of input data."""
        if not research_result:
            return DataQualityAssessment(
                source="none",
                freshness_days=365,
                completeness=0.3,
                accuracy_estimate=0.5,
                reliability_score=0.4,
                issues=["No research data available"],
                recommendations=["Conduct company research"]
            )

        # Check freshness
        days_old = (datetime.now() - research_result.created_at).days if research_result.created_at else 30

        # Check completeness based on available data
        completeness_factors = [
            research_result.target_company is not None,
            len(research_result.competitors) > 0,
            research_result.market is not None,
            len(research_result.sources) > 3
        ]
        completeness = sum(completeness_factors) / len(completeness_factors)

        issues = []
        recommendations = []

        if days_old > 30:
            issues.append(f"Data is {days_old} days old")
            recommendations.append("Refresh research data")

        if len(research_result.competitors) < 3:
            issues.append("Limited competitor data")
            recommendations.append("Research additional competitors")

        return DataQualityAssessment(
            source="research_engine",
            freshness_days=days_old,
            completeness=completeness,
            accuracy_estimate=0.7 if len(research_result.sources) > 5 else 0.5,
            reliability_score=max(0.3, 1 - (days_old / 365) - (1 - completeness) * 0.3),
            issues=issues,
            recommendations=recommendations
        )

    def _calculate_data_uncertainty(self, assessment: DataQualityAssessment) -> float:
        """Calculate uncertainty contribution from data quality."""
        # Lower quality = higher uncertainty
        base = 1 - assessment.reliability_score

        # Adjust for freshness
        freshness_factor = min(1.0, assessment.freshness_days / 180)

        # Adjust for completeness
        completeness_factor = 1 - assessment.completeness

        return (base * 0.4 + freshness_factor * 0.3 + completeness_factor * 0.3)

    def _estimate_model_uncertainty(self, prediction: Dict) -> float:
        """Estimate inherent model uncertainty."""
        # Base model uncertainty
        base = 0.15

        # Increase for complex predictions
        if prediction.get("type") in ["market_share", "competitive_response"]:
            base += 0.1

        return base

    def _estimate_market_volatility(
        self,
        research_result: Optional[ResearchResult]
    ) -> float:
        """Estimate market volatility uncertainty."""
        if not research_result or not research_result.market:
            return 0.25  # Default moderate volatility

        market = research_result.market
        volatility = 0.15  # Base

        # Adjust based on market characteristics
        growth_rate = market.growth_rate or 0.1
        if growth_rate > 0.2:  # High growth market
            volatility += 0.15  # More volatile

        # More competitors = more volatile
        if len(research_result.competitors) > 5:
            volatility += 0.1

        return min(0.4, volatility)

    def _estimate_competitor_uncertainty(
        self,
        scenario_tree: Optional[ScenarioTree],
        research_result: Optional[ResearchResult]
    ) -> float:
        """Estimate uncertainty from competitor behavior."""
        base = 0.2

        if scenario_tree:
            # More divergent scenarios = more uncertainty
            outcome_probs = scenario_tree.outcome_probabilities
            if outcome_probs:
                # Calculate entropy as measure of uncertainty
                probs = list(outcome_probs.values())
                entropy = -sum(p * np.log(p + 1e-10) for p in probs if p > 0)
                normalized_entropy = entropy / np.log(len(probs) + 1e-10)
                base = 0.1 + normalized_entropy * 0.3

        if research_result:
            # More competitors = more uncertainty
            n_competitors = len(research_result.competitors)
            base *= (1 + n_competitors * 0.05)

        return min(0.5, base)

    def _estimate_customer_uncertainty(self, prediction: Dict) -> float:
        """Estimate uncertainty from customer behavior."""
        base = 0.15

        # Price-related predictions have higher customer uncertainty
        if prediction.get("type") == "price_change":
            percent = abs(prediction.get("percent", 0))
            base += percent * 0.01  # More extreme changes = more uncertainty

        return min(0.35, base)

    def _estimate_execution_risk(self, prediction: Dict) -> float:
        """Estimate execution risk uncertainty."""
        base = 0.1

        # Complex moves have higher execution risk
        complexity_factors = [
            prediction.get("requires_engineering", False),
            prediction.get("requires_marketing", False),
            prediction.get("requires_sales", False),
            prediction.get("cross_functional", False)
        ]

        base += sum(complexity_factors) * 0.05

        return min(0.3, base)

    def _calculate_temporal_decay(self, days: int) -> float:
        """Calculate uncertainty increase over time horizon."""
        # Exponential decay of confidence
        decay_rate = 0.01  # ~1% uncertainty increase per month
        return min(0.4, 1 - np.exp(-decay_rate * days / 30))

    def _assess_assumptions(self, prediction: Dict) -> float:
        """Assess sensitivity to key assumptions."""
        # Count explicit assumptions
        assumptions = prediction.get("assumptions", [])

        if len(assumptions) == 0:
            return 0.15  # Hidden assumptions are risky

        # More explicit assumptions = lower uncertainty
        return max(0.05, 0.2 - len(assumptions) * 0.02)

    def _extract_assumptions(self, prediction: Dict) -> List[str]:
        """Extract key assumptions from prediction."""
        assumptions = prediction.get("assumptions", [])

        if not assumptions:
            # Default assumptions
            assumptions = [
                "Market conditions remain stable",
                "No major competitor announcements",
                "Implementation proceeds as planned",
                "Customer behavior follows historical patterns"
            ]

        return assumptions[:5]

    def _to_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert numeric confidence to level."""
        if confidence >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 0.75:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.5:
            return ConfidenceLevel.MODERATE
        elif confidence >= 0.25:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def _prepare_chart_data(self, components: List[UncertaintyComponent]) -> Dict:
        """Prepare data for visualization."""
        return {
            "breakdown": [
                {
                    "name": c.name,
                    "source": c.source.value,
                    "contribution": round(c.contribution, 3),
                    "reducible": c.reducible,
                    "reduction_potential": c.reduction_potential
                }
                for c in sorted(components, key=lambda x: x.contribution, reverse=True)
            ],
            "reducible_total": sum(c.contribution for c in components if c.reducible),
            "irreducible_total": sum(c.contribution for c in components if not c.reducible)
        }

    def run_sensitivity_analysis(
        self,
        prediction: Dict,
        variables: List[str],
        variation_range: float = 0.2
    ) -> SensitivityAnalysis:
        """
        Analyze how sensitive the prediction is to key variables.
        """
        sensitivities = {}

        for variable in variables:
            base_value = prediction.get(variable, 0)

            # Test +/- variation
            low_value = base_value * (1 - variation_range)
            high_value = base_value * (1 + variation_range)

            # Estimate impact (simplified - would use actual model in production)
            impact = self._estimate_variable_impact(variable, variation_range)

            sensitivities[variable] = {
                "base_value": base_value,
                "test_range": (low_value, high_value),
                "impact_score": impact,
                "impact_direction": "proportional" if impact > 0 else "inverse",
                "elasticity": abs(impact / variation_range) if variation_range > 0 else 0
            }

        # Rank by impact
        ranked = sorted(sensitivities.items(), key=lambda x: abs(x[1]["impact_score"]), reverse=True)

        return SensitivityAnalysis(
            prediction_id=prediction.get("id", ""),
            variables_tested=variables,
            sensitivities=sensitivities,
            most_sensitive_to=[v[0] for v in ranked[:3]],
            least_sensitive_to=[v[0] for v in ranked[-3:]],
            variables_to_monitor=[v[0] for v in ranked[:5]],
            robustness_score=1 - np.mean([abs(s["impact_score"]) for s in sensitivities.values()])
        )

    def _estimate_variable_impact(self, variable: str, variation: float) -> float:
        """Estimate impact of variable variation on prediction."""
        # Simplified impact estimation
        high_impact_vars = ["price", "market_share", "competitor_response", "churn_rate"]
        medium_impact_vars = ["marketing_spend", "feature_adoption", "sales_cycle"]

        if any(v in variable.lower() for v in high_impact_vars):
            return variation * 0.8
        elif any(v in variable.lower() for v in medium_impact_vars):
            return variation * 0.4
        else:
            return variation * 0.2

    def generate_confidence_report(
        self,
        decomposition: ConfidenceDecomposition,
        prediction_summary: str
    ) -> ConfidenceReport:
        """
        Generate a human-readable confidence report.
        """
        confidence = decomposition.overall_confidence
        level = decomposition.confidence_level

        # Generate headline
        headline = f"{level.value.replace('_', ' ').title()} confidence ({int(confidence * 100)}%)"

        # Plain English explanation
        if level == ConfidenceLevel.VERY_HIGH:
            plain_english = "This prediction is highly reliable based on strong evidence and low uncertainty."
        elif level == ConfidenceLevel.HIGH:
            plain_english = "This prediction is well-supported with manageable uncertainty."
        elif level == ConfidenceLevel.MODERATE:
            plain_english = "This prediction has reasonable support but significant uncertainties remain."
        elif level == ConfidenceLevel.LOW:
            plain_english = "This prediction has substantial uncertainty and should be treated as directional."
        else:
            plain_english = "This prediction has very high uncertainty. Consider gathering more data."

        # Format main uncertainties
        main_uncertainties = [
            {
                "name": c.name,
                "contribution": f"{int(c.contribution * 100)}%",
                "can_reduce": c.reducible,
                "how_to_reduce": c.reduction_actions[0] if c.reduction_actions else None
            }
            for c in sorted(decomposition.components, key=lambda x: x.contribution, reverse=True)[:3]
        ]

        # Actions to increase confidence
        to_increase = []
        reducible = [c for c in decomposition.components if c.reducible]
        for c in sorted(reducible, key=lambda x: x.reduction_potential * x.contribution, reverse=True)[:3]:
            if c.reduction_actions:
                to_increase.append(c.reduction_actions[0])

        # Risk mitigation
        to_reduce_risk = [
            "Set clear success/failure criteria before execution",
            "Plan checkpoint reviews at key milestones",
            "Prepare contingency plans for worst-case scenarios"
        ]

        return ConfidenceReport(
            prediction_summary=prediction_summary,
            headline=headline,
            plain_english=plain_english,
            confidence_value=confidence,
            confidence_level=level,
            main_uncertainties=main_uncertainties,
            to_increase_confidence=to_increase,
            to_reduce_risk=to_reduce_risk,
            key_assumptions=decomposition.critical_assumptions,
            what_could_change=[
                f"If {decomposition.primary_uncertainty.lower()} changes significantly",
                "Market conditions shift unexpectedly",
                "Competitor makes unexpected move"
            ]
        )
