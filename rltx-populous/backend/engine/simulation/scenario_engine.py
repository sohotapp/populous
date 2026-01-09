"""
Scenario Simulation Engine

This is what makes enterprises pay $5-10M:
The ability to run "what-if" scenarios and see how decisions change.

Key Capabilities:
1. Adjust any input parameter and see cascading effects
2. Compare multiple scenarios side-by-side
3. Run sensitivity analysis on any variable
4. Monte Carlo simulation with custom distributions
5. Stress testing with correlated shocks
"""

from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from enum import Enum
import numpy as np
from datetime import datetime
import copy


class ScenarioType(str, Enum):
    BASE_CASE = "base_case"
    BULL_CASE = "bull_case"
    BEAR_CASE = "bear_case"
    STRESS_TEST = "stress_test"
    CUSTOM = "custom"


class ParameterAdjustment(BaseModel):
    """A single parameter adjustment in a scenario"""
    parameter_path: str  # e.g., "team_score", "market.tam", "funding.last_round_amount"
    adjustment_type: str  # "absolute", "percentage", "override"
    adjustment_value: float
    rationale: str = ""


class Scenario(BaseModel):
    """A complete scenario definition"""
    scenario_id: str = Field(default_factory=lambda: f"sc_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    scenario_name: str
    scenario_type: ScenarioType
    description: str

    # Adjustments
    adjustments: List[ParameterAdjustment] = []

    # Results (populated after simulation)
    base_probability: Optional[float] = None
    adjusted_probability: Optional[float] = None
    probability_delta: Optional[float] = None

    base_valuation: Optional[float] = None
    adjusted_valuation: Optional[float] = None
    valuation_delta: Optional[float] = None

    # Factor score changes
    factor_deltas: Dict[str, float] = {}

    # Recommendation change
    base_recommendation: Optional[str] = None
    adjusted_recommendation: Optional[str] = None
    recommendation_changed: bool = False

    # Narrative
    impact_summary: str = ""


class SensitivityResult(BaseModel):
    """Result of sensitivity analysis on a single parameter"""
    parameter: str
    parameter_display_name: str

    # Range tested
    min_value: float
    max_value: float
    base_value: float

    # Impact on outcome
    min_probability: float
    max_probability: float
    base_probability: float

    # Elasticity (% change in output / % change in input)
    elasticity: float

    # Data points for charting
    values: List[float]
    probabilities: List[float]

    # Inflection points
    inflection_points: List[Dict[str, float]] = []


class MonteCarloResult(BaseModel):
    """Result of Monte Carlo simulation"""
    simulations: int
    seed: Optional[int] = None

    # Distribution summary
    mean_probability: float
    median_probability: float
    std_dev: float

    # Percentiles
    p5: float
    p10: float
    p25: float
    p50: float
    p75: float
    p90: float
    p95: float

    # Confidence intervals
    ci_90: Tuple[float, float]
    ci_95: Tuple[float, float]
    ci_99: Tuple[float, float]

    # Distribution shape
    skewness: float
    kurtosis: float

    # Scenario probabilities
    prob_unicorn: float  # P(valuation > $1B)
    prob_centaur: float  # P(valuation > $100M)
    prob_success: float  # P(exit > investment)
    prob_failure: float  # P(failure)

    # Raw data for charting
    distribution: List[float] = []
    histogram_bins: List[float] = []
    histogram_counts: List[int] = []


class StressTestResult(BaseModel):
    """Result of stress testing"""
    scenario_name: str
    description: str

    # Shocked parameters
    shocks: List[Dict[str, Any]]

    # Impact
    base_probability: float
    stressed_probability: float
    probability_drop: float
    probability_drop_pct: float

    # Survival analysis
    survives_scenario: bool
    recovery_time_estimate: Optional[str] = None

    # Risk rating
    vulnerability_rating: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"


class ScenarioEngine:
    """
    Enterprise simulation engine for decision intelligence.

    This is the differentiator that makes F500 companies pay millions:
    - Run unlimited what-if scenarios
    - See exactly how each assumption affects the outcome
    - Stress test against market downturns
    - Quantify uncertainty with Monte Carlo
    """

    def __init__(self, base_prediction: Dict[str, Any], company_data: Dict[str, Any]):
        """
        Initialize with a base prediction and company data.

        Args:
            base_prediction: The current prediction state
            company_data: Raw company data for recalculation
        """
        self.base_prediction = copy.deepcopy(base_prediction)
        self.company_data = copy.deepcopy(company_data)

        # Cache base values
        self._base_probability = base_prediction.get("unicorn_probability", 0)
        self._base_valuation = base_prediction.get("expected_valuation", 0)
        self._base_factors = {
            "team_score": base_prediction.get("team_score", 0.5),
            "market_score": base_prediction.get("market_score", 0.5),
            "traction_score": base_prediction.get("traction_score", 0.5),
            "timing_score": base_prediction.get("timing_score", 0.5),
            "capital_score": base_prediction.get("capital_score", 0.5),
        }

    def run_scenario(self, scenario: Scenario) -> Scenario:
        """
        Run a single scenario and compute its impact.
        """
        # Apply adjustments
        adjusted_factors = copy.deepcopy(self._base_factors)

        for adj in scenario.adjustments:
            param = adj.parameter_path

            if param in adjusted_factors:
                if adj.adjustment_type == "absolute":
                    adjusted_factors[param] = adj.adjustment_value
                elif adj.adjustment_type == "percentage":
                    adjusted_factors[param] *= (1 + adj.adjustment_value / 100)
                elif adj.adjustment_type == "override":
                    adjusted_factors[param] = adj.adjustment_value

                # Clamp to 0-1
                adjusted_factors[param] = max(0, min(1, adjusted_factors[param]))

        # Recalculate probability with adjusted factors
        adjusted_probability = self._calculate_probability(adjusted_factors)
        adjusted_valuation = self._calculate_valuation(adjusted_factors, adjusted_probability)

        # Populate results
        scenario.base_probability = self._base_probability
        scenario.adjusted_probability = adjusted_probability
        scenario.probability_delta = adjusted_probability - self._base_probability

        scenario.base_valuation = self._base_valuation
        scenario.adjusted_valuation = adjusted_valuation
        scenario.valuation_delta = adjusted_valuation - self._base_valuation

        # Factor deltas
        scenario.factor_deltas = {
            k: adjusted_factors[k] - self._base_factors[k]
            for k in self._base_factors
        }

        # Recommendations
        scenario.base_recommendation = self._get_recommendation(self._base_probability)
        scenario.adjusted_recommendation = self._get_recommendation(adjusted_probability)
        scenario.recommendation_changed = (
            scenario.base_recommendation != scenario.adjusted_recommendation
        )

        # Generate impact summary
        scenario.impact_summary = self._generate_impact_summary(scenario)

        return scenario

    def run_sensitivity_analysis(
        self,
        parameter: str,
        min_value: float = 0.0,
        max_value: float = 1.0,
        steps: int = 20
    ) -> SensitivityResult:
        """
        Run sensitivity analysis on a single parameter.

        Shows how changes in one input affect the output.
        """
        values = np.linspace(min_value, max_value, steps).tolist()
        probabilities = []

        for val in values:
            adjusted_factors = copy.deepcopy(self._base_factors)
            adjusted_factors[parameter] = val
            prob = self._calculate_probability(adjusted_factors)
            probabilities.append(prob)

        # Calculate elasticity at base point
        base_idx = int(steps / 2)
        if base_idx > 0 and base_idx < len(values) - 1:
            delta_x = (values[base_idx + 1] - values[base_idx - 1]) / self._base_factors.get(parameter, 0.5)
            delta_y = (probabilities[base_idx + 1] - probabilities[base_idx - 1]) / self._base_probability if self._base_probability > 0 else 0
            elasticity = delta_y / delta_x if delta_x != 0 else 0
        else:
            elasticity = 0

        # Find inflection points (where second derivative changes sign)
        inflection_points = []
        if len(probabilities) >= 3:
            second_deriv = np.diff(np.diff(probabilities))
            for i in range(len(second_deriv) - 1):
                if second_deriv[i] * second_deriv[i + 1] < 0:
                    inflection_points.append({
                        "value": values[i + 1],
                        "probability": probabilities[i + 1]
                    })

        return SensitivityResult(
            parameter=parameter,
            parameter_display_name=parameter.replace("_", " ").title(),
            min_value=min_value,
            max_value=max_value,
            base_value=self._base_factors.get(parameter, 0.5),
            min_probability=min(probabilities),
            max_probability=max(probabilities),
            base_probability=self._base_probability,
            elasticity=elasticity,
            values=values,
            probabilities=probabilities,
            inflection_points=inflection_points
        )

    def run_monte_carlo(
        self,
        simulations: int = 10000,
        factor_uncertainty: Dict[str, Tuple[float, float]] = None,
        seed: Optional[int] = None
    ) -> MonteCarloResult:
        """
        Run Monte Carlo simulation with uncertainty distributions.

        Args:
            simulations: Number of simulations to run
            factor_uncertainty: Dict of {factor: (min_mult, max_mult)} for uncertainty range
            seed: Random seed for reproducibility
        """
        if seed:
            np.random.seed(seed)

        # Default uncertainty: +/- 20% on each factor
        if factor_uncertainty is None:
            factor_uncertainty = {
                "team_score": (0.8, 1.2),
                "market_score": (0.8, 1.2),
                "traction_score": (0.7, 1.3),  # Traction more uncertain
                "timing_score": (0.85, 1.15),
                "capital_score": (0.9, 1.1),
            }

        results = []

        for _ in range(simulations):
            # Sample from triangular distribution for each factor
            adjusted_factors = {}
            for factor, (low_mult, high_mult) in factor_uncertainty.items():
                base_val = self._base_factors.get(factor, 0.5)
                # Triangular: mode at base value
                sampled = np.random.triangular(
                    base_val * low_mult,
                    base_val,
                    base_val * high_mult
                )
                adjusted_factors[factor] = max(0, min(1, sampled))

            # Fill in any missing factors
            for factor in self._base_factors:
                if factor not in adjusted_factors:
                    adjusted_factors[factor] = self._base_factors[factor]

            prob = self._calculate_probability(adjusted_factors)
            results.append(prob)

        results = np.array(results)

        # Calculate statistics
        mean_prob = float(np.mean(results))
        median_prob = float(np.median(results))
        std_dev = float(np.std(results))

        percentiles = {
            "p5": float(np.percentile(results, 5)),
            "p10": float(np.percentile(results, 10)),
            "p25": float(np.percentile(results, 25)),
            "p50": float(np.percentile(results, 50)),
            "p75": float(np.percentile(results, 75)),
            "p90": float(np.percentile(results, 90)),
            "p95": float(np.percentile(results, 95)),
        }

        # Histogram for charting
        hist_counts, hist_bins = np.histogram(results, bins=50)

        return MonteCarloResult(
            simulations=simulations,
            seed=seed,
            mean_probability=mean_prob,
            median_probability=median_prob,
            std_dev=std_dev,
            **percentiles,
            ci_90=(percentiles["p5"], percentiles["p95"]),
            ci_95=(float(np.percentile(results, 2.5)), float(np.percentile(results, 97.5))),
            ci_99=(float(np.percentile(results, 0.5)), float(np.percentile(results, 99.5))),
            skewness=float(self._calculate_skewness(results)),
            kurtosis=float(self._calculate_kurtosis(results)),
            prob_unicorn=float(np.mean(results > 0.10)),  # >10% = likely unicorn
            prob_centaur=float(np.mean(results > 0.05)),
            prob_success=float(np.mean(results > 0.02)),
            prob_failure=float(np.mean(results < 0.02)),
            distribution=results.tolist()[:1000],  # Limit for JSON size
            histogram_bins=hist_bins.tolist(),
            histogram_counts=hist_counts.tolist()
        )

    def run_stress_test(
        self,
        scenario_name: str,
        shocks: List[Dict[str, Any]]
    ) -> StressTestResult:
        """
        Run a stress test with correlated shocks.

        Common stress scenarios:
        - Market downturn: All scores drop 20-30%
        - Competition shock: Market and timing scores drop
        - Execution crisis: Team and traction scores drop
        - Funding winter: Capital and timing scores drop
        """
        # Apply all shocks simultaneously
        adjusted_factors = copy.deepcopy(self._base_factors)

        for shock in shocks:
            factor = shock.get("factor")
            shock_type = shock.get("type", "percentage")
            shock_value = shock.get("value", -0.20)

            if factor in adjusted_factors:
                if shock_type == "percentage":
                    adjusted_factors[factor] *= (1 + shock_value)
                elif shock_type == "absolute":
                    adjusted_factors[factor] += shock_value

                adjusted_factors[factor] = max(0, min(1, adjusted_factors[factor]))

        stressed_probability = self._calculate_probability(adjusted_factors)

        prob_drop = self._base_probability - stressed_probability
        prob_drop_pct = (prob_drop / self._base_probability * 100) if self._base_probability > 0 else 0

        # Determine vulnerability rating
        if prob_drop_pct > 50:
            vulnerability = "CRITICAL"
            survives = False
        elif prob_drop_pct > 30:
            vulnerability = "HIGH"
            survives = True
        elif prob_drop_pct > 15:
            vulnerability = "MEDIUM"
            survives = True
        else:
            vulnerability = "LOW"
            survives = True

        return StressTestResult(
            scenario_name=scenario_name,
            description=f"Stress test with {len(shocks)} correlated shocks",
            shocks=shocks,
            base_probability=self._base_probability,
            stressed_probability=stressed_probability,
            probability_drop=prob_drop,
            probability_drop_pct=prob_drop_pct,
            survives_scenario=survives,
            vulnerability_rating=vulnerability
        )

    def create_preset_scenarios(self) -> List[Scenario]:
        """
        Create standard Bull/Base/Bear scenarios.
        """
        scenarios = []

        # Bull Case: All factors +20%
        bull = Scenario(
            scenario_name="Bull Case",
            scenario_type=ScenarioType.BULL_CASE,
            description="Optimistic scenario with all factors improving 20%",
            adjustments=[
                ParameterAdjustment(
                    parameter_path=factor,
                    adjustment_type="percentage",
                    adjustment_value=20,
                    rationale="Bull case assumption"
                )
                for factor in self._base_factors
            ]
        )
        scenarios.append(self.run_scenario(bull))

        # Base Case (current state)
        base = Scenario(
            scenario_name="Base Case",
            scenario_type=ScenarioType.BASE_CASE,
            description="Current state with no adjustments",
            adjustments=[]
        )
        base.base_probability = self._base_probability
        base.adjusted_probability = self._base_probability
        base.probability_delta = 0
        base.base_valuation = self._base_valuation
        base.adjusted_valuation = self._base_valuation
        base.valuation_delta = 0
        scenarios.append(base)

        # Bear Case: All factors -20%
        bear = Scenario(
            scenario_name="Bear Case",
            scenario_type=ScenarioType.BEAR_CASE,
            description="Pessimistic scenario with all factors declining 20%",
            adjustments=[
                ParameterAdjustment(
                    parameter_path=factor,
                    adjustment_type="percentage",
                    adjustment_value=-20,
                    rationale="Bear case assumption"
                )
                for factor in self._base_factors
            ]
        )
        scenarios.append(self.run_scenario(bear))

        return scenarios

    def _calculate_probability(self, factors: Dict[str, float]) -> float:
        """
        Recalculate unicorn probability from factor scores.

        Uses the same calibrated logistic model as the main prediction engine.
        """
        # Factor weights (from decision framework)
        weights = {
            "team_score": 0.30,
            "market_score": 0.25,
            "traction_score": 0.20,
            "timing_score": 0.15,
            "capital_score": 0.10
        }

        # Weighted average
        weighted_score = sum(
            factors.get(k, 0.5) * w
            for k, w in weights.items()
        )

        # Logistic transformation calibrated to ~1.8% base rate
        import math
        # Calibration parameters
        base_rate = 0.018
        logistic_slope = 4.0
        logistic_intercept = -4.2

        # Calculate logit
        score_logit = logistic_intercept + logistic_slope * weighted_score

        # Convert to probability
        probability = 1 / (1 + math.exp(-score_logit))

        return probability

    def _calculate_valuation(self, factors: Dict[str, float], probability: float) -> float:
        """Calculate expected valuation from factors and probability"""
        base_valuation = self._base_valuation or 20_000_000
        prob_ratio = probability / self._base_probability if self._base_probability > 0 else 1
        return base_valuation * prob_ratio

    def _get_recommendation(self, probability: float) -> str:
        """Get recommendation based on probability"""
        if probability > 0.15:
            return "STRONG_YES"
        elif probability > 0.08:
            return "YES"
        elif probability > 0.04:
            return "CONDITIONAL"
        elif probability > 0.02:
            return "NO"
        else:
            return "STRONG_NO"

    def _generate_impact_summary(self, scenario: Scenario) -> str:
        """Generate a narrative summary of scenario impact"""
        delta_pct = (scenario.probability_delta / self._base_probability * 100) if self._base_probability > 0 else 0

        if scenario.probability_delta > 0:
            direction = "increases"
        elif scenario.probability_delta < 0:
            direction = "decreases"
        else:
            direction = "remains unchanged"

        summary = f"This scenario {direction} unicorn probability by {abs(delta_pct):.1f}%"

        if scenario.recommendation_changed:
            summary += f", changing recommendation from {scenario.base_recommendation} to {scenario.adjusted_recommendation}"

        return summary

    @staticmethod
    def _calculate_skewness(data: np.ndarray) -> float:
        """Calculate skewness of distribution"""
        n = len(data)
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return (n / ((n - 1) * (n - 2))) * np.sum(((data - mean) / std) ** 3)

    @staticmethod
    def _calculate_kurtosis(data: np.ndarray) -> float:
        """Calculate kurtosis of distribution"""
        n = len(data)
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return ((n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))) * np.sum(((data - mean) / std) ** 4) - (3 * (n - 1) ** 2) / ((n - 2) * (n - 3))


# =============================================================================
# PRESET STRESS TESTS
# =============================================================================

def create_market_downturn_stress_test() -> Tuple[str, List[Dict[str, Any]]]:
    """2008/2022-style market crash"""
    return "Market Downturn", [
        {"factor": "market_score", "type": "percentage", "value": -0.30},
        {"factor": "timing_score", "type": "percentage", "value": -0.40},
        {"factor": "capital_score", "type": "percentage", "value": -0.25},
    ]


def create_competitive_disruption_stress_test() -> Tuple[str, List[Dict[str, Any]]]:
    """Major competitor enters market"""
    return "Competitive Disruption", [
        {"factor": "market_score", "type": "percentage", "value": -0.25},
        {"factor": "traction_score", "type": "percentage", "value": -0.15},
    ]


def create_execution_crisis_stress_test() -> Tuple[str, List[Dict[str, Any]]]:
    """Key founder leaves / major pivot"""
    return "Execution Crisis", [
        {"factor": "team_score", "type": "percentage", "value": -0.35},
        {"factor": "traction_score", "type": "percentage", "value": -0.20},
    ]


def create_funding_winter_stress_test() -> Tuple[str, List[Dict[str, Any]]]:
    """Venture capital pullback"""
    return "Funding Winter", [
        {"factor": "capital_score", "type": "percentage", "value": -0.40},
        {"factor": "timing_score", "type": "percentage", "value": -0.30},
    ]
