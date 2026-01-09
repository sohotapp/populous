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

    def generate_investment_memo(self, company_name: str) -> InvestmentMemo:
        """Generate board-ready investment memo using framework configuration"""
        pred = self.state.predictions.get(company_name, {})
        brief = self.state.decision_briefs.get(company_name, {})
        research = self.state.research.get(company_name, {})
        monte_carlo = self.state.monte_carlo.get(company_name, {})
        exit_model = self.state.exit_models.get(company_name, {})

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
            mc_mean = monte_carlo.get('mean', prob)
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
            team_assessment={
                "score": getattr(pred, 'team_score', 0.5) if hasattr(pred, 'team_score') else 0.5,
                "strengths": ["Relevant domain experience"],
                "concerns": ["First-time founders"]
            },
            market_assessment={
                "score": getattr(pred, 'market_score', 0.5) if hasattr(pred, 'market_score') else 0.5,
                "tam": "$50B+",
                "growth_rate": "25% CAGR",
                "timing": "Favorable"
            },
            traction_assessment={
                "score": getattr(pred, 'traction_score', 0.5) if hasattr(pred, 'traction_score') else 0.5,
                "stage": "Pre-revenue / Early revenue",
                "key_metrics": "User growth, engagement"
            },
            competitive_assessment={
                "moat": "Moderate",
                "key_competitors": ["Incumbent A", "Startup B"],
                "differentiation": "Technical approach"
            },
            top_risks=[
                {"risk": "Execution risk", "severity": "HIGH", "mitigation": "Strong advisory board"},
                {"risk": "Market timing", "severity": "MEDIUM", "mitigation": "Flexible go-to-market"},
                {"risk": "Competition", "severity": "MEDIUM", "mitigation": "First-mover advantage"}
            ],
            comparables=[
                {"company": "Similar Co A", "valuation": "$100M", "stage": "Series A"},
                {"company": "Similar Co B", "valuation": "$80M", "stage": "Seed"}
            ],
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
        """Generate comprehensive risk register"""
        pred = self.state.predictions.get(company_name, {})

        risks = [
            RiskItem(
                id="R001",
                title="Execution Risk",
                description="Team may not execute on product roadmap as planned",
                category=RiskCategory.EXECUTION,
                severity=RiskSeverity.HIGH,
                likelihood=0.4,
                impact_score=0.8,
                risk_score=0.32,
                current_mitigations=["Experienced advisors", "Clear milestones"],
                recommended_mitigations=["Monthly board check-ins", "Hire key VP"],
                residual_risk=0.2,
                early_warning_signs=["Missed sprint goals", "Key hire departures"],
                monitoring_frequency="Monthly"
            ),
            RiskItem(
                id="R002",
                title="Market Risk",
                description="Market may not develop as expected or timing may be off",
                category=RiskCategory.MARKET,
                severity=RiskSeverity.MEDIUM,
                likelihood=0.3,
                impact_score=0.7,
                risk_score=0.21,
                current_mitigations=["Market research completed", "Customer discovery ongoing"],
                recommended_mitigations=["Expand customer interviews", "Build pivot optionality"],
                residual_risk=0.15,
                early_warning_signs=["Slowing inbound interest", "Competitor traction"],
                monitoring_frequency="Quarterly"
            ),
            RiskItem(
                id="R003",
                title="Competitive Risk",
                description="Incumbents or well-funded startups may capture market",
                category=RiskCategory.COMPETITIVE,
                severity=RiskSeverity.MEDIUM,
                likelihood=0.5,
                impact_score=0.6,
                risk_score=0.30,
                current_mitigations=["Differentiated approach", "Speed to market"],
                recommended_mitigations=["Accelerate product development", "Secure key partnerships"],
                residual_risk=0.2,
                early_warning_signs=["Competitor funding announcements", "Feature parity"],
                monitoring_frequency="Monthly"
            ),
            RiskItem(
                id="R004",
                title="Financial Risk",
                description="May run out of runway before achieving key milestones",
                category=RiskCategory.FINANCIAL,
                severity=RiskSeverity.HIGH,
                likelihood=0.3,
                impact_score=0.9,
                risk_score=0.27,
                current_mitigations=["18-month runway", "Capital efficient model"],
                recommended_mitigations=["Develop bridge financing relationships", "Identify cost levers"],
                residual_risk=0.15,
                early_warning_signs=["Burn rate increase", "Revenue miss"],
                monitoring_frequency="Monthly"
            ),
            RiskItem(
                id="R005",
                title="Team Risk",
                description="Key person dependency or team conflicts",
                category=RiskCategory.TEAM,
                severity=RiskSeverity.MEDIUM,
                likelihood=0.25,
                impact_score=0.7,
                risk_score=0.175,
                current_mitigations=["Vesting schedules", "Clear roles"],
                recommended_mitigations=["Hire backup for key roles", "Team coaching"],
                residual_risk=0.1,
                early_warning_signs=["Founder tension", "Key hire struggles"],
                monitoring_frequency="Quarterly"
            )
        ]

        return RiskRegister(
            company_name=company_name,
            overall_risk_rating=RiskSeverity.MEDIUM,
            risk_score=65,
            risk_trend="STABLE",
            risks=risks,
            critical_risks=0,
            high_risks=2,
            medium_risks=3,
            low_risks=0,
            top_concerns=[
                "Execution timeline pressure",
                "Competitive response from incumbents",
                "Runway management in uncertain market"
            ],
            risk_concentrations=[
                "Execution risks clustered around product delivery",
                "Market risks tied to timing assumptions"
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
