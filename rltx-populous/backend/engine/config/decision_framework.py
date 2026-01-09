"""
Enterprise Decision Framework Configuration

This is the CORE of what makes this worth $5-10M.

Enterprise customers PAY for:
1. Customization to THEIR decision process, not a generic one
2. Integration with THEIR data sources
3. THEIR risk tolerance and investment thesis baked in
4. Accountability and audit trails

This module provides the configuration layer that transforms a generic
prediction engine into THEIR decision intelligence platform.
"""

from typing import Dict, List, Optional, Any, Callable
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import json


class UseCase(str, Enum):
    """Primary use cases - each has different factor weightings and outputs"""
    VC_INVESTMENT = "vc_investment"  # Early-stage startup evaluation
    PE_DUE_DILIGENCE = "pe_due_diligence"  # Private equity acquisition
    MA_EVALUATION = "ma_evaluation"  # M&A target assessment
    VENDOR_SELECTION = "vendor_selection"  # B2B vendor/partner risk
    MARKET_ENTRY = "market_entry"  # New market opportunity analysis
    PORTFOLIO_MONITORING = "portfolio_monitoring"  # Existing portfolio health
    COMPETITIVE_INTEL = "competitive_intel"  # Competitor threat assessment
    DEFENSE_PROCUREMENT = "defense_procurement"  # Defense/Gov contractor eval


class RiskProfile(str, Enum):
    """Organization's risk tolerance"""
    AGGRESSIVE = "aggressive"  # High risk, high return focus
    MODERATE = "moderate"  # Balanced approach
    CONSERVATIVE = "conservative"  # Capital preservation focus
    INSTITUTIONAL = "institutional"  # Fiduciary duty constraints


class DataSourceConfig(BaseModel):
    """Configuration for external data integrations"""
    # Market Data
    bloomberg_enabled: bool = False
    bloomberg_api_key: Optional[str] = None
    pitchbook_enabled: bool = False
    pitchbook_api_key: Optional[str] = None
    crunchbase_enabled: bool = False
    crunchbase_api_key: Optional[str] = None

    # News & Sentiment
    exa_enabled: bool = True
    exa_api_key: Optional[str] = None
    news_api_enabled: bool = False
    news_api_key: Optional[str] = None

    # Alternative Data
    linkedin_enabled: bool = False
    github_enabled: bool = True
    glassdoor_enabled: bool = False

    # Internal Data
    salesforce_integration: bool = False
    internal_crm_endpoint: Optional[str] = None
    internal_data_lake: Optional[str] = None


class FactorWeighting(BaseModel):
    """Customizable factor weights for scoring model"""
    # Core factors - must sum to 1.0
    team_weight: float = 0.30
    market_weight: float = 0.25
    traction_weight: float = 0.20
    timing_weight: float = 0.15
    capital_weight: float = 0.10

    # Sub-factor weights (within each category)
    # Team sub-factors
    founder_experience_weight: float = 0.35
    team_completeness_weight: float = 0.25
    domain_expertise_weight: float = 0.25
    execution_track_record_weight: float = 0.15

    # Market sub-factors
    tam_weight: float = 0.30
    growth_rate_weight: float = 0.25
    competitive_dynamics_weight: float = 0.25
    regulatory_risk_weight: float = 0.20

    # Traction sub-factors
    revenue_growth_weight: float = 0.35
    user_engagement_weight: float = 0.25
    unit_economics_weight: float = 0.25
    product_market_fit_weight: float = 0.15

    def validate_weights(self) -> bool:
        """Ensure weights sum to 1.0"""
        total = (self.team_weight + self.market_weight +
                 self.traction_weight + self.timing_weight + self.capital_weight)
        return abs(total - 1.0) < 0.01


class InvestmentCriteria(BaseModel):
    """Organization's investment thesis and criteria"""
    # Stage preferences
    target_stages: List[str] = ["seed", "series_a", "series_b"]

    # Sector focus
    target_sectors: List[str] = ["ai", "fintech", "healthcare", "enterprise_saas"]
    excluded_sectors: List[str] = ["crypto", "cannabis", "gambling"]

    # Geographic focus
    target_geographies: List[str] = ["US", "EU", "Canada"]

    # Valuation constraints
    max_pre_money_valuation: float = 50_000_000  # $50M
    min_ownership_target: float = 0.10  # 10%
    max_ownership_target: float = 0.25  # 25%

    # Check size
    min_check_size: float = 500_000  # $500K
    max_check_size: float = 5_000_000  # $5M

    # Return requirements
    target_irr: float = 0.30  # 30%
    target_multiple: float = 10.0  # 10x

    # Risk thresholds
    max_acceptable_risk_score: float = 0.7  # 70/100
    min_prediction_confidence: float = 0.6  # 60%

    # Deal breakers
    deal_breakers: List[str] = [
        "no_technical_cofounder",
        "single_founder",
        "regulatory_uncertainty",
        "no_clear_moat"
    ]


class ThresholdConfig(BaseModel):
    """Recommendation thresholds - customizable per organization"""
    # Probability thresholds for recommendations
    strong_yes_threshold: float = 0.15  # >15% unicorn probability
    yes_threshold: float = 0.08  # >8%
    conditional_threshold: float = 0.04  # >4%
    no_threshold: float = 0.02  # >2%
    # Below no_threshold = STRONG_NO

    # Risk thresholds
    critical_risk_threshold: float = 0.8
    high_risk_threshold: float = 0.6
    medium_risk_threshold: float = 0.4

    # Confidence thresholds
    high_confidence_threshold: float = 0.8
    medium_confidence_threshold: float = 0.6


class OutputConfig(BaseModel):
    """Customize what outputs are generated"""
    # Deliverables to generate
    generate_investment_memo: bool = True
    generate_risk_register: bool = True
    generate_decision_matrix: bool = True
    generate_executive_brief: bool = True
    generate_scenario_analysis: bool = True
    generate_action_playbook: bool = False

    # Branding
    company_name: str = "Investment Committee"
    company_logo_url: Optional[str] = None

    # Format preferences
    currency: str = "USD"
    date_format: str = "%Y-%m-%d"
    number_format: str = ",.2f"

    # Confidentiality
    classification: str = "CONFIDENTIAL"
    distribution_list: List[str] = ["Investment Committee"]


class WorkflowConfig(BaseModel):
    """Decision workflow configuration"""
    # Approval workflow
    require_dual_approval: bool = True
    approval_roles: List[str] = ["Partner", "Investment Committee"]

    # Audit requirements
    capture_audit_trail: bool = True
    version_control_enabled: bool = True

    # Notifications
    slack_webhook: Optional[str] = None
    email_notifications: List[str] = []

    # Integration hooks
    pre_decision_webhook: Optional[str] = None
    post_decision_webhook: Optional[str] = None


class DecisionFramework(BaseModel):
    """
    Complete decision framework configuration.

    This is what makes the platform worth $5-10M:
    - Fully customizable to organization's needs
    - Integrates with their data sources
    - Reflects their investment thesis
    - Produces their required outputs
    - Fits their workflow
    """
    # Identity
    framework_id: str = Field(default_factory=lambda: f"df_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    framework_name: str = "Default Framework"
    organization: str = "Default Organization"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0.0"

    # Core Configuration
    use_case: UseCase = UseCase.VC_INVESTMENT
    risk_profile: RiskProfile = RiskProfile.MODERATE

    # Sub-configurations
    data_sources: DataSourceConfig = Field(default_factory=DataSourceConfig)
    factor_weights: FactorWeighting = Field(default_factory=FactorWeighting)
    investment_criteria: InvestmentCriteria = Field(default_factory=InvestmentCriteria)
    thresholds: ThresholdConfig = Field(default_factory=ThresholdConfig)
    outputs: OutputConfig = Field(default_factory=OutputConfig)
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)

    # Custom scoring adjustments
    sector_multipliers: Dict[str, float] = Field(default_factory=lambda: {
        "ai": 1.2,
        "fintech": 1.1,
        "healthcare": 1.0,
        "enterprise_saas": 1.0,
        "consumer": 0.9,
        "hardware": 0.8
    })

    # Custom rules
    custom_rules: List[Dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# PRESET FRAMEWORKS FOR DIFFERENT USE CASES
# =============================================================================

def create_vc_framework(
    firm_name: str = "Venture Fund",
    target_stages: List[str] = ["seed", "series_a"],
    check_size_range: tuple = (500_000, 5_000_000),
    target_ownership: float = 0.15
) -> DecisionFramework:
    """Create a VC-optimized decision framework"""
    return DecisionFramework(
        framework_name=f"{firm_name} Investment Framework",
        organization=firm_name,
        use_case=UseCase.VC_INVESTMENT,
        risk_profile=RiskProfile.MODERATE,
        factor_weights=FactorWeighting(
            team_weight=0.35,  # VCs weight team heavily
            market_weight=0.25,
            traction_weight=0.20,
            timing_weight=0.12,
            capital_weight=0.08
        ),
        investment_criteria=InvestmentCriteria(
            target_stages=target_stages,
            min_check_size=check_size_range[0],
            max_check_size=check_size_range[1],
            min_ownership_target=target_ownership - 0.05,
            max_ownership_target=target_ownership + 0.10,
            target_irr=0.30,
            target_multiple=10.0
        ),
        thresholds=ThresholdConfig(
            strong_yes_threshold=0.12,
            yes_threshold=0.06,
            conditional_threshold=0.03
        )
    )


def create_pe_framework(
    firm_name: str = "PE Fund",
    min_revenue: float = 10_000_000,
    target_ebitda_margin: float = 0.15
) -> DecisionFramework:
    """Create a PE-optimized decision framework (growth equity focus)"""
    return DecisionFramework(
        framework_name=f"{firm_name} Due Diligence Framework",
        organization=firm_name,
        use_case=UseCase.PE_DUE_DILIGENCE,
        risk_profile=RiskProfile.CONSERVATIVE,
        factor_weights=FactorWeighting(
            team_weight=0.20,  # PE cares more about metrics
            market_weight=0.20,
            traction_weight=0.35,  # Revenue/EBITDA focus
            timing_weight=0.10,
            capital_weight=0.15  # Capital efficiency matters
        ),
        investment_criteria=InvestmentCriteria(
            target_stages=["growth", "late_stage"],
            target_irr=0.25,  # Lower IRR target for PE
            target_multiple=3.0,  # 3x is good for PE
            max_acceptable_risk_score=0.5  # More conservative
        ),
        thresholds=ThresholdConfig(
            strong_yes_threshold=0.20,  # Higher bar
            yes_threshold=0.12,
            conditional_threshold=0.08
        )
    )


def create_ma_framework(
    acquirer_name: str = "Acquirer Corp",
    strategic_focus: List[str] = ["technology", "talent", "market_access"]
) -> DecisionFramework:
    """Create an M&A-optimized decision framework"""
    return DecisionFramework(
        framework_name=f"{acquirer_name} M&A Evaluation Framework",
        organization=acquirer_name,
        use_case=UseCase.MA_EVALUATION,
        risk_profile=RiskProfile.INSTITUTIONAL,
        factor_weights=FactorWeighting(
            team_weight=0.25,  # Integration risk
            market_weight=0.30,  # Strategic fit
            traction_weight=0.25,  # Synergy potential
            timing_weight=0.10,
            capital_weight=0.10
        ),
        outputs=OutputConfig(
            generate_investment_memo=True,
            generate_risk_register=True,
            generate_decision_matrix=True,
            generate_scenario_analysis=True,
            generate_action_playbook=True  # Integration playbook
        )
    )


def create_defense_framework(
    agency_name: str = "Defense Agency",
    security_clearance_required: bool = True
) -> DecisionFramework:
    """Create a Defense/Government procurement framework"""
    return DecisionFramework(
        framework_name=f"{agency_name} Contractor Evaluation Framework",
        organization=agency_name,
        use_case=UseCase.DEFENSE_PROCUREMENT,
        risk_profile=RiskProfile.INSTITUTIONAL,
        factor_weights=FactorWeighting(
            team_weight=0.30,  # Security clearances
            market_weight=0.15,
            traction_weight=0.20,  # Past performance
            timing_weight=0.10,
            capital_weight=0.25  # Financial stability critical
        ),
        investment_criteria=InvestmentCriteria(
            deal_breakers=[
                "foreign_ownership",
                "no_security_clearance",
                "financial_instability",
                "compliance_issues"
            ]
        ),
        outputs=OutputConfig(
            classification="SECRET",
            company_name=agency_name
        )
    )


def create_vendor_selection_framework(
    company_name: str = "Enterprise Corp",
    budget_range: tuple = (1_000_000, 10_000_000)
) -> DecisionFramework:
    """Create a vendor/partner selection framework"""
    return DecisionFramework(
        framework_name=f"{company_name} Vendor Evaluation Framework",
        organization=company_name,
        use_case=UseCase.VENDOR_SELECTION,
        risk_profile=RiskProfile.CONSERVATIVE,
        factor_weights=FactorWeighting(
            team_weight=0.20,  # Support team quality
            market_weight=0.15,  # Market position
            traction_weight=0.30,  # Customer success
            timing_weight=0.10,
            capital_weight=0.25  # Financial stability
        ),
        outputs=OutputConfig(
            generate_investment_memo=False,
            generate_risk_register=True,
            generate_decision_matrix=True,
            generate_executive_brief=True,
            generate_action_playbook=True  # Vendor onboarding
        )
    )


# =============================================================================
# FRAMEWORK MANAGER
# =============================================================================

class FrameworkManager:
    """
    Manages decision frameworks for an organization.

    In production, this would persist to database and handle:
    - Multi-tenant framework storage
    - Version control
    - Access control
    - Audit logging
    """

    def __init__(self):
        self._frameworks: Dict[str, DecisionFramework] = {}
        self._default_framework_id: Optional[str] = None

    def register_framework(self, framework: DecisionFramework) -> str:
        """Register a new framework"""
        self._frameworks[framework.framework_id] = framework
        if self._default_framework_id is None:
            self._default_framework_id = framework.framework_id
        return framework.framework_id

    def get_framework(self, framework_id: str) -> Optional[DecisionFramework]:
        """Get a framework by ID"""
        return self._frameworks.get(framework_id)

    def get_default_framework(self) -> DecisionFramework:
        """Get the default framework"""
        if self._default_framework_id and self._default_framework_id in self._frameworks:
            return self._frameworks[self._default_framework_id]
        return DecisionFramework()  # Return default if none registered

    def list_frameworks(self) -> List[Dict[str, str]]:
        """List all registered frameworks"""
        return [
            {
                "id": f.framework_id,
                "name": f.framework_name,
                "organization": f.organization,
                "use_case": f.use_case.value
            }
            for f in self._frameworks.values()
        ]

    def export_framework(self, framework_id: str) -> str:
        """Export framework as JSON"""
        framework = self.get_framework(framework_id)
        if framework:
            return framework.model_dump_json(indent=2)
        return "{}"

    def import_framework(self, json_str: str) -> str:
        """Import framework from JSON"""
        framework = DecisionFramework.model_validate_json(json_str)
        return self.register_framework(framework)


# Global framework manager instance
framework_manager = FrameworkManager()

# Register default frameworks
framework_manager.register_framework(create_vc_framework())
