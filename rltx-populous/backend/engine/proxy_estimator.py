"""
Proxy Estimation Engine
Estimates missing metrics using proxy signals and industry benchmarks
"""

import math
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from backend.engine.data_sources import (
    CompanyData, DataPoint, DataConfidence,
    FounderData, TractionData, FundingData, MarketData
)


# =============================================================================
# INDUSTRY BENCHMARKS
# =============================================================================

class BusinessModel(Enum):
    B2B_SAAS = "b2b_saas"
    B2C_SAAS = "b2c_saas"
    MARKETPLACE = "marketplace"
    CONSUMER = "consumer"
    FINTECH = "fintech"
    ENTERPRISE = "enterprise"
    DEV_TOOLS = "dev_tools"
    HARDWARE = "hardware"
    UNKNOWN = "unknown"


# Revenue per employee benchmarks by business model and stage
REVENUE_PER_EMPLOYEE = {
    BusinessModel.B2B_SAAS: {"early": 80_000, "growth": 180_000, "mature": 280_000},
    BusinessModel.B2C_SAAS: {"early": 60_000, "growth": 150_000, "mature": 250_000},
    BusinessModel.MARKETPLACE: {"early": 200_000, "growth": 400_000, "mature": 600_000},
    BusinessModel.CONSUMER: {"early": 50_000, "growth": 120_000, "mature": 200_000},
    BusinessModel.FINTECH: {"early": 100_000, "growth": 250_000, "mature": 400_000},
    BusinessModel.ENTERPRISE: {"early": 120_000, "growth": 220_000, "mature": 350_000},
    BusinessModel.DEV_TOOLS: {"early": 90_000, "growth": 200_000, "mature": 300_000},
    BusinessModel.HARDWARE: {"early": 80_000, "growth": 160_000, "mature": 250_000},
    BusinessModel.UNKNOWN: {"early": 80_000, "growth": 150_000, "mature": 220_000},
}

# User-to-revenue conversion rates
USER_REVENUE_RATES = {
    BusinessModel.B2B_SAAS: 500,      # $500 ARPU
    BusinessModel.B2C_SAAS: 50,       # $50 ARPU
    BusinessModel.MARKETPLACE: 20,    # $20 per user GMV contribution
    BusinessModel.CONSUMER: 10,       # $10 ARPU (ads/freemium)
    BusinessModel.FINTECH: 200,       # $200 ARPU
    BusinessModel.DEV_TOOLS: 100,     # $100 ARPU
    BusinessModel.UNKNOWN: 100,
}

# Market size benchmarks (fallback TAM in billions)
DEFAULT_TAM_BY_INDUSTRY = {
    "fintech": 150,
    "developer tools": 50,
    "enterprise software": 200,
    "saas": 150,
    "ai": 500,
    "machine learning": 200,
    "healthcare": 300,
    "edtech": 50,
    "ecommerce": 400,
    "cybersecurity": 150,
    "data": 100,
    "cloud": 200,
    "marketing": 80,
    "hr": 50,
    "default": 30,
}

# Education tier definitions
TIER_1_SCHOOLS = {
    "stanford", "mit", "harvard", "berkeley", "caltech", "princeton",
    "yale", "columbia", "carnegie mellon", "cmu", "cornell", "oxford", "cambridge"
}

TIER_2_SCHOOLS = {
    "ucla", "michigan", "ut austin", "georgia tech", "uiuc", "penn",
    "duke", "northwestern", "nyu", "usc", "brown", "dartmouth", "rice"
}

# Top company experience
TOP_COMPANIES = {
    "google", "meta", "facebook", "apple", "amazon", "microsoft", "netflix",
    "stripe", "airbnb", "uber", "coinbase", "robinhood", "snap", "twitter",
    "linkedin", "salesforce", "adobe", "nvidia", "tesla", "spacex",
    "palantir", "databricks", "snowflake", "figma", "notion", "slack"
}


# =============================================================================
# PROXY ESTIMATION ENGINE
# =============================================================================

@dataclass
class EstimatedMetric:
    """A metric that was estimated using proxies"""
    value: Any
    confidence: float  # 0-1
    method: str
    inputs: Dict[str, Any]
    reasoning: str


class ProxyEstimator:
    """
    Estimates missing metrics using proxy signals and benchmarks
    """

    def __init__(self):
        pass

    def estimate_all(self, company: CompanyData) -> Dict[str, EstimatedMetric]:
        """
        Estimate all missing metrics for a company
        Returns dict of metric_name -> EstimatedMetric
        """
        estimates = {}

        # Determine business model
        business_model = self._infer_business_model(company)
        stage = self._infer_stage(company)

        # Estimate revenue if missing
        if not self._has_value(company.traction.revenue_annual) and not self._has_value(company.traction.revenue_monthly):
            revenue_est = self._estimate_revenue(company, business_model, stage)
            if revenue_est:
                estimates["revenue_annual"] = revenue_est

        # Estimate employee count if missing
        if not self._has_value(company.employee_count):
            emp_est = self._estimate_employees(company)
            if emp_est:
                estimates["employee_count"] = emp_est

        # Estimate user count if missing
        if not self._has_value(company.traction.user_count) and not self._has_value(company.traction.customer_count):
            user_est = self._estimate_users(company, business_model)
            if user_est:
                estimates["user_count"] = user_est

        # Estimate TAM if missing
        if not self._has_value(company.market.tam):
            tam_est = self._estimate_tam(company)
            if tam_est:
                estimates["tam"] = tam_est

        # Estimate valuation if missing
        if not self._has_value(company.funding.last_valuation):
            val_est = self._estimate_valuation(company, estimates)
            if val_est:
                estimates["valuation"] = val_est

        # Estimate growth rate if missing
        if not self._has_value(company.traction.revenue_growth_rate):
            growth_est = self._estimate_growth_rate(company, stage)
            if growth_est:
                estimates["growth_rate"] = growth_est

        return estimates

    def _estimate_revenue(self, company: CompanyData, business_model: BusinessModel, stage: str) -> Optional[EstimatedMetric]:
        """Estimate annual revenue using multiple proxy methods"""
        estimates = []
        methods_used = []

        # Method 1: Employee count × Revenue per employee
        if self._has_value(company.employee_count):
            emp_count = self._get_value(company.employee_count)
            rev_per_emp = REVENUE_PER_EMPLOYEE.get(business_model, REVENUE_PER_EMPLOYEE[BusinessModel.UNKNOWN]).get(stage, 100_000)
            est = emp_count * rev_per_emp
            estimates.append((est, 0.5, "employee_count"))
            methods_used.append(f"employees({emp_count}) × ${rev_per_emp:,}/emp")

        # Method 2: User count × ARPU
        if self._has_value(company.traction.user_count):
            users = self._get_value(company.traction.user_count)
            arpu = USER_REVENUE_RATES.get(business_model, 100)
            est = users * arpu
            estimates.append((est, 0.4, "user_arpu"))
            methods_used.append(f"users({users:,}) × ${arpu} ARPU")

        # Method 3: Customer count × Enterprise ARPU
        if self._has_value(company.traction.customer_count):
            customers = self._get_value(company.traction.customer_count)
            # B2B typically $5-50K per customer
            arpu = 20_000 if business_model in [BusinessModel.B2B_SAAS, BusinessModel.ENTERPRISE] else 5_000
            est = customers * arpu
            estimates.append((est, 0.5, "customer_arpu"))
            methods_used.append(f"customers({customers:,}) × ${arpu:,}")

        # Method 4: Funding efficiency (funding × typical revenue multiple at stage)
        if self._has_value(company.funding.total_raised):
            total_raised = self._get_value(company.funding.total_raised)
            # Typical ARR/funding ratios
            efficiency = {"early": 0.2, "growth": 0.5, "mature": 1.0}.get(stage, 0.3)
            est = total_raised * efficiency
            estimates.append((est, 0.3, "funding_efficiency"))
            methods_used.append(f"raised(${total_raised/1e6:.1f}M) × {efficiency} efficiency")

        # Method 5: GitHub stars (for dev tools)
        if self._has_value(company.traction.github_stars) and business_model == BusinessModel.DEV_TOOLS:
            stars = self._get_value(company.traction.github_stars)
            # Rough heuristic: popular OSS projects ~$100-1000 per star in commercial value
            est = stars * 500  # Conservative estimate
            estimates.append((est, 0.3, "github_stars"))
            methods_used.append(f"stars({stars:,}) × $500")

        if not estimates:
            return None

        # Weighted average
        total_weight = sum(e[1] for e in estimates)
        weighted_avg = sum(e[0] * e[1] for e in estimates) / total_weight

        # Confidence based on number of methods and their individual confidences
        confidence = min(0.7, total_weight / len(estimates) * 0.5 + len(estimates) * 0.1)

        return EstimatedMetric(
            value=weighted_avg,
            confidence=confidence,
            method="weighted_average",
            inputs={"methods": methods_used, "estimates": [e[0] for e in estimates]},
            reasoning=f"Estimated using {len(estimates)} proxy methods: " + ", ".join(methods_used)
        )

    def _estimate_employees(self, company: CompanyData) -> Optional[EstimatedMetric]:
        """Estimate employee count from funding or revenue"""
        estimates = []

        # Method 1: From funding (typical team size at each stage)
        if self._has_value(company.funding.total_raised):
            raised = self._get_value(company.funding.total_raised)
            # Rough heuristic: $200K-500K per employee in burn
            if raised < 2_000_000:
                est = max(3, raised / 200_000)
            elif raised < 10_000_000:
                est = raised / 300_000
            elif raised < 50_000_000:
                est = raised / 400_000
            else:
                est = raised / 500_000
            estimates.append((est, 0.4))

        # Method 2: From last round type
        if self._has_value(company.funding.last_round_type):
            round_type = str(self._get_value(company.funding.last_round_type)).lower()
            typical_sizes = {
                "pre-seed": 4, "seed": 8, "series a": 25,
                "series b": 60, "series c": 150, "series d": 300
            }
            for rt, size in typical_sizes.items():
                if rt in round_type:
                    estimates.append((size, 0.3))
                    break

        if not estimates:
            return None

        avg = sum(e[0] for e in estimates) / len(estimates)
        confidence = min(0.5, sum(e[1] for e in estimates) / len(estimates))

        return EstimatedMetric(
            value=int(avg),
            confidence=confidence,
            method="funding_stage",
            inputs={"estimates": estimates},
            reasoning=f"Estimated {int(avg)} employees based on funding stage"
        )

    def _estimate_users(self, company: CompanyData, business_model: BusinessModel) -> Optional[EstimatedMetric]:
        """Estimate user/customer count from various signals"""
        estimates = []

        # Method 1: From GitHub stars (for dev tools)
        if self._has_value(company.traction.github_stars):
            stars = self._get_value(company.traction.github_stars)
            # Active users typically 10-50% of stars
            est = stars * 0.2
            estimates.append((est, 0.4, f"github_stars({stars}) × 0.2"))

        # Method 2: From Product Hunt upvotes
        if self._has_value(company.traction.product_hunt_upvotes):
            upvotes = self._get_value(company.traction.product_hunt_upvotes)
            # Each upvote ~ 10-50 actual users
            est = upvotes * 30
            estimates.append((est, 0.3, f"ph_upvotes({upvotes}) × 30"))

        # Method 3: From G2 reviews (B2B)
        if self._has_value(company.traction.g2_reviews):
            reviews = self._get_value(company.traction.g2_reviews)
            if isinstance(reviews, dict):
                review_count = reviews.get("value", reviews.get("review_count", 0))
            else:
                review_count = reviews
            # 1 review per ~50 customers
            est = review_count * 50
            estimates.append((est, 0.4, f"g2_reviews({review_count}) × 50"))

        # Method 4: From funding (typical user metrics at stage)
        if self._has_value(company.funding.total_raised):
            raised = self._get_value(company.funding.total_raised)
            if business_model in [BusinessModel.B2B_SAAS, BusinessModel.ENTERPRISE]:
                # B2B: fewer customers, higher value
                est = raised / 10_000  # ~$10K per customer
            else:
                # Consumer: more users, lower value
                est = raised / 100  # ~$100 per user acquired
            estimates.append((est, 0.25, f"funding/${raised/1e6:.1f}M"))

        if not estimates:
            return None

        avg = sum(e[0] for e in estimates) / len(estimates)
        confidence = min(0.5, len(estimates) * 0.15)

        return EstimatedMetric(
            value=int(avg),
            confidence=confidence,
            method="proxy_signals",
            inputs={"methods": [e[2] for e in estimates]},
            reasoning=f"Estimated {int(avg):,} users from {len(estimates)} proxy signals"
        )

    def _estimate_tam(self, company: CompanyData) -> Optional[EstimatedMetric]:
        """Estimate TAM from industry/market information"""
        if self._has_value(company.industry):
            industry = str(self._get_value(company.industry)).lower()

            # Find best matching industry TAM
            for ind_key, tam_billions in DEFAULT_TAM_BY_INDUSTRY.items():
                if ind_key in industry:
                    return EstimatedMetric(
                        value=tam_billions * 1e9,
                        confidence=0.4,
                        method="industry_benchmark",
                        inputs={"industry": industry, "benchmark": ind_key},
                        reasoning=f"${tam_billions}B TAM for {ind_key} industry"
                    )

        # Default TAM
        return EstimatedMetric(
            value=30e9,
            confidence=0.2,
            method="default",
            inputs={},
            reasoning="Default $30B TAM (insufficient industry data)"
        )

    def _estimate_valuation(self, company: CompanyData, estimates: Dict[str, EstimatedMetric]) -> Optional[EstimatedMetric]:
        """Estimate valuation from funding and revenue"""
        vals = []

        # Method 1: From last round (typical step-up)
        if self._has_value(company.funding.last_round_amount):
            amount = self._get_value(company.funding.last_round_amount)
            # Typical 20% dilution = 5x post-money multiple
            est = amount * 5
            vals.append((est, 0.5, "round_dilution"))

        # Method 2: From total raised (at typical efficiency)
        if self._has_value(company.funding.total_raised):
            raised = self._get_value(company.funding.total_raised)
            # Companies typically worth 3-6x their total raised
            est = raised * 4
            vals.append((est, 0.4, "funding_multiple"))

        # Method 3: From revenue (SaaS multiples)
        if "revenue_annual" in estimates:
            revenue = estimates["revenue_annual"].value
            # SaaS: 10-20x ARR, adjust by growth
            multiple = 12
            est = revenue * multiple
            vals.append((est, 0.5, "revenue_multiple"))
        elif self._has_value(company.traction.revenue_annual):
            revenue = self._get_value(company.traction.revenue_annual)
            est = revenue * 12
            vals.append((est, 0.6, "revenue_multiple"))

        if not vals:
            return None

        avg = sum(v[0] for v in vals) / len(vals)
        confidence = min(0.6, sum(v[1] for v in vals) / len(vals))

        return EstimatedMetric(
            value=avg,
            confidence=confidence,
            method="multi_method",
            inputs={"methods": [v[2] for v in vals]},
            reasoning=f"${avg/1e6:.1f}M valuation from {len(vals)} methods"
        )

    def _estimate_growth_rate(self, company: CompanyData, stage: str) -> Optional[EstimatedMetric]:
        """Estimate growth rate from stage and signals"""
        # Default growth rates by stage
        stage_growth = {
            "early": 0.15,   # 15% MoM = 435% YoY
            "growth": 0.08,  # 8% MoM = 152% YoY
            "mature": 0.03,  # 3% MoM = 43% YoY
        }

        base_growth = stage_growth.get(stage, 0.08)

        # Adjust based on signals
        adjustments = []

        # Recent funding = likely growth investment
        if self._has_value(company.funding.last_round_date):
            date_str = self._get_value(company.funding.last_round_date)
            # If raised recently, likely growing faster
            base_growth *= 1.2
            adjustments.append("recent_funding")

        # Product signals suggest momentum
        if self._has_value(company.traction.github_stars):
            stars = self._get_value(company.traction.github_stars)
            if stars > 5000:
                base_growth *= 1.3
                adjustments.append("high_github_stars")

        if self._has_value(company.traction.product_hunt_upvotes):
            upvotes = self._get_value(company.traction.product_hunt_upvotes)
            if upvotes > 500:
                base_growth *= 1.2
                adjustments.append("ph_traction")

        return EstimatedMetric(
            value=base_growth,
            confidence=0.3,
            method="stage_benchmark",
            inputs={"stage": stage, "adjustments": adjustments},
            reasoning=f"{base_growth*100:.1f}% monthly growth for {stage} stage"
        )

    # =============================================================================
    # HELPER METHODS
    # =============================================================================

    def _has_value(self, dp: Optional[DataPoint]) -> bool:
        """Check if a DataPoint has a non-null value"""
        return dp is not None and dp.value is not None

    def _get_value(self, dp: DataPoint) -> Any:
        """Extract value from DataPoint"""
        return dp.value

    def _infer_business_model(self, company: CompanyData) -> BusinessModel:
        """Infer business model from company data"""
        if self._has_value(company.business_model):
            model = str(self._get_value(company.business_model)).lower()

            if "marketplace" in model:
                return BusinessModel.MARKETPLACE
            if "consumer" in model or "b2c" in model:
                return BusinessModel.CONSUMER
            if "enterprise" in model:
                return BusinessModel.ENTERPRISE
            if "fintech" in model or "financial" in model:
                return BusinessModel.FINTECH
            if "developer" in model or "api" in model or "dev tool" in model:
                return BusinessModel.DEV_TOOLS
            if "hardware" in model:
                return BusinessModel.HARDWARE
            if "saas" in model or "b2b" in model:
                return BusinessModel.B2B_SAAS

        # Infer from industry
        if self._has_value(company.industry):
            industry = str(self._get_value(company.industry)).lower()

            if "fintech" in industry or "payment" in industry:
                return BusinessModel.FINTECH
            if "developer" in industry or "api" in industry:
                return BusinessModel.DEV_TOOLS
            if "consumer" in industry:
                return BusinessModel.CONSUMER
            if "enterprise" in industry:
                return BusinessModel.ENTERPRISE

        # Infer from signals
        if self._has_value(company.traction.github_stars):
            return BusinessModel.DEV_TOOLS

        return BusinessModel.B2B_SAAS  # Default

    def _infer_stage(self, company: CompanyData) -> str:
        """Infer company stage from funding and signals"""
        # From round type
        if self._has_value(company.funding.last_round_type):
            round_type = str(self._get_value(company.funding.last_round_type)).lower()
            if "seed" in round_type or "pre" in round_type:
                return "early"
            if "series a" in round_type or "series b" in round_type:
                return "growth"
            if "series c" in round_type or "series d" in round_type:
                return "mature"

        # From funding amount
        if self._has_value(company.funding.total_raised):
            raised = self._get_value(company.funding.total_raised)
            if raised < 5_000_000:
                return "early"
            if raised < 50_000_000:
                return "growth"
            return "mature"

        # From employee count
        if self._has_value(company.employee_count):
            emp = self._get_value(company.employee_count)
            if emp < 20:
                return "early"
            if emp < 100:
                return "growth"
            return "mature"

        return "early"  # Default


# =============================================================================
# SCORING ENGINE
# =============================================================================

class ScoringEngine:
    """
    Convert extracted and estimated data into prediction scores
    """

    def __init__(self):
        self.estimator = ProxyEstimator()

    def score_team(self, company: CompanyData) -> Tuple[float, float, Dict]:
        """
        Score team quality (0-1) with confidence
        Returns: (score, confidence, breakdown)
        """
        scores = []
        breakdown = {}

        for founder in company.founders:
            founder_score = 0.0

            # Prior exits (major factor)
            if founder.prior_exits:
                exit_count = len(founder.prior_exits)
                exit_score = min(0.3, exit_count * 0.15)
                founder_score += exit_score
                breakdown[f"{founder.name}_exits"] = exit_count

                # Exit values
                if founder.prior_exit_values:
                    max_exit = max(
                        self._get_value_safe(ev, 0)
                        for ev in founder.prior_exit_values
                    )
                    if max_exit > 100_000_000:
                        founder_score += 0.15
                    elif max_exit > 10_000_000:
                        founder_score += 0.08

            # Experience
            if founder.years_experience:
                years = self._get_value_safe(founder.years_experience, 0)
                exp_score = min(0.15, years * 0.015)
                founder_score += exp_score
                breakdown[f"{founder.name}_years_exp"] = years

            # Education
            if founder.education_tier:
                tier = self._get_value_safe(founder.education_tier, 3)
                if tier == 1:
                    founder_score += 0.05
                    breakdown[f"{founder.name}_edu"] = "tier1"
                elif tier == 2:
                    founder_score += 0.03
                    breakdown[f"{founder.name}_edu"] = "tier2"

            # Top company experience
            if founder.top_company_experience:
                if self._get_value_safe(founder.top_company_experience, False):
                    founder_score += 0.05
                    breakdown[f"{founder.name}_top_co"] = True

            # YC alumni
            if founder.yc_alumni:
                if self._get_value_safe(founder.yc_alumni, False):
                    founder_score += 0.10
                    breakdown[f"{founder.name}_yc"] = True

            # Technical background (for tech companies)
            if founder.technical_background:
                if self._get_value_safe(founder.technical_background, False):
                    founder_score += 0.03

            scores.append(founder_score)

        if not scores:
            return 0.3, 0.2, {"note": "no_founder_data"}

        # Team score = best founder + bonus for co-founder strength
        team_score = max(scores)
        if len(scores) > 1:
            team_score += min(0.1, scores[1] * 0.3)  # Second founder bonus

        # Confidence based on data availability
        confidence = min(0.8, 0.3 + len(company.founders) * 0.1 + len(breakdown) * 0.02)

        return min(1.0, team_score), confidence, breakdown

    def score_market(self, company: CompanyData, estimates: Dict[str, EstimatedMetric]) -> Tuple[float, float, Dict]:
        """
        Score market opportunity (0-1) with confidence
        """
        score = 0.5  # Base score
        breakdown = {}
        confidences = []

        # TAM size
        tam = None
        if company.market.tam:
            tam = self._get_value_safe(company.market.tam, 0)
            confidences.append(self._confidence_to_float(company.market.tam.confidence))
        elif "tam" in estimates:
            tam = estimates["tam"].value
            confidences.append(estimates["tam"].confidence)

        if tam:
            tam_billions = tam / 1e9
            breakdown["tam_billions"] = tam_billions
            if tam_billions > 100:
                score += 0.2
            elif tam_billions > 50:
                score += 0.15
            elif tam_billions > 20:
                score += 0.1
            elif tam_billions > 5:
                score += 0.05

        # Market growth
        if company.market.market_growth_rate:
            growth = self._get_value_safe(company.market.market_growth_rate, 0)
            breakdown["market_growth"] = growth
            if growth > 0.3:  # 30%+ growth
                score += 0.15
            elif growth > 0.2:
                score += 0.1
            elif growth > 0.1:
                score += 0.05
            confidences.append(self._confidence_to_float(company.market.market_growth_rate.confidence))

        # Competition (fewer competitors can be good or bad)
        if company.market.competitors:
            comp_count = len(company.market.competitors)
            breakdown["competitor_count"] = comp_count
            if 3 <= comp_count <= 10:
                score += 0.05  # Validated market, room to compete
            elif comp_count > 15:
                score -= 0.05  # Crowded

        # Calculate confidence
        confidence = sum(confidences) / len(confidences) if confidences else 0.3

        return min(1.0, max(0.1, score)), confidence, breakdown

    def score_traction(self, company: CompanyData, estimates: Dict[str, EstimatedMetric]) -> Tuple[float, float, Dict]:
        """
        Score traction (0-1) with confidence
        """
        score = 0.2  # Base score (low without evidence)
        breakdown = {}
        confidences = []

        # Revenue
        revenue = None
        if company.traction.revenue_annual:
            revenue = self._get_value_safe(company.traction.revenue_annual, 0)
            confidences.append(self._confidence_to_float(company.traction.revenue_annual.confidence))
        elif company.traction.revenue_monthly:
            revenue = self._get_value_safe(company.traction.revenue_monthly, 0) * 12
            confidences.append(self._confidence_to_float(company.traction.revenue_monthly.confidence))
        elif "revenue_annual" in estimates:
            revenue = estimates["revenue_annual"].value
            confidences.append(estimates["revenue_annual"].confidence)

        if revenue:
            breakdown["revenue_annual"] = revenue
            if revenue > 10_000_000:
                score += 0.35
            elif revenue > 1_000_000:
                score += 0.25
            elif revenue > 100_000:
                score += 0.15
            else:
                score += 0.05

        # Growth rate
        growth = None
        if company.traction.revenue_growth_rate:
            growth = self._get_value_safe(company.traction.revenue_growth_rate, 0)
            confidences.append(self._confidence_to_float(company.traction.revenue_growth_rate.confidence))
        elif "growth_rate" in estimates:
            growth = estimates["growth_rate"].value
            confidences.append(estimates["growth_rate"].confidence)

        if growth:
            breakdown["monthly_growth"] = growth
            if growth > 0.15:  # >15% MoM
                score += 0.2
            elif growth > 0.08:
                score += 0.1
            elif growth > 0.03:
                score += 0.05

        # User/customer count
        users = None
        if company.traction.user_count:
            users = self._get_value_safe(company.traction.user_count, 0)
        elif company.traction.customer_count:
            users = self._get_value_safe(company.traction.customer_count, 0)
        elif "user_count" in estimates:
            users = estimates["user_count"].value

        if users:
            breakdown["users"] = users
            if users > 100_000:
                score += 0.1
            elif users > 10_000:
                score += 0.05

        # Product signals
        if company.traction.github_stars:
            stars = self._get_value_safe(company.traction.github_stars, 0)
            breakdown["github_stars"] = stars
            if stars > 10_000:
                score += 0.1
            elif stars > 1_000:
                score += 0.05
            confidences.append(0.8)  # GitHub stars are reliable

        if company.traction.product_hunt_upvotes:
            upvotes = self._get_value_safe(company.traction.product_hunt_upvotes, 0)
            breakdown["ph_upvotes"] = upvotes
            if upvotes > 1_000:
                score += 0.05
            confidences.append(0.7)

        confidence = sum(confidences) / len(confidences) if confidences else 0.2

        return min(1.0, score), confidence, breakdown

    def score_timing(self, company: CompanyData) -> Tuple[float, float, Dict]:
        """
        Score market timing (0-1) with confidence
        """
        score = 0.6  # Neutral timing
        breakdown = {}

        # Industry timing signals
        if company.industry:
            industry = str(self._get_value_safe(company.industry, "")).lower()
            breakdown["industry"] = industry

            # Hot sectors (2024-2025)
            hot_sectors = ["ai", "machine learning", "llm", "generative", "automation"]
            warm_sectors = ["fintech", "climate", "healthcare", "cybersecurity"]
            cooling_sectors = ["crypto", "web3", "metaverse"]

            for sector in hot_sectors:
                if sector in industry:
                    score += 0.2
                    breakdown["timing"] = "hot"
                    break
            else:
                for sector in warm_sectors:
                    if sector in industry:
                        score += 0.1
                        breakdown["timing"] = "warm"
                        break
                else:
                    for sector in cooling_sectors:
                        if sector in industry:
                            score -= 0.1
                            breakdown["timing"] = "cooling"
                            break

        # Recent funding in space = validated timing
        if company.funding.last_round_date:
            breakdown["recent_funding"] = True
            score += 0.05

        return min(1.0, max(0.2, score)), 0.5, breakdown

    def score_capital(self, company: CompanyData, estimates: Dict[str, EstimatedMetric]) -> Tuple[float, float, Dict]:
        """
        Score capital efficiency (0-1) with confidence
        """
        score = 0.5  # Base
        breakdown = {}
        confidences = []

        # Total raised
        total_raised = None
        if company.funding.total_raised:
            total_raised = self._get_value_safe(company.funding.total_raised, 0)
            confidences.append(self._confidence_to_float(company.funding.total_raised.confidence))
            breakdown["total_raised"] = total_raised

        # Calculate efficiency if we have revenue
        revenue = None
        if company.traction.revenue_annual:
            revenue = self._get_value_safe(company.traction.revenue_annual, 0)
        elif "revenue_annual" in estimates:
            revenue = estimates["revenue_annual"].value

        if total_raised and revenue and total_raised > 0:
            efficiency = revenue / total_raised
            breakdown["capital_efficiency"] = efficiency

            if efficiency > 1.0:
                score += 0.3  # Exceptional
            elif efficiency > 0.5:
                score += 0.2  # Good
            elif efficiency > 0.25:
                score += 0.1  # Decent
            # Below 0.25 = no bonus

        # Investor quality (top investors = validation)
        if company.funding.lead_investors:
            lead = self._get_value_safe(company.funding.lead_investors[0], "") if company.funding.lead_investors else ""
            top_investors = ["sequoia", "a16z", "andreessen", "benchmark", "accel", "greylock",
                           "yc", "y combinator", "founders fund", "khosla", "lightspeed", "index"]
            for ti in top_investors:
                if ti in str(lead).lower():
                    score += 0.1
                    breakdown["top_investor"] = lead
                    break

        confidence = sum(confidences) / len(confidences) if confidences else 0.4

        return min(1.0, score), confidence, breakdown

    def _get_value_safe(self, dp: Any, default: Any = None) -> Any:
        """Safely extract value from DataPoint or return default"""
        if dp is None:
            return default
        if isinstance(dp, DataPoint):
            return dp.value if dp.value is not None else default
        return dp

    def _confidence_to_float(self, conf: DataConfidence) -> float:
        """Convert DataConfidence to float"""
        if conf == DataConfidence.HIGH:
            return 0.9
        if conf == DataConfidence.MEDIUM:
            return 0.6
        if conf == DataConfidence.LOW:
            return 0.3
        return 0.5
