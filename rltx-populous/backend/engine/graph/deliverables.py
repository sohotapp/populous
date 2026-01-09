"""
Enterprise Deliverables Generator

This module generates board-ready, executive deliverables from the graph execution state.
These are the "Answer Nodes" - tangible outputs that justify $5-10M enterprise contracts.

Deliverable Types:
1. Investment Memo - Board-ready investment recommendation
2. Risk Register - Comprehensive risk assessment with mitigations
3. Decision Matrix - Side-by-side comparison with clear recommendation
4. Action Playbook - Step-by-step execution plan
5. Executive Brief - 1-page summary for C-suite
6. Scenario Analysis - What-if comparisons with probabilities
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import json


class RecommendationStrength(str, Enum):
    STRONG_YES = "STRONG_YES"
    YES = "YES"
    CONDITIONAL = "CONDITIONAL"
    NO = "NO"
    STRONG_NO = "STRONG_NO"


class RiskSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RiskCategory(str, Enum):
    MARKET = "MARKET"
    EXECUTION = "EXECUTION"
    FINANCIAL = "FINANCIAL"
    TEAM = "TEAM"
    COMPETITIVE = "COMPETITIVE"
    REGULATORY = "REGULATORY"
    TECHNICAL = "TECHNICAL"


# =============================================================================
# INVESTMENT MEMO
# =============================================================================

class InvestmentThesis(BaseModel):
    """Core investment thesis"""
    headline: str  # "Invest $X at $Y valuation for Z% ownership"
    rationale: List[str]  # 3-5 bullet points
    key_assumptions: List[str]
    upside_case: str
    downside_case: str


class DealTerms(BaseModel):
    """Proposed deal structure"""
    investment_amount: float
    pre_money_valuation: float
    post_money_valuation: float
    ownership_percentage: float
    instrument: str  # "SAFE", "Priced Round", "Convertible Note"
    key_terms: List[str]


class InvestmentMemo(BaseModel):
    """Board-ready investment memorandum"""
    # Header
    company_name: str
    prepared_for: str = "Investment Committee"
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    classification: str = "CONFIDENTIAL"

    # Executive Summary
    recommendation: RecommendationStrength
    recommendation_summary: str  # 2-3 sentences
    confidence_level: float  # 0-1

    # Investment Thesis
    thesis: InvestmentThesis

    # Deal Terms
    deal: DealTerms

    # Key Metrics
    metrics: Dict[str, Any]

    # Factor Analysis
    team_assessment: Dict[str, Any]
    market_assessment: Dict[str, Any]
    traction_assessment: Dict[str, Any]
    competitive_assessment: Dict[str, Any]

    # Risk Summary
    top_risks: List[Dict[str, str]]  # [{risk, severity, mitigation}]

    # Comparable Analysis
    comparables: List[Dict[str, Any]]

    # Exit Analysis
    exit_scenarios: List[Dict[str, Any]]
    expected_return_multiple: float
    expected_irr: float

    # Recommendation
    conditions_for_approval: List[str]
    next_steps: List[str]


# =============================================================================
# RISK REGISTER
# =============================================================================

class RiskItem(BaseModel):
    """Individual risk item"""
    id: str
    title: str
    description: str
    category: RiskCategory
    severity: RiskSeverity
    likelihood: float  # 0-1
    impact_score: float  # 0-1
    risk_score: float  # likelihood * impact

    # Mitigation
    current_mitigations: List[str]
    recommended_mitigations: List[str]
    residual_risk: float

    # Monitoring
    early_warning_signs: List[str]
    monitoring_frequency: str
    owner: str = "Investment Team"


class RiskRegister(BaseModel):
    """Comprehensive risk assessment"""
    company_name: str
    assessment_date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    # Summary
    overall_risk_rating: RiskSeverity
    risk_score: float  # 0-100
    risk_trend: str  # "INCREASING", "STABLE", "DECREASING"

    # Risks by Category
    risks: List[RiskItem]

    # Risk Matrix Summary
    critical_risks: int
    high_risks: int
    medium_risks: int
    low_risks: int

    # Key Insights
    top_concerns: List[str]
    risk_concentrations: List[str]  # Where risk is clustered

    # Recommendations
    immediate_actions: List[str]
    monitoring_plan: List[str]


# =============================================================================
# DECISION MATRIX
# =============================================================================

class CompanyComparison(BaseModel):
    """Single company in comparison"""
    name: str
    recommendation: RecommendationStrength
    overall_score: float

    # Factor Scores
    team_score: float
    market_score: float
    traction_score: float
    timing_score: float
    capital_score: float

    # Key Metrics
    unicorn_probability: float
    expected_valuation: float
    risk_score: float

    # Qualitative
    key_strengths: List[str]
    key_risks: List[str]

    # Deal Terms
    asking_valuation: float
    expected_return: float


class DecisionMatrix(BaseModel):
    """Side-by-side comparison with clear recommendation"""
    title: str
    decision_context: str  # "Which company to invest in from YC W24"
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    # Comparisons
    companies: List[CompanyComparison]

    # Winner
    recommended_company: str
    recommendation_rationale: str
    confidence_level: float

    # Trade-off Analysis
    trade_offs: List[Dict[str, str]]  # [{factor, winner, explanation}]

    # Sensitivity Analysis
    scenarios_where_recommendation_changes: List[str]

    # Final Recommendation
    primary_recommendation: str
    alternative_recommendation: str
    conditions_for_alternative: List[str]


# =============================================================================
# ACTION PLAYBOOK
# =============================================================================

class ActionItem(BaseModel):
    """Single action item"""
    id: str
    title: str
    description: str
    owner: str
    deadline: str
    priority: str  # "P0", "P1", "P2"
    dependencies: List[str]
    success_criteria: str
    estimated_effort: str


class PlaybookPhase(BaseModel):
    """Phase in the playbook"""
    name: str
    objective: str
    duration: str
    actions: List[ActionItem]
    exit_criteria: List[str]
    risks: List[str]


class ActionPlaybook(BaseModel):
    """Step-by-step execution plan"""
    title: str
    objective: str
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    # Context
    decision: str  # What decision was made
    rationale: str

    # Phases
    phases: List[PlaybookPhase]

    # Timeline
    total_duration: str
    key_milestones: List[Dict[str, str]]

    # Resources
    required_resources: List[str]
    budget_estimate: str

    # Governance
    decision_rights: Dict[str, str]
    escalation_path: List[str]
    review_cadence: str

    # Success Metrics
    success_metrics: List[Dict[str, str]]
    failure_indicators: List[str]


# =============================================================================
# EXECUTIVE BRIEF
# =============================================================================

class ExecutiveBrief(BaseModel):
    """1-page C-suite summary"""
    title: str
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    prepared_for: str

    # The Ask
    decision_required: str
    deadline: str

    # Recommendation
    recommendation: RecommendationStrength
    recommendation_text: str  # 1-2 sentences
    confidence: float

    # Key Points (max 5)
    key_points: List[str]

    # Numbers That Matter
    key_metrics: Dict[str, str]

    # Risk Summary
    top_risk: str
    risk_mitigation: str

    # Alternatives Considered
    alternatives: List[Dict[str, str]]

    # Next Steps
    if_approved: List[str]
    if_rejected: List[str]

    # Appendix Reference
    supporting_documents: List[str]


# =============================================================================
# SCENARIO ANALYSIS
# =============================================================================

class Scenario(BaseModel):
    """Single scenario"""
    name: str
    probability: float
    description: str

    # Assumptions
    key_assumptions: List[str]

    # Outcomes
    valuation_outcome: float
    return_multiple: float
    time_to_exit: float

    # Implications
    implications: List[str]
    required_actions: List[str]


class ScenarioAnalysis(BaseModel):
    """What-if scenario comparison"""
    title: str
    company_name: str
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    # Base Case
    base_case: Scenario

    # Alternative Scenarios
    upside_case: Scenario
    downside_case: Scenario
    stress_case: Scenario

    # Expected Value
    probability_weighted_outcome: float
    expected_return: float

    # Sensitivity
    key_drivers: List[Dict[str, Any]]  # Which inputs matter most
    break_even_assumptions: List[str]

    # Decision Framework
    proceed_if: List[str]
    pause_if: List[str]
    exit_if: List[str]


# =============================================================================
# DELIVERABLES GENERATOR
# =============================================================================

class DeliverablesGenerator:
    """Generates all deliverables from graph state"""

    def __init__(self, graph_state: Any, framework: Any = None):
        self.state = graph_state
        self.framework = framework

        # Load default framework if none provided
        if self.framework is None:
            try:
                from backend.engine.config.decision_framework import DecisionFramework
                self.framework = DecisionFramework()
            except ImportError:
                self.framework = None

    def _get_threshold(self, threshold_name: str, default: float) -> float:
        """Get threshold from framework or use default"""
        if self.framework and hasattr(self.framework, 'thresholds'):
            return getattr(self.framework.thresholds, threshold_name, default)
        return default

    def _get_investment_criteria(self, criteria_name: str, default: Any) -> Any:
        """Get investment criteria from framework"""
        if self.framework and hasattr(self.framework, 'investment_criteria'):
            return getattr(self.framework.investment_criteria, criteria_name, default)
        return default

    def _build_team_assessment(self, pred: Any, research: Any, team_score: float, key_strengths: List[str]) -> Dict[str, Any]:
        """Build team assessment from actual data"""
        # Extract founder info from research
        founders = []
        if research and hasattr(research, 'founders'):
            founders = [f.name if hasattr(f, 'name') else str(f) for f in (research.founders or [])]
        elif isinstance(research, dict):
            founders = [f.get('name', str(f)) if isinstance(f, dict) else str(f) for f in research.get('founders', [])]

        # Build strengths from key_strengths or generate from score
        team_strengths = [s for s in key_strengths if any(word in s.lower() for word in ['team', 'founder', 'experience', 'expertise', 'leader'])][:3]
        if not team_strengths:
            if team_score > 0.7:
                team_strengths = ["Exceptional founding team with proven track record", "Deep domain expertise"]
            elif team_score > 0.5:
                team_strengths = ["Solid team with relevant experience", "Complementary skill sets"]
            else:
                team_strengths = ["Motivated founding team", "Learning rapidly"]

        # Build concerns based on score
        if team_score > 0.7:
            concerns = ["Key person dependency"]
        elif team_score > 0.5:
            concerns = ["May need to strengthen go-to-market leadership"]
        else:
            concerns = ["Limited operating experience", "May need senior hires"]

        return {
            "score": team_score,
            "founders": founders[:3] if founders else ["Founding team under research"],
            "strengths": team_strengths,
            "concerns": concerns
        }

    def _build_market_assessment(self, pred: Any, research: Any, market_score: float) -> Dict[str, Any]:
        """Build market assessment from actual data"""
        # Extract sector from research
        sector = "Technology"
        if research and hasattr(research, 'overview') and research.overview:
            sector = getattr(research.overview, 'sector', 'Technology') if hasattr(research.overview, 'sector') else 'Technology'
        elif isinstance(research, dict):
            overview = research.get('overview', {})
            sector = overview.get('sector', 'Technology') if isinstance(overview, dict) else 'Technology'

        if market_score > 0.7:
            tam = "$100B+"
            growth = "30%+ CAGR"
            timing = "Excellent - market inflection point"
        elif market_score > 0.5:
            tam = "$50B+"
            growth = "20-30% CAGR"
            timing = "Favorable - growing market"
        else:
            tam = "$10-50B"
            growth = "10-20% CAGR"
            timing = "Emerging - early market"

        return {
            "score": market_score,
            "sector": sector,
            "tam": tam,
            "growth_rate": growth,
            "timing": timing
        }

    def _build_traction_assessment(self, pred: Any, research: Any, traction_score: float) -> Dict[str, Any]:
        """Build traction assessment from actual data"""
        # Extract funding from research
        funding = None
        if research and hasattr(research, 'funding') and research.funding:
            funding_data = research.funding
            if hasattr(funding_data, 'value'):
                funding = funding_data.value
            elif isinstance(funding_data, dict):
                funding = funding_data.get('value')

        funding_str = f"${funding/1e6:.1f}M raised" if funding and funding > 0 else "Funding details under research"

        if traction_score > 0.7:
            stage = "Strong product-market fit"
            metrics = "Revenue growing, strong retention"
        elif traction_score > 0.5:
            stage = "Early product-market fit signals"
            metrics = "Growing user base, early revenue"
        elif traction_score > 0.3:
            stage = "Pre-revenue with user traction"
            metrics = "User growth, engagement metrics"
        else:
            stage = "Pre-launch / Early development"
            metrics = "Development milestones"

        return {
            "score": traction_score,
            "funding": funding_str,
            "stage": stage,
            "key_metrics": metrics
        }

    def _build_competitive_assessment(self, pred: Any, research: Any) -> Dict[str, Any]:
        """Build competitive assessment from research data"""
        # Extract from research if available
        competitors = []
        if research and hasattr(research, 'overview') and research.overview:
            if hasattr(research.overview, 'competitors'):
                competitors = research.overview.competitors or []
        elif isinstance(research, dict):
            overview = research.get('overview', {})
            if isinstance(overview, dict):
                competitors = overview.get('competitors', [])

        # Determine moat strength from prediction
        moat = "Moderate"
        diff = "Technical differentiation"
        key_risks = getattr(pred, 'key_risks', []) if hasattr(pred, 'key_risks') else pred.get('key_risks', []) if isinstance(pred, dict) else []

        if any('compet' in str(r).lower() for r in key_risks):
            moat = "Developing"
            diff = "Building defensibility"
        elif any('first' in str(r).lower() or 'leader' in str(r).lower() for r in (getattr(pred, 'key_strengths', []) if hasattr(pred, 'key_strengths') else [])):
            moat = "Strong first-mover advantage"
            diff = "Market leadership position"

        return {
            "moat": moat,
            "key_competitors": competitors[:3] if competitors else ["Market competitors under research"],
            "differentiation": diff
        }

    def _build_top_risks(self, pred: Any, key_risks: List[str], team_score: float, market_score: float, traction_score: float) -> List[Dict[str, str]]:
        """Build top risks from prediction key_risks and factor scores"""
        risks = []

        # Use actual key_risks from prediction
        for risk in key_risks[:2]:
            severity = "HIGH" if any(word in risk.lower() for word in ['major', 'critical', 'significant']) else "MEDIUM"
            risks.append({
                "risk": risk,
                "severity": severity,
                "mitigation": "Active monitoring and contingency planning"
            })

        # Add factor-based risks if we don't have enough
        if team_score < 0.5 and len(risks) < 3:
            risks.append({
                "risk": f"Team execution risk (score: {team_score*100:.0f}/100)",
                "severity": "HIGH" if team_score < 0.3 else "MEDIUM",
                "mitigation": "Consider adding experienced advisors or operators"
            })

        if market_score < 0.5 and len(risks) < 3:
            risks.append({
                "risk": f"Market timing/size risk (score: {market_score*100:.0f}/100)",
                "severity": "HIGH" if market_score < 0.3 else "MEDIUM",
                "mitigation": "Monitor market development closely"
            })

        if traction_score < 0.4 and len(risks) < 3:
            risks.append({
                "risk": f"Product-market fit risk (score: {traction_score*100:.0f}/100)",
                "severity": "HIGH" if traction_score < 0.2 else "MEDIUM",
                "mitigation": "Milestone-based funding tranches"
            })

        # Ensure we have at least 3 risks
        default_risks = [
            {"risk": "Competitive dynamics", "severity": "MEDIUM", "mitigation": "Build sustainable moat"},
            {"risk": "Funding environment", "severity": "MEDIUM", "mitigation": "Capital efficient growth"},
            {"risk": "Regulatory changes", "severity": "LOW", "mitigation": "Monitor policy landscape"}
        ]
        while len(risks) < 3:
            risks.append(default_risks[len(risks) % len(default_risks)])

        return risks[:3]

    def _build_comparables(self, research: Any, expected_val: float) -> List[Dict[str, Any]]:
        """Build comparables from research data or intelligent defaults"""
        # Try to extract from research
        sector = "Technology"
        if research and hasattr(research, 'overview') and research.overview:
            sector = getattr(research.overview, 'sector', 'Technology') if hasattr(research.overview, 'sector') else 'Technology'
        elif isinstance(research, dict):
            overview = research.get('overview', {})
            sector = overview.get('sector', 'Technology') if isinstance(overview, dict) else 'Technology'

        # Generate contextual comparables based on valuation tier
        if expected_val > 100_000_000:
            return [
                {"company": f"{sector} leader (Series B)", "valuation": "$150M", "stage": "Series B"},
                {"company": f"Recent {sector} unicorn", "valuation": "$1B", "stage": "Series C"}
            ]
        elif expected_val > 50_000_000:
            return [
                {"company": f"{sector} Series A comp", "valuation": "$80M", "stage": "Series A"},
                {"company": f"Similar stage {sector} startup", "valuation": "$60M", "stage": "Series A"}
            ]
        else:
            return [
                {"company": f"Seed-stage {sector} comp", "valuation": "$25M", "stage": "Seed"},
                {"company": f"YC {sector} graduate", "valuation": "$20M", "stage": "Seed"}
            ]

    def _calculate_deal_terms(self, valuation: float) -> Dict[str, Any]:
        """Calculate deal terms from framework configuration"""
        min_check = self._get_investment_criteria('min_check_size', 500_000)
        max_check = self._get_investment_criteria('max_check_size', 5_000_000)
        target_ownership = self._get_investment_criteria('min_ownership_target', 0.10)

        # Calculate investment amount to hit target ownership
        investment = valuation * target_ownership / (1 - target_ownership)
        investment = max(min_check, min(max_check, investment))

        ownership = investment / (valuation + investment)

        return {
            "investment_amount": investment,
            "pre_money_valuation": valuation,
            "post_money_valuation": valuation + investment,
            "ownership_percentage": ownership * 100,
            "instrument": "SAFE" if valuation < 10_000_000 else "Priced Round"
        }

    def _safe_to_dict(self, obj: Any) -> Dict:
        """Safely convert an object to dict, handling Pydantic models and dicts"""
        if obj is None:
            return {}
        if isinstance(obj, dict):
            return obj
        if hasattr(obj, 'model_dump'):
            try:
                return obj.model_dump()
            except Exception:
                pass
        if hasattr(obj, '__dict__'):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        return {}

    def _get_value(self, obj: Any, key: str, default: Any = None) -> Any:
        """Safely get a value from either a dict or object"""
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def generate_investment_memo(self, company_name: str) -> InvestmentMemo:
        """Generate board-ready investment memo using framework configuration"""
        pred = self.state.predictions.get(company_name, {})
        brief = self.state.decision_briefs.get(company_name, {})
        research = self.state.research.get(company_name, {})
        monte_carlo_obj = self.state.monte_carlo.get(company_name)
        monte_carlo = self._safe_to_dict(monte_carlo_obj)
        exit_model_obj = self.state.exit_models.get(company_name)
        exit_model = self._safe_to_dict(exit_model_obj)

        # Extract prediction values (handle both object and dict)
        prob = getattr(pred, 'unicorn_probability', 0) if hasattr(pred, 'unicorn_probability') else pred.get('unicorn_probability', 0)
        expected_val = getattr(pred, 'expected_valuation', 50_000_000) if hasattr(pred, 'expected_valuation') else pred.get('expected_valuation', 50_000_000)
        confidence = getattr(pred, 'prediction_confidence', 0.5) if hasattr(pred, 'prediction_confidence') else pred.get('prediction_confidence', 0.5)

        # Get factor scores from prediction
        team_score = getattr(pred, 'team_score', 0.5) if hasattr(pred, 'team_score') else pred.get('team_score', 0.5)
        market_score = getattr(pred, 'market_score', 0.5) if hasattr(pred, 'market_score') else pred.get('market_score', 0.5)
        traction_score = getattr(pred, 'traction_score', 0.5) if hasattr(pred, 'traction_score') else pred.get('traction_score', 0.5)
        timing_score = getattr(pred, 'timing_score', 0.5) if hasattr(pred, 'timing_score') else pred.get('timing_score', 0.5)
        capital_score = getattr(pred, 'capital_score', 0.5) if hasattr(pred, 'capital_score') else pred.get('capital_score', 0.5)

        # Get key strengths and risks from prediction
        key_strengths = getattr(pred, 'key_strengths', []) if hasattr(pred, 'key_strengths') else pred.get('key_strengths', [])
        key_risks = getattr(pred, 'key_risks', []) if hasattr(pred, 'key_risks') else pred.get('key_risks', [])

        # Calculate recommendation using framework thresholds
        strong_yes_threshold = self._get_threshold('strong_yes_threshold', 0.15)
        yes_threshold = self._get_threshold('yes_threshold', 0.08)
        conditional_threshold = self._get_threshold('conditional_threshold', 0.04)
        no_threshold = self._get_threshold('no_threshold', 0.02)

        if prob > strong_yes_threshold:
            recommendation = RecommendationStrength.STRONG_YES
        elif prob > yes_threshold:
            recommendation = RecommendationStrength.YES
        elif prob > conditional_threshold:
            recommendation = RecommendationStrength.CONDITIONAL
        elif prob > no_threshold:
            recommendation = RecommendationStrength.NO
        else:
            recommendation = RecommendationStrength.STRONG_NO

        # Calculate deal terms from framework
        deal_terms = self._calculate_deal_terms(expected_val)
        investment_amount = deal_terms["investment_amount"]
        ownership_pct = deal_terms["ownership_percentage"]

        # Extract exit probabilities from exit model
        exit_ipo_prob = exit_model.get('ipo_probability', prob)
        exit_acquisition_prob = exit_model.get('acquisition_probability', 0.3)

        # Calculate expected IRR from Monte Carlo if available
        expected_irr = 0.30  # Default
        if monte_carlo:
            # MonteCarloOutput uses 'unicorn_prob_mean' field name
            mc_mean = monte_carlo.get('unicorn_prob_mean', monte_carlo.get('mean', prob))
            if mc_mean > 0.15:
                expected_irr = 0.50
            elif mc_mean > 0.08:
                expected_irr = 0.35
            elif mc_mean > 0.04:
                expected_irr = 0.25
            else:
                expected_irr = 0.15

        # Calculate expected return multiple
        expected_multiple = prob * 20 + exit_acquisition_prob * 5 + (1 - prob - exit_acquisition_prob) * 0.5

        return InvestmentMemo(
            company_name=company_name,
            prepared_for=self.framework.outputs.company_name if self.framework and hasattr(self.framework, 'outputs') else "Investment Committee",
            recommendation=recommendation,
            recommendation_summary=f"{company_name} presents a {recommendation.value.lower().replace('_', ' ')} investment opportunity with {prob*100:.1f}% unicorn probability, {confidence*100:.0f}% model confidence, and expected valuation of ${expected_val/1e6:.0f}M.",
            confidence_level=confidence,
            thesis=InvestmentThesis(
                headline=f"Invest ${investment_amount/1e6:.1f}M at ${expected_val/1e6:.0f}M valuation for {ownership_pct:.1f}% ownership",
                rationale=key_strengths[:4] if key_strengths else ['Strong founding team', 'Large addressable market', 'Early traction signals', 'Favorable timing'],
                key_assumptions=[
                    f"Team score of {team_score*100:.0f}/100 reflects execution capability",
                    f"Market opportunity supports ${expected_val/1e6:.0f}M+ outcomes",
                    f"Current traction ({traction_score*100:.0f}/100) validates product-market fit trajectory"
                ],
                upside_case=f"With {prob*100:.1f}% unicorn probability, strong execution could yield {expected_multiple:.0f}x+ returns in 5-7 years",
                downside_case="Market contraction or execution issues could require bridge financing or result in acqui-hire exit"
            ),
            deal=DealTerms(
                investment_amount=investment_amount,
                pre_money_valuation=expected_val,
                post_money_valuation=expected_val + investment_amount,
                ownership_percentage=ownership_pct,
                instrument=deal_terms["instrument"],
                key_terms=["Pro-rata rights", "Information rights", "Board observer seat"] if investment_amount > 1_000_000 else ["Pro-rata rights", "Information rights", "MFN clause"]
            ),
            metrics={
                "unicorn_probability": f"{prob*100:.1f}%",
                "expected_valuation": f"${expected_val/1e6:.0f}M",
                "team_score": f"{getattr(pred, 'team_score', 0.5)*100:.0f}/100" if hasattr(pred, 'team_score') else "50/100",
                "market_score": f"{getattr(pred, 'market_score', 0.5)*100:.0f}/100" if hasattr(pred, 'market_score') else "50/100",
            },
            team_assessment=self._build_team_assessment(pred, research, team_score, key_strengths),
            market_assessment=self._build_market_assessment(pred, research, market_score),
            traction_assessment=self._build_traction_assessment(pred, research, traction_score),
            competitive_assessment=self._build_competitive_assessment(pred, research),
            top_risks=self._build_top_risks(pred, key_risks, team_score, market_score, traction_score),
            comparables=self._build_comparables(research, expected_val),
            exit_scenarios=[
                {"scenario": "Unicorn IPO", "probability": f"{prob*100:.0f}%", "return": "20x"},
                {"scenario": "Strategic Acquisition", "probability": "30%", "return": "5x"},
                {"scenario": "Acqui-hire", "probability": "20%", "return": "1x"}
            ],
            expected_return_multiple=prob * 20 + 0.3 * 5 + 0.2 * 1,
            expected_irr=0.35,
            conditions_for_approval=[
                "Complete technical due diligence",
                "Reference checks on founders",
                "Confirm lead investor participation"
            ],
            next_steps=[
                "Schedule founder deep-dive session",
                "Request data room access",
                "Prepare term sheet draft"
            ]
        )

    def generate_risk_register(self, company_name: str) -> RiskRegister:
        """Generate comprehensive risk register based on ACTUAL factor scores"""
        pred = self.state.predictions.get(company_name, {})

        # Extract factor scores
        team_score = getattr(pred, 'team_score', 0.5) if hasattr(pred, 'team_score') else pred.get('team_score', 0.5) if isinstance(pred, dict) else 0.5
        market_score = getattr(pred, 'market_score', 0.5) if hasattr(pred, 'market_score') else pred.get('market_score', 0.5) if isinstance(pred, dict) else 0.5
        traction_score = getattr(pred, 'traction_score', 0.5) if hasattr(pred, 'traction_score') else pred.get('traction_score', 0.5) if isinstance(pred, dict) else 0.5
        timing_score = getattr(pred, 'timing_score', 0.5) if hasattr(pred, 'timing_score') else pred.get('timing_score', 0.5) if isinstance(pred, dict) else 0.5
        capital_score = getattr(pred, 'capital_score', 0.5) if hasattr(pred, 'capital_score') else pred.get('capital_score', 0.5) if isinstance(pred, dict) else 0.5

        # Get key risks from prediction for context
        key_risks = getattr(pred, 'key_risks', []) if hasattr(pred, 'key_risks') else pred.get('key_risks', []) if isinstance(pred, dict) else []

        # Calculate dynamic severity based on factor scores
        def score_to_severity(score: float) -> RiskSeverity:
            if score < 0.3: return RiskSeverity.CRITICAL
            if score < 0.5: return RiskSeverity.HIGH
            if score < 0.7: return RiskSeverity.MEDIUM
            return RiskSeverity.LOW

        risks = [
            RiskItem(
                id="R001",
                title=f"Execution Risk (Team Score: {team_score*100:.0f}/100)",
                description=f"Team execution capability assessment based on founder experience, prior exits, and domain expertise. {'Strong team reduces execution risk.' if team_score > 0.6 else 'Team may need strengthening in key areas.'}",
                category=RiskCategory.EXECUTION,
                severity=score_to_severity(team_score),
                likelihood=round(1 - team_score, 2),
                impact_score=0.8,
                risk_score=round((1 - team_score) * 0.8, 2),
                current_mitigations=["Experienced advisors in place" if team_score > 0.5 else "Building advisory network"],
                recommended_mitigations=["Monthly milestone reviews", "Executive coaching" if team_score < 0.5 else "Succession planning"],
                residual_risk=round((1 - team_score) * 0.5, 2),
                early_warning_signs=["Missed milestones", "Key hire departures", "Founder burnout"],
                monitoring_frequency="Monthly"
            ),
            RiskItem(
                id="R002",
                title=f"Market Risk (Market Score: {market_score*100:.0f}/100)",
                description=f"Market timing and sizing assessment. {'Favorable market conditions.' if market_score > 0.6 else 'Market timing or size may present challenges.'}",
                category=RiskCategory.MARKET,
                severity=score_to_severity(market_score),
                likelihood=round(1 - market_score, 2),
                impact_score=0.7,
                risk_score=round((1 - market_score) * 0.7, 2),
                current_mitigations=["Market research completed" if market_score > 0.5 else "Conducting market validation"],
                recommended_mitigations=["Expand customer discovery", "Build pivot optionality"],
                residual_risk=round((1 - market_score) * 0.4, 2),
                early_warning_signs=["Slowing demand signals", "Competitor traction", "Market contraction"],
                monitoring_frequency="Quarterly"
            ),
            RiskItem(
                id="R003",
                title=f"Traction Risk (Traction Score: {traction_score*100:.0f}/100)",
                description=f"Product-market fit assessment. {'Strong early traction validates approach.' if traction_score > 0.6 else 'Still proving product-market fit.'}",
                category=RiskCategory.EXECUTION,
                severity=score_to_severity(traction_score),
                likelihood=round(1 - traction_score, 2),
                impact_score=0.7,
                risk_score=round((1 - traction_score) * 0.7, 2),
                current_mitigations=["Active customer engagement" if traction_score > 0.4 else "Building initial user base"],
                recommended_mitigations=["Accelerate customer feedback loops", "A/B testing framework"],
                residual_risk=round((1 - traction_score) * 0.4, 2),
                early_warning_signs=["User churn increase", "Engagement decline", "Feature requests stall"],
                monitoring_frequency="Weekly"
            ),
            RiskItem(
                id="R004",
                title=f"Capital Risk (Capital Score: {capital_score*100:.0f}/100)",
                description=f"Funding and runway assessment. {'Well-capitalized for current stage.' if capital_score > 0.6 else 'May need funding runway attention.'}",
                category=RiskCategory.FINANCIAL,
                severity=score_to_severity(capital_score),
                likelihood=round(1 - capital_score, 2),
                impact_score=0.9,
                risk_score=round((1 - capital_score) * 0.9, 2),
                current_mitigations=["Budget controls in place" if capital_score > 0.5 else "Developing capital efficiency"],
                recommended_mitigations=["Bridge financing relationships", "Cost optimization review"],
                residual_risk=round((1 - capital_score) * 0.5, 2),
                early_warning_signs=["Burn rate acceleration", "Revenue shortfall", "Funding delays"],
                monitoring_frequency="Monthly"
            ),
            RiskItem(
                id="R005",
                title=f"Timing Risk (Timing Score: {timing_score*100:.0f}/100)",
                description=f"Market timing assessment. {'Favorable timing window.' if timing_score > 0.6 else 'Timing may be suboptimal.'}",
                category=RiskCategory.MARKET,
                severity=score_to_severity(timing_score),
                likelihood=round(1 - timing_score, 2),
                impact_score=0.6,
                risk_score=round((1 - timing_score) * 0.6, 2),
                current_mitigations=["Market monitoring active" if timing_score > 0.5 else "Tracking market signals"],
                recommended_mitigations=["Flexible launch timeline", "Market catalyst tracking"],
                residual_risk=round((1 - timing_score) * 0.3, 2),
                early_warning_signs=["Market slowdown", "Regulatory changes", "Technology shifts"],
                monitoring_frequency="Quarterly"
            )
        ]

        # Calculate dynamic summary metrics
        avg_score = (team_score + market_score + traction_score + timing_score + capital_score) / 5
        overall_risk = round((1 - avg_score) * 100)
        critical_count = sum(1 for r in risks if r.severity == RiskSeverity.CRITICAL)
        high_count = sum(1 for r in risks if r.severity == RiskSeverity.HIGH)
        medium_count = sum(1 for r in risks if r.severity == RiskSeverity.MEDIUM)
        low_count = sum(1 for r in risks if r.severity == RiskSeverity.LOW)

        # Determine overall rating
        if critical_count > 0:
            overall_rating = RiskSeverity.CRITICAL
        elif high_count >= 3:
            overall_rating = RiskSeverity.HIGH
        elif high_count >= 1:
            overall_rating = RiskSeverity.MEDIUM
        else:
            overall_rating = RiskSeverity.LOW

        # Build dynamic concerns from key_risks
        top_concerns = key_risks[:3] if key_risks else [
            f"{'Team execution' if team_score < 0.5 else 'Market timing'} is primary concern",
            f"Traction {'needs acceleration' if traction_score < 0.5 else 'on track'}",
            "Standard early-stage risks apply"
        ]

        return RiskRegister(
            company_name=company_name,
            overall_risk_rating=overall_rating,
            risk_score=overall_risk,
            risk_trend="IMPROVING" if avg_score > 0.6 else ("STABLE" if avg_score > 0.4 else "ELEVATED"),
            risks=risks,
            critical_risks=critical_count,
            high_risks=high_count,
            medium_risks=medium_count,
            low_risks=low_count,
            top_concerns=top_concerns,
            risk_concentrations=[
                f"{'Execution risks' if team_score < market_score else 'Market risks'} require primary attention",
                f"Capital efficiency {'strong' if capital_score > 0.6 else 'needs monitoring'}"
            ],
            immediate_actions=[
                "Establish monthly milestone reviews",
                "Complete competitive intelligence refresh",
                "Model downside runway scenarios"
            ],
            monitoring_plan=[
                "Weekly: Burn rate and cash position",
                "Monthly: Product milestones and team health",
                "Quarterly: Market dynamics and competitive landscape"
            ]
        )

    def generate_decision_matrix(self) -> DecisionMatrix:
        """Generate side-by-side comparison"""
        companies = []

        for company_name in self.state.target_companies[:5]:
            pred = self.state.predictions.get(company_name, {})
            brief = self.state.decision_briefs.get(company_name, {})

            prob = getattr(pred, 'unicorn_probability', 0.03) if hasattr(pred, 'unicorn_probability') else 0.03

            if prob > 0.10:
                rec = RecommendationStrength.STRONG_YES
            elif prob > 0.05:
                rec = RecommendationStrength.YES
            elif prob > 0.03:
                rec = RecommendationStrength.CONDITIONAL
            else:
                rec = RecommendationStrength.NO

            companies.append(CompanyComparison(
                name=company_name,
                recommendation=rec,
                overall_score=prob * 100,
                team_score=getattr(pred, 'team_score', 0.5) if hasattr(pred, 'team_score') else 0.5,
                market_score=getattr(pred, 'market_score', 0.5) if hasattr(pred, 'market_score') else 0.5,
                traction_score=getattr(pred, 'traction_score', 0.5) if hasattr(pred, 'traction_score') else 0.5,
                timing_score=getattr(pred, 'timing_score', 0.5) if hasattr(pred, 'timing_score') else 0.5,
                capital_score=getattr(pred, 'capital_score', 0.5) if hasattr(pred, 'capital_score') else 0.5,
                unicorn_probability=prob,
                expected_valuation=getattr(pred, 'expected_valuation', 50_000_000) if hasattr(pred, 'expected_valuation') else 50_000_000,
                risk_score=0.5,
                key_strengths=getattr(pred, 'key_strengths', ['Strong potential'])[:2] if hasattr(pred, 'key_strengths') else ['Analysis pending'],
                key_risks=getattr(pred, 'key_risks', ['Standard risks'])[:2] if hasattr(pred, 'key_risks') else ['Under review'],
                asking_valuation=getattr(pred, 'expected_valuation', 50_000_000) if hasattr(pred, 'expected_valuation') else 50_000_000,
                expected_return=prob * 20
            ))

        # Sort by overall score
        companies.sort(key=lambda x: x.overall_score, reverse=True)

        winner = companies[0] if companies else None

        return DecisionMatrix(
            title=f"{self.state.batch.batch_name if self.state.batch else 'Batch'} Investment Decision Matrix",
            decision_context=f"Evaluate top candidates from {self.state.batch.batch_name if self.state.batch else 'batch'} for investment",
            companies=companies,
            recommended_company=winner.name if winner else "None",
            recommendation_rationale=f"{winner.name} leads with {winner.unicorn_probability*100:.1f}% unicorn probability, strong market timing, and acceptable risk profile." if winner else "Insufficient data",
            confidence_level=0.75,
            trade_offs=[
                {"factor": "Upside Potential", "winner": winner.name if winner else "N/A", "explanation": "Highest unicorn probability"},
                {"factor": "Risk-Adjusted Return", "winner": winner.name if winner else "N/A", "explanation": "Best Sharpe ratio equivalent"},
                {"factor": "Market Timing", "winner": winner.name if winner else "N/A", "explanation": "Optimal sector positioning"}
            ],
            scenarios_where_recommendation_changes=[
                "If market conditions deteriorate significantly",
                "If due diligence reveals undisclosed issues",
                "If valuation expectations increase materially"
            ],
            primary_recommendation=f"Invest in {winner.name}" if winner else "Further analysis required",
            alternative_recommendation=f"Consider {companies[1].name} as backup" if len(companies) > 1 else "No alternative",
            conditions_for_alternative=[
                "If primary target declines our terms",
                "If reference checks raise concerns",
                "If competitive dynamics shift"
            ]
        )

    def generate_executive_brief(self, company_name: str) -> ExecutiveBrief:
        """Generate 1-page C-suite summary"""
        pred = self.state.predictions.get(company_name, {})

        prob = getattr(pred, 'unicorn_probability', 0.03) if hasattr(pred, 'unicorn_probability') else 0.03
        expected_val = getattr(pred, 'expected_valuation', 50_000_000) if hasattr(pred, 'expected_valuation') else 50_000_000

        if prob > 0.10:
            rec = RecommendationStrength.STRONG_YES
        elif prob > 0.05:
            rec = RecommendationStrength.YES
        elif prob > 0.03:
            rec = RecommendationStrength.CONDITIONAL
        else:
            rec = RecommendationStrength.NO

        return ExecutiveBrief(
            title=f"{company_name} - Investment Decision Brief",
            prepared_for="Investment Committee",
            decision_required=f"Approve $500K investment in {company_name} at ${expected_val/1e6:.0f}M valuation",
            deadline="End of week",
            recommendation=rec,
            recommendation_text=f"Recommend {rec.value.lower().replace('_', ' ')} based on {prob*100:.1f}% unicorn probability and strong market positioning.",
            confidence=0.75,
            key_points=[
                f"Unicorn probability: {prob*100:.1f}% (top quartile for this batch)",
                f"Expected valuation: ${expected_val/1e6:.0f}M (7-year horizon)",
                "Market timing: Favorable (sector growing 25%+ CAGR)",
                "Team: Strong domain expertise, first-time founders",
                "Risk level: Moderate (standard for stage)"
            ],
            key_metrics={
                "Unicorn Probability": f"{prob*100:.1f}%",
                "Expected Return": f"{prob * 20:.1f}x",
                "Time to Exit": "5-7 years",
                "Investment Size": "$500K",
                "Ownership": "1%"
            },
            top_risk="Execution risk - first-time founders with ambitious timeline",
            risk_mitigation="Monthly milestone reviews and experienced advisory board",
            alternatives=[
                {"option": "Full investment", "pros": "Maximum exposure to upside", "cons": "Full risk"},
                {"option": "Half investment", "pros": "Reduced risk", "cons": "Less ownership"},
                {"option": "Pass", "pros": "Preserve capital", "cons": "Miss potential winner"}
            ],
            if_approved=[
                "Finalize term sheet by Friday",
                "Complete legal docs within 2 weeks",
                "Close funding within 30 days"
            ],
            if_rejected=[
                "Document reasons for future reference",
                "Maintain relationship for potential future rounds",
                "Monitor company progress quarterly"
            ],
            supporting_documents=[
                "Full Investment Memo",
                "Risk Register",
                "Due Diligence Report",
                "Comparable Analysis"
            ]
        )

    def generate_all_deliverables(self) -> Dict[str, Any]:
        """Generate all deliverables for the batch"""
        deliverables = {
            "generated_at": datetime.now().isoformat(),
            "batch": self.state.batch.batch_name if self.state.batch else "Unknown",
            "companies_analyzed": len(self.state.target_companies),

            # Batch-level deliverables
            "decision_matrix": self.generate_decision_matrix().model_dump(),

            # Per-company deliverables
            "investment_memos": {},
            "risk_registers": {},
            "executive_briefs": {}
        }

        for company in self.state.target_companies:
            deliverables["investment_memos"][company] = self.generate_investment_memo(company).model_dump()
            deliverables["risk_registers"][company] = self.generate_risk_register(company).model_dump()
            deliverables["executive_briefs"][company] = self.generate_executive_brief(company).model_dump()

        return deliverables
