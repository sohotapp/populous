"""
Multi-Source Data Collection Engine
Free/open-source alternatives to paid APIs for startup research
"""

import os
import re
import json
import asyncio
import hashlib
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import math

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    from exa_py import Exa
except ImportError:
    Exa = None


# =============================================================================
# DATA MODELS
# =============================================================================

class DataConfidence(Enum):
    HIGH = "high"      # Direct source, recent, verified
    MEDIUM = "medium"  # Inferred or single source
    LOW = "low"        # Estimated or old data
    UNKNOWN = "unknown"


@dataclass
class DataPoint:
    """A single data point with provenance"""
    value: Any
    confidence: DataConfidence
    source: str
    source_url: Optional[str] = None
    extracted_at: datetime = field(default_factory=datetime.now)
    raw_text: Optional[str] = None


@dataclass
class FounderData:
    """Comprehensive founder profile"""
    name: str
    role: str
    linkedin_url: Optional[str] = None

    # Experience
    years_experience: Optional[DataPoint] = None
    prior_companies: List[DataPoint] = field(default_factory=list)
    prior_exits: List[DataPoint] = field(default_factory=list)
    prior_exit_values: List[DataPoint] = field(default_factory=list)

    # Education
    education: List[DataPoint] = field(default_factory=list)
    education_tier: Optional[DataPoint] = None

    # Network
    linkedin_connections: Optional[DataPoint] = None
    twitter_followers: Optional[DataPoint] = None
    github_followers: Optional[DataPoint] = None

    # Background
    technical_background: Optional[DataPoint] = None
    domain_expertise_years: Optional[DataPoint] = None
    top_company_experience: Optional[DataPoint] = None
    yc_alumni: Optional[DataPoint] = None


@dataclass
class TractionData:
    """Traction metrics with confidence"""
    # Revenue
    revenue_annual: Optional[DataPoint] = None
    revenue_monthly: Optional[DataPoint] = None
    revenue_growth_rate: Optional[DataPoint] = None

    # Users/Customers
    user_count: Optional[DataPoint] = None
    customer_count: Optional[DataPoint] = None
    user_growth_rate: Optional[DataPoint] = None

    # Engagement
    dau: Optional[DataPoint] = None
    mau: Optional[DataPoint] = None

    # Product signals
    github_stars: Optional[DataPoint] = None
    product_hunt_upvotes: Optional[DataPoint] = None
    g2_reviews: Optional[DataPoint] = None
    app_store_rating: Optional[DataPoint] = None
    app_downloads: Optional[DataPoint] = None

    # Web presence
    web_traffic_rank: Optional[DataPoint] = None
    backlinks: Optional[DataPoint] = None


@dataclass
class FundingData:
    """Funding history with confidence"""
    total_raised: Optional[DataPoint] = None
    last_round_amount: Optional[DataPoint] = None
    last_round_date: Optional[DataPoint] = None
    last_round_type: Optional[DataPoint] = None
    last_valuation: Optional[DataPoint] = None
    investors: List[DataPoint] = field(default_factory=list)
    lead_investors: List[DataPoint] = field(default_factory=list)


@dataclass
class MarketData:
    """Market analysis with confidence"""
    market_name: Optional[DataPoint] = None
    tam: Optional[DataPoint] = None
    sam: Optional[DataPoint] = None
    market_growth_rate: Optional[DataPoint] = None
    competitors: List[DataPoint] = field(default_factory=list)
    competitor_funding: List[DataPoint] = field(default_factory=list)


@dataclass
class CompanyData:
    """Aggregated company research data"""
    name: str
    description: Optional[DataPoint] = None
    website: Optional[DataPoint] = None
    founded_year: Optional[DataPoint] = None
    headquarters: Optional[DataPoint] = None
    employee_count: Optional[DataPoint] = None
    industry: Optional[DataPoint] = None
    business_model: Optional[DataPoint] = None

    founders: List[FounderData] = field(default_factory=list)
    traction: TractionData = field(default_factory=TractionData)
    funding: FundingData = field(default_factory=FundingData)
    market: MarketData = field(default_factory=MarketData)

    # Metadata
    research_timestamp: datetime = field(default_factory=datetime.now)
    source_count: int = 0
    overall_confidence: float = 0.5


# =============================================================================
# FREE DATA SOURCE QUERIES
# =============================================================================

class ExaQueryStrategy:
    """
    Multi-query strategy for comprehensive research using Exa
    Free alternative to Crunchbase, LinkedIn, SimilarWeb
    """

    @staticmethod
    def get_queries(company_name: str, batch: Optional[str] = None) -> Dict[str, List[str]]:
        """Generate targeted queries for each data category"""

        queries = {
            # Founder/Team queries (LinkedIn alternative)
            "founders": [
                f'"{company_name}" founder CEO background experience biography',
                f'"{company_name}" co-founder CTO team leadership',
                f'"{company_name}" founder LinkedIn previous companies startups',
                f'"{company_name}" founder prior exits acquisitions sold company',
            ],

            # Funding queries (Crunchbase alternative)
            "funding": [
                f'site:techcrunch.com "{company_name}" funding raises Series',
                f'"{company_name}" funding round million Series seed investors',
                f'"{company_name}" valuation investment raised venture capital',
                f'site:crunchbase.com/organization "{company_name}"',
            ],

            # Traction queries (SimilarWeb alternative)
            "traction": [
                f'"{company_name}" revenue ARR MRR growth customers',
                f'"{company_name}" users customers growth metrics',
                f'"{company_name}" product launch Product Hunt reviews',
                f'site:g2.com "{company_name}" OR site:capterra.com "{company_name}"',
            ],

            # Market queries
            "market": [
                f'"{company_name}" market size TAM competitors industry',
                f'"{company_name}" vs competitors comparison alternative',
                f'{company_name} industry market growth forecast',
            ],

            # Company overview
            "overview": [
                f'"{company_name}" startup company about description',
                f'site:linkedin.com/company "{company_name}"',
            ],

            # Technical signals (for dev tools)
            "technical": [
                f'site:github.com/{company_name.lower().replace(" ", "")}',
                f'"{company_name}" open source github stars developers',
                f'site:news.ycombinator.com "{company_name}"',
            ],
        }

        # Add batch-specific queries
        if batch:
            queries["accelerator"] = [
                f'"{company_name}" {batch} Y Combinator YC demo day',
                f'"{company_name}" {batch} batch accelerator',
            ]

        return queries


# =============================================================================
# DATA EXTRACTION ENGINE
# =============================================================================

class DataExtractionEngine:
    """
    Extract structured data from raw text using Claude
    """

    def __init__(self):
        self.llm = Anthropic() if Anthropic else None

    async def extract_founder_data(self, texts: List[str], company_name: str) -> List[FounderData]:
        """Extract founder profiles from research text"""

        if not self.llm or not texts:
            return []

        combined_text = "\n\n---\n\n".join(texts[:10])  # Limit context

        prompt = f"""Analyze this research about {company_name} and extract FOUNDER information.

RESEARCH DATA:
{combined_text[:15000]}

Extract ALL founders mentioned. For EACH founder, provide:

```json
{{
  "founders": [
    {{
      "name": "Full Name",
      "role": "CEO/CTO/Co-founder/etc",
      "linkedin_url": "URL if found",
      "years_experience": {{"value": 10, "confidence": "high/medium/low", "evidence": "quote from text"}},
      "prior_companies": [
        {{"company": "Company Name", "role": "Role", "years": "2015-2020", "confidence": "high/medium/low"}}
      ],
      "prior_exits": [
        {{"company": "Company Name", "exit_type": "acquisition/IPO", "year": 2020, "value_usd": 50000000, "confidence": "high/medium/low"}}
      ],
      "education": [
        {{"institution": "Stanford", "degree": "BS Computer Science", "year": 2010, "confidence": "high/medium/low"}}
      ],
      "technical_background": {{"value": true, "confidence": "high/medium/low", "evidence": "CS degree, engineering roles"}},
      "top_company_experience": {{"value": true, "company": "Google", "confidence": "high/medium/low"}},
      "yc_alumni": {{"value": true, "batch": "W15", "confidence": "high/medium/low"}}
    }}
  ]
}}
```

IMPORTANT:
- Only include data actually found in the text
- Set confidence based on: HIGH = directly stated, MEDIUM = inferred, LOW = uncertain
- Include evidence quotes for key claims
- If data not found, omit the field entirely
- Convert all monetary values to USD"""

        try:
            response = self.llm.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.content[0].text

            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                data = json.loads(json_match.group())
                return self._parse_founders(data.get("founders", []))

        except Exception as e:
            print(f"Founder extraction error: {e}")

        return []

    async def extract_funding_data(self, texts: List[str], company_name: str) -> FundingData:
        """Extract funding history from research text"""

        if not self.llm or not texts:
            return FundingData()

        combined_text = "\n\n---\n\n".join(texts[:10])

        prompt = f"""Analyze this research about {company_name} and extract FUNDING information.

RESEARCH DATA:
{combined_text[:15000]}

Extract funding details:

```json
{{
  "total_raised_usd": {{"value": 50000000, "confidence": "high/medium/low", "evidence": "quote"}},
  "funding_rounds": [
    {{
      "round_type": "Series A",
      "amount_usd": 20000000,
      "date": "2023-06",
      "valuation_usd": 100000000,
      "lead_investor": "Sequoia",
      "other_investors": ["YC", "Angel"],
      "confidence": "high/medium/low",
      "source": "TechCrunch article"
    }}
  ],
  "last_valuation_usd": {{"value": 100000000, "confidence": "high/medium/low"}}
}}
```

IMPORTANT:
- Convert all amounts to USD
- Extract specific round details when available
- Note the source of funding information
- HIGH confidence = press release or official announcement
- MEDIUM confidence = news article or interview
- LOW confidence = estimated or rumored"""

        try:
            response = self.llm.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.content[0].text
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                data = json.loads(json_match.group())
                return self._parse_funding(data)

        except Exception as e:
            print(f"Funding extraction error: {e}")

        return FundingData()

    async def extract_traction_data(self, texts: List[str], company_name: str) -> TractionData:
        """Extract traction metrics from research text"""

        if not self.llm or not texts:
            return TractionData()

        combined_text = "\n\n---\n\n".join(texts[:10])

        prompt = f"""Analyze this research about {company_name} and extract TRACTION metrics.

RESEARCH DATA:
{combined_text[:15000]}

Extract traction data:

```json
{{
  "revenue": {{
    "annual_usd": {{"value": 5000000, "confidence": "high/medium/low", "date": "2024", "evidence": "quote"}},
    "monthly_usd": {{"value": 400000, "confidence": "high/medium/low"}},
    "growth_rate_monthly": {{"value": 0.15, "confidence": "medium", "evidence": "15% MoM growth mentioned"}}
  }},
  "users": {{
    "total": {{"value": 50000, "confidence": "high/medium/low", "evidence": "quote"}},
    "growth_rate": {{"value": 0.20, "confidence": "medium"}}
  }},
  "customers": {{
    "total": {{"value": 500, "confidence": "high/medium/low"}},
    "notable": ["Company A", "Company B"]
  }},
  "product_signals": {{
    "github_stars": {{"value": 5000, "confidence": "high"}},
    "product_hunt_upvotes": {{"value": 1500, "confidence": "high"}},
    "g2_reviews": {{"value": 200, "rating": 4.5, "confidence": "high"}},
    "app_store_rating": {{"value": 4.7, "review_count": 1000, "confidence": "high"}}
  }},
  "pmf_signals": [
    "Low churn mentioned",
    "Word of mouth growth",
    "Expanding into enterprise"
  ]
}}
```

IMPORTANT:
- Extract specific numbers when available
- Note dates for metrics (traction changes over time)
- Include growth rates if mentioned
- PMF signals = qualitative indicators of product-market fit"""

        try:
            response = self.llm.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.content[0].text
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                data = json.loads(json_match.group())
                return self._parse_traction(data)

        except Exception as e:
            print(f"Traction extraction error: {e}")

        return TractionData()

    async def extract_market_data(self, texts: List[str], company_name: str) -> MarketData:
        """Extract market analysis from research text"""

        if not self.llm or not texts:
            return MarketData()

        combined_text = "\n\n---\n\n".join(texts[:10])

        prompt = f"""Analyze this research about {company_name} and extract MARKET information.

RESEARCH DATA:
{combined_text[:15000]}

Extract market data:

```json
{{
  "market_name": "Developer Tools / API Infrastructure",
  "tam_usd": {{"value": 50000000000, "confidence": "high/medium/low", "source": "Gartner report", "year": 2024}},
  "sam_usd": {{"value": 10000000000, "confidence": "medium"}},
  "market_growth_rate": {{"value": 0.25, "confidence": "medium", "evidence": "25% CAGR"}},
  "competitors": [
    {{"name": "Competitor A", "funding_usd": 100000000, "estimated_revenue": 50000000}},
    {{"name": "Competitor B", "funding_usd": 50000000}}
  ],
  "competitive_position": "Differentiated on developer experience",
  "market_timing": "emerging/growth/mature"
}}
```

IMPORTANT:
- TAM = Total Addressable Market (entire market)
- SAM = Serviceable Addressable Market (realistic target)
- Include source for market size estimates
- List direct competitors with their funding if known"""

        try:
            response = self.llm.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.content[0].text
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                data = json.loads(json_match.group())
                return self._parse_market(data)

        except Exception as e:
            print(f"Market extraction error: {e}")

        return MarketData()

    async def extract_company_overview(self, texts: List[str], company_name: str) -> Dict:
        """Extract basic company information"""

        if not self.llm or not texts:
            return {}

        combined_text = "\n\n---\n\n".join(texts[:5])

        prompt = f"""Analyze this research about {company_name} and extract basic company info.

RESEARCH DATA:
{combined_text[:10000]}

```json
{{
  "description": "One paragraph description of what the company does",
  "website": "https://...",
  "founded_year": 2020,
  "headquarters": "San Francisco, CA",
  "employee_count": {{"value": 50, "confidence": "high/medium/low", "evidence": "LinkedIn shows 50 employees"}},
  "industry": "Developer Tools",
  "business_model": "B2B SaaS"
}}
```"""

        try:
            response = self.llm.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.content[0].text
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                return json.loads(json_match.group())

        except Exception as e:
            print(f"Overview extraction error: {e}")

        return {}

    # Helper methods to parse extracted data into dataclasses
    def _parse_founders(self, founders_data: List[Dict]) -> List[FounderData]:
        """Parse founder JSON into FounderData objects"""
        founders = []
        for f in founders_data:
            founder = FounderData(
                name=f.get("name", "Unknown"),
                role=f.get("role", "Founder"),
                linkedin_url=f.get("linkedin_url")
            )

            if "years_experience" in f:
                founder.years_experience = self._make_datapoint(f["years_experience"])

            if "prior_companies" in f:
                founder.prior_companies = [
                    self._make_datapoint(pc) for pc in f["prior_companies"]
                ]

            if "prior_exits" in f:
                founder.prior_exits = [
                    self._make_datapoint(pe) for pe in f["prior_exits"]
                ]
                founder.prior_exit_values = [
                    self._make_datapoint({"value": pe.get("value_usd"), "confidence": pe.get("confidence", "medium")})
                    for pe in f["prior_exits"] if pe.get("value_usd")
                ]

            if "education" in f:
                founder.education = [
                    self._make_datapoint(edu) for edu in f["education"]
                ]
                # Determine education tier
                tier = self._determine_education_tier(f["education"])
                founder.education_tier = DataPoint(
                    value=tier,
                    confidence=DataConfidence.MEDIUM,
                    source="derived"
                )

            if "technical_background" in f:
                founder.technical_background = self._make_datapoint(f["technical_background"])

            if "top_company_experience" in f:
                founder.top_company_experience = self._make_datapoint(f["top_company_experience"])

            if "yc_alumni" in f:
                founder.yc_alumni = self._make_datapoint(f["yc_alumni"])

            founders.append(founder)

        return founders

    def _parse_funding(self, data: Dict) -> FundingData:
        """Parse funding JSON into FundingData object"""
        funding = FundingData()

        if "total_raised_usd" in data:
            funding.total_raised = self._make_datapoint(data["total_raised_usd"])

        if "funding_rounds" in data and data["funding_rounds"]:
            last_round = data["funding_rounds"][-1]
            funding.last_round_amount = DataPoint(
                value=last_round.get("amount_usd"),
                confidence=self._parse_confidence(last_round.get("confidence", "medium")),
                source=last_round.get("source", "research")
            )
            funding.last_round_date = DataPoint(
                value=last_round.get("date"),
                confidence=self._parse_confidence(last_round.get("confidence", "medium")),
                source="research"
            )
            funding.last_round_type = DataPoint(
                value=last_round.get("round_type"),
                confidence=self._parse_confidence(last_round.get("confidence", "medium")),
                source="research"
            )

            if last_round.get("valuation_usd"):
                funding.last_valuation = DataPoint(
                    value=last_round["valuation_usd"],
                    confidence=self._parse_confidence(last_round.get("confidence", "medium")),
                    source="research"
                )

            if last_round.get("lead_investor"):
                funding.lead_investors.append(DataPoint(
                    value=last_round["lead_investor"],
                    confidence=self._parse_confidence(last_round.get("confidence", "medium")),
                    source="research"
                ))

            for inv in last_round.get("other_investors", []):
                funding.investors.append(DataPoint(
                    value=inv,
                    confidence=DataConfidence.MEDIUM,
                    source="research"
                ))

        if "last_valuation_usd" in data:
            funding.last_valuation = self._make_datapoint(data["last_valuation_usd"])

        return funding

    def _parse_traction(self, data: Dict) -> TractionData:
        """Parse traction JSON into TractionData object"""
        traction = TractionData()

        if "revenue" in data:
            rev = data["revenue"]
            if "annual_usd" in rev:
                traction.revenue_annual = self._make_datapoint(rev["annual_usd"])
            if "monthly_usd" in rev:
                traction.revenue_monthly = self._make_datapoint(rev["monthly_usd"])
            if "growth_rate_monthly" in rev:
                traction.revenue_growth_rate = self._make_datapoint(rev["growth_rate_monthly"])

        if "users" in data:
            users = data["users"]
            if "total" in users:
                traction.user_count = self._make_datapoint(users["total"])
            if "growth_rate" in users:
                traction.user_growth_rate = self._make_datapoint(users["growth_rate"])

        if "customers" in data:
            cust = data["customers"]
            if "total" in cust:
                traction.customer_count = self._make_datapoint(cust["total"])

        if "product_signals" in data:
            ps = data["product_signals"]
            if "github_stars" in ps:
                traction.github_stars = self._make_datapoint(ps["github_stars"])
            if "product_hunt_upvotes" in ps:
                traction.product_hunt_upvotes = self._make_datapoint(ps["product_hunt_upvotes"])
            if "g2_reviews" in ps:
                traction.g2_reviews = self._make_datapoint(ps["g2_reviews"])
            if "app_store_rating" in ps:
                traction.app_store_rating = self._make_datapoint(ps["app_store_rating"])

        return traction

    def _parse_market(self, data: Dict) -> MarketData:
        """Parse market JSON into MarketData object"""
        market = MarketData()

        if "market_name" in data:
            market.market_name = DataPoint(
                value=data["market_name"],
                confidence=DataConfidence.MEDIUM,
                source="research"
            )

        if "tam_usd" in data:
            market.tam = self._make_datapoint(data["tam_usd"])

        if "sam_usd" in data:
            market.sam = self._make_datapoint(data["sam_usd"])

        if "market_growth_rate" in data:
            market.market_growth_rate = self._make_datapoint(data["market_growth_rate"])

        if "competitors" in data:
            for comp in data["competitors"]:
                market.competitors.append(DataPoint(
                    value=comp.get("name"),
                    confidence=DataConfidence.MEDIUM,
                    source="research"
                ))
                if comp.get("funding_usd"):
                    market.competitor_funding.append(DataPoint(
                        value={"name": comp["name"], "funding": comp["funding_usd"]},
                        confidence=DataConfidence.MEDIUM,
                        source="research"
                    ))

        return market

    def _make_datapoint(self, data: Any) -> DataPoint:
        """Create a DataPoint from various input formats"""
        if isinstance(data, dict):
            return DataPoint(
                value=data.get("value"),
                confidence=self._parse_confidence(data.get("confidence", "medium")),
                source=data.get("source", "research"),
                raw_text=data.get("evidence")
            )
        return DataPoint(
            value=data,
            confidence=DataConfidence.MEDIUM,
            source="research"
        )

    def _parse_confidence(self, conf: str) -> DataConfidence:
        """Parse confidence string to enum"""
        conf_lower = str(conf).lower()
        if conf_lower == "high":
            return DataConfidence.HIGH
        elif conf_lower == "low":
            return DataConfidence.LOW
        return DataConfidence.MEDIUM

    def _determine_education_tier(self, education: List[Dict]) -> int:
        """Determine education tier (1=top, 2=good, 3=other)"""
        TIER_1 = {"stanford", "mit", "harvard", "berkeley", "caltech", "princeton",
                  "yale", "columbia", "cmu", "carnegie mellon", "cornell"}
        TIER_2 = {"ucla", "michigan", "ut austin", "georgia tech", "uiuc",
                  "penn", "duke", "northwestern", "nyu", "usc"}

        best_tier = 3
        for edu in education:
            inst = str(edu.get("institution", "")).lower()
            for t1 in TIER_1:
                if t1 in inst:
                    best_tier = min(best_tier, 1)
                    break
            for t2 in TIER_2:
                if t2 in inst:
                    best_tier = min(best_tier, 2)
                    break

        return best_tier


# =============================================================================
# MULTI-SOURCE RESEARCH ENGINE
# =============================================================================

class MultiSourceResearchEngine:
    """
    Orchestrates research across multiple free data sources
    """

    def __init__(self):
        self.exa = Exa(api_key=os.environ.get("EXA_API_KEY")) if Exa and os.environ.get("EXA_API_KEY") else None
        self.extractor = DataExtractionEngine()
        self._cache: Dict[str, CompanyData] = {}

    async def research_company(self, name: str, batch: Optional[str] = None) -> CompanyData:
        """
        Comprehensive research on a company using multiple queries
        """
        cache_key = f"{name}:{batch or 'none'}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        print(f"[Research] Starting multi-source research for {name}")

        # Get all query categories
        queries = ExaQueryStrategy.get_queries(name, batch)

        # Execute queries in parallel by category
        category_results: Dict[str, List[str]] = {}

        for category, category_queries in queries.items():
            texts = []
            urls = []

            for query in category_queries:
                try:
                    results = await self._execute_exa_query(query)
                    for r in results:
                        if hasattr(r, 'text') and r.text:
                            texts.append(r.text[:3000])
                        if hasattr(r, 'url'):
                            urls.append(r.url)
                except Exception as e:
                    print(f"[Research] Query failed: {query[:50]}... - {e}")

            category_results[category] = texts
            print(f"[Research] {category}: {len(texts)} text sources")

        # Extract structured data from each category
        company = CompanyData(name=name)

        # Extract founder data
        founder_texts = category_results.get("founders", [])
        if founder_texts:
            company.founders = await self.extractor.extract_founder_data(founder_texts, name)
            print(f"[Research] Extracted {len(company.founders)} founders")

        # Extract funding data
        funding_texts = category_results.get("funding", [])
        if funding_texts:
            company.funding = await self.extractor.extract_funding_data(funding_texts, name)
            print(f"[Research] Extracted funding: {company.funding.total_raised}")

        # Extract traction data
        traction_texts = category_results.get("traction", []) + category_results.get("technical", [])
        if traction_texts:
            company.traction = await self.extractor.extract_traction_data(traction_texts, name)

        # Extract market data
        market_texts = category_results.get("market", [])
        if market_texts:
            company.market = await self.extractor.extract_market_data(market_texts, name)

        # Extract overview
        overview_texts = category_results.get("overview", []) + category_results.get("funding", [])[:2]
        if overview_texts:
            overview = await self.extractor.extract_company_overview(overview_texts, name)
            if overview:
                company.description = DataPoint(value=overview.get("description"), confidence=DataConfidence.MEDIUM, source="research")
                company.website = DataPoint(value=overview.get("website"), confidence=DataConfidence.HIGH, source="research")
                company.founded_year = DataPoint(value=overview.get("founded_year"), confidence=DataConfidence.MEDIUM, source="research")
                company.headquarters = DataPoint(value=overview.get("headquarters"), confidence=DataConfidence.MEDIUM, source="research")
                company.industry = DataPoint(value=overview.get("industry"), confidence=DataConfidence.MEDIUM, source="research")
                company.business_model = DataPoint(value=overview.get("business_model"), confidence=DataConfidence.MEDIUM, source="research")

                if "employee_count" in overview:
                    emp = overview["employee_count"]
                    if isinstance(emp, dict):
                        company.employee_count = DataPoint(
                            value=emp.get("value"),
                            confidence=DataConfidence.MEDIUM,
                            source="research"
                        )
                    else:
                        company.employee_count = DataPoint(value=emp, confidence=DataConfidence.MEDIUM, source="research")

        # Calculate overall source count and confidence
        company.source_count = sum(len(texts) for texts in category_results.values())
        company.overall_confidence = self._calculate_overall_confidence(company)

        # Cache result
        self._cache[cache_key] = company

        print(f"[Research] Complete: {company.source_count} sources, {company.overall_confidence:.2f} confidence")

        return company

    async def _execute_exa_query(self, query: str, num_results: int = 5) -> List:
        """Execute a single Exa query"""
        if not self.exa:
            return []

        try:
            results = self.exa.search_and_contents(
                query=query,
                num_results=num_results,
                use_autoprompt=True,
                text=True
            )
            return results.results if hasattr(results, 'results') else []
        except Exception as e:
            print(f"[Exa] Query error: {e}")
            return []

    def _calculate_overall_confidence(self, company: CompanyData) -> float:
        """Calculate overall research confidence score"""
        scores = []

        # Founder data confidence
        if company.founders:
            founder_score = min(1.0, len(company.founders) * 0.3)
            if any(f.prior_exits for f in company.founders):
                founder_score += 0.2
            if any(f.education for f in company.founders):
                founder_score += 0.1
            scores.append(founder_score)

        # Funding data confidence
        if company.funding.total_raised:
            scores.append(0.8 if company.funding.total_raised.confidence == DataConfidence.HIGH else 0.5)

        # Traction data confidence
        traction_score = 0
        if company.traction.revenue_annual or company.traction.revenue_monthly:
            traction_score += 0.4
        if company.traction.user_count or company.traction.customer_count:
            traction_score += 0.3
        if company.traction.github_stars or company.traction.product_hunt_upvotes:
            traction_score += 0.2
        if traction_score > 0:
            scores.append(traction_score)

        # Market data confidence
        if company.market.tam:
            scores.append(0.6)

        # Source count bonus
        source_bonus = min(0.3, company.source_count * 0.02)

        if scores:
            return min(0.95, sum(scores) / len(scores) + source_bonus)
        return 0.3 + source_bonus
