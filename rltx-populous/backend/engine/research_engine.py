"""
Research Engine
Deep company and market research using Exa API and Claude
"""

import os
import json
import asyncio
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from anthropic import Anthropic

try:
    from exa_py import Exa
    EXA_AVAILABLE = True
except ImportError:
    EXA_AVAILABLE = False
    Exa = None

from backend.models.company import (
    Company, Market, ResearchResult, CompanyProduct, Leader,
    NewsItem, ProductTier, CompetitorRelation, MarketPosition,
    FundingStage, CompanySize
)


class ResearchEngine:
    """
    Engine for deep company and market research.
    Uses Exa for web search and Claude for synthesis.
    """

    def __init__(
        self,
        exa_client=None,
        llm_client: Anthropic = None
    ):
        self.exa = exa_client
        self.llm = llm_client or Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Initialize Exa if not provided
        if self.exa is None and EXA_AVAILABLE:
            exa_key = os.getenv("EXA_API_KEY")
            if exa_key:
                self.exa = Exa(api_key=exa_key)

    async def research_company(
        self,
        query: str,
        depth: str = "deep"
    ) -> ResearchResult:
        """
        Perform deep research on a company.

        Args:
            query: Company name or description
            depth: "quick", "standard", or "deep"

        Returns:
            Complete ResearchResult with company, competitors, and market
        """
        start_time = datetime.now()
        sources_consulted = 0

        # Step 1: Search for company information
        company_info = await self._search_company_info(query)
        sources_consulted += len(company_info.get("sources", []))

        # Step 2: Search for competitors
        competitor_info = await self._search_competitors(query, company_info)
        sources_consulted += len(competitor_info.get("sources", []))

        # Step 3: Search for market information
        market_info = await self._search_market(query, company_info)
        sources_consulted += len(market_info.get("sources", []))

        # Step 4: Search for recent news
        news_info = await self._search_news(query)
        sources_consulted += len(news_info.get("sources", []))

        # Step 5: Synthesize into structured models
        target_company = await self._synthesize_company(
            query, company_info, news_info
        )

        competitors = await self._synthesize_competitors(
            competitor_info, target_company
        )

        market = await self._synthesize_market(
            market_info, target_company, competitors
        )

        # Calculate research duration
        duration = (datetime.now() - start_time).total_seconds()

        return ResearchResult(
            query=query,
            research_depth=depth,
            target_company=target_company,
            competitors=competitors,
            market=market,
            sources_consulted=sources_consulted,
            research_duration_seconds=duration,
            overall_confidence=self._calculate_confidence(
                company_info, competitor_info, market_info
            )
        )

    async def _search_company_info(self, query: str) -> Dict:
        """Search for company information using Exa."""

        if not self.exa:
            # Fallback to LLM-only research
            return await self._llm_research_company(query)

        try:
            # Search for company overview
            overview_results = self.exa.search_and_contents(
                query=f"{query} company overview about funding employees",
                num_results=10,
                use_autoprompt=True,
                text=True
            )

            # Search for company products and pricing
            product_results = self.exa.search_and_contents(
                query=f"{query} products pricing features",
                num_results=8,
                use_autoprompt=True,
                text=True
            )

            # Search for company leadership
            leadership_results = self.exa.search_and_contents(
                query=f"{query} CEO founder leadership team",
                num_results=5,
                use_autoprompt=True,
                text=True
            )

            return {
                "overview": self._extract_texts(overview_results),
                "products": self._extract_texts(product_results),
                "leadership": self._extract_texts(leadership_results),
                "sources": self._extract_urls(overview_results) +
                          self._extract_urls(product_results) +
                          self._extract_urls(leadership_results)
            }

        except Exception as e:
            print(f"Exa search failed: {e}")
            return await self._llm_research_company(query)

    async def _search_competitors(self, query: str, company_info: Dict) -> Dict:
        """Search for competitor information."""

        if not self.exa:
            return await self._llm_research_competitors(query)

        try:
            # Search for competitors
            competitor_results = self.exa.search_and_contents(
                query=f"{query} competitors alternatives vs comparison",
                num_results=10,
                use_autoprompt=True,
                text=True
            )

            # Search for competitive landscape
            landscape_results = self.exa.search_and_contents(
                query=f"{query} market competitive landscape industry players",
                num_results=8,
                use_autoprompt=True,
                text=True
            )

            return {
                "competitors": self._extract_texts(competitor_results),
                "landscape": self._extract_texts(landscape_results),
                "sources": self._extract_urls(competitor_results) +
                          self._extract_urls(landscape_results)
            }

        except Exception as e:
            print(f"Exa competitor search failed: {e}")
            return await self._llm_research_competitors(query)

    async def _search_market(self, query: str, company_info: Dict) -> Dict:
        """Search for market information."""

        if not self.exa:
            return await self._llm_research_market(query)

        try:
            # Search for market size and trends
            market_results = self.exa.search_and_contents(
                query=f"{query} market size TAM growth trends industry",
                num_results=10,
                use_autoprompt=True,
                text=True
            )

            return {
                "market": self._extract_texts(market_results),
                "sources": self._extract_urls(market_results)
            }

        except Exception as e:
            print(f"Exa market search failed: {e}")
            return await self._llm_research_market(query)

    async def _search_news(self, query: str) -> Dict:
        """Search for recent news about the company."""

        if not self.exa:
            return {"news": [], "sources": []}

        try:
            # Search for recent news
            news_results = self.exa.search_and_contents(
                query=f"{query} news announcement launch pricing",
                num_results=10,
                use_autoprompt=True,
                text=True
            )

            return {
                "news": self._extract_texts(news_results),
                "sources": self._extract_urls(news_results)
            }

        except Exception as e:
            print(f"Exa news search failed: {e}")
            return {"news": [], "sources": []}

    async def _synthesize_company(
        self,
        query: str,
        company_info: Dict,
        news_info: Dict
    ) -> Company:
        """Use Claude to synthesize company information into structured model."""

        # Combine all research
        research_text = ""
        for key, texts in company_info.items():
            if key != "sources" and isinstance(texts, list):
                research_text += f"\n\n=== {key.upper()} ===\n"
                research_text += "\n---\n".join(texts[:5])  # Limit to prevent context overflow

        if news_info.get("news"):
            research_text += "\n\n=== RECENT NEWS ===\n"
            research_text += "\n---\n".join(news_info["news"][:5])

        prompt = f"""Based on this research about "{query}", extract structured company information.

RESEARCH DATA:
{research_text[:15000]}  # Limit context

Return a JSON object with these fields:
{{
    "name": "Company name",
    "description": "2-3 sentence description",
    "tagline": "Company tagline if known",
    "website": "website URL",
    "industry": "Primary industry",
    "sub_industry": "Sub-industry if applicable",
    "founded": 2020,
    "headquarters": "City, Country",
    "employee_count": "1-10" | "11-50" | "51-200" | "201-1000" | "1001-5000" | "5000+",
    "funding_stage": "bootstrapped" | "seed" | "series_a" | "series_b" | "series_c" | "series_d_plus" | "public",
    "total_funding": "$XXM",
    "revenue_estimate": "$XXM ARR",
    "products": [
        {{
            "name": "Product name",
            "description": "Description",
            "category": "Category",
            "positioning": "How it's positioned",
            "key_features": ["feature1", "feature2"],
            "pricing_tiers": [
                {{"name": "Free", "price": 0, "price_unit": "month"}},
                {{"name": "Pro", "price": 10, "price_unit": "user/month"}}
            ],
            "target_market": "Who it's for",
            "differentiators": ["diff1", "diff2"]
        }}
    ],
    "leadership": [
        {{"name": "Name", "role": "CEO", "background": "Brief background"}}
    ],
    "market_position": "leader" | "challenger" | "niche" | "emerging",
    "notable_customers": ["Customer1", "Customer2"],
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "opportunities": ["opportunity1", "opportunity2"],
    "threats": ["threat1", "threat2"],
    "direct_competitors": ["Competitor1", "Competitor2"],
    "growth_strategy": "Description of growth strategy",
    "pricing_strategy": "Description of pricing strategy"
}}

Be specific and factual. If information is not available, omit the field or use null.
Return ONLY valid JSON, no other text."""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            # Extract JSON from response
            text = response.content[0].text
            # Find JSON in response
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(text[start:end])
            else:
                data = {}

            # Convert to Company model
            return self._dict_to_company(data, company_info.get("sources", []))

        except Exception as e:
            print(f"Failed to parse company synthesis: {e}")
            # Return minimal company
            return Company(
                name=query,
                description=f"Company researched: {query}",
                industry="Unknown",
                research_sources=company_info.get("sources", [])
            )

    async def _synthesize_competitors(
        self,
        competitor_info: Dict,
        target_company: Company
    ) -> List[Company]:
        """Synthesize competitor information into Company models."""

        research_text = ""
        for key, texts in competitor_info.items():
            if key != "sources" and isinstance(texts, list):
                research_text += "\n---\n".join(texts[:5])

        prompt = f"""Based on this competitive research for {target_company.name}, identify and describe the top 3-5 competitors.

RESEARCH DATA:
{research_text[:10000]}

For each competitor, return a JSON array:
[
    {{
        "name": "Competitor name",
        "description": "2-3 sentence description",
        "industry": "{target_company.industry}",
        "market_position": "leader" | "challenger" | "niche" | "emerging",
        "strengths": ["strength1", "strength2"],
        "weaknesses": ["weakness1", "weakness2"],
        "pricing_strategy": "How they price",
        "threat_level": 0.8,
        "overlap_with_target": ["area1", "area2"]
    }}
]

Return ONLY valid JSON array, no other text."""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            text = response.content[0].text
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                data = json.loads(text[start:end])
            else:
                data = []

            competitors = []
            for comp_data in data[:5]:
                comp = Company(
                    name=comp_data.get("name", "Unknown"),
                    description=comp_data.get("description", ""),
                    industry=comp_data.get("industry", target_company.industry),
                    market_position=MarketPosition(comp_data.get("market_position", "challenger")),
                    strengths=comp_data.get("strengths", []),
                    weaknesses=comp_data.get("weaknesses", []),
                    pricing_strategy=comp_data.get("pricing_strategy"),
                    research_sources=competitor_info.get("sources", [])
                )
                competitors.append(comp)

            return competitors

        except Exception as e:
            print(f"Failed to parse competitors: {e}")
            return []

    async def _synthesize_market(
        self,
        market_info: Dict,
        target_company: Company,
        competitors: List[Company]
    ) -> Market:
        """Synthesize market information into Market model."""

        research_text = ""
        for key, texts in market_info.items():
            if key != "sources" and isinstance(texts, list):
                research_text += "\n---\n".join(texts[:5])

        competitor_names = [c.name for c in competitors]

        prompt = f"""Based on this market research for {target_company.name}'s market, describe the market.

RESEARCH DATA:
{research_text[:10000]}

TARGET COMPANY: {target_company.name} - {target_company.description}
COMPETITORS: {', '.join(competitor_names)}

Return a JSON object:
{{
    "name": "Market name (e.g., 'Project Management Software')",
    "description": "2-3 sentence market description",
    "category": "Broad category",
    "total_addressable_market": "$XXB",
    "growth_rate": 0.15,
    "growth_drivers": ["driver1", "driver2"],
    "maturity": "emerging" | "growing" | "mature" | "declining",
    "barriers_to_entry": ["barrier1", "barrier2"],
    "key_success_factors": ["factor1", "factor2"],
    "segments": [
        {{"name": "Enterprise", "size_percent": 40, "growth": "high"}},
        {{"name": "SMB", "size_percent": 35, "growth": "medium"}},
        {{"name": "Consumer", "size_percent": 25, "growth": "low"}}
    ],
    "major_trends": ["trend1", "trend2"],
    "disruption_risks": ["risk1", "risk2"],
    "market_leaders": ["Leader1", "Leader2"],
    "concentration": "concentrated" | "moderate" | "fragmented"
}}

Return ONLY valid JSON, no other text."""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            text = response.content[0].text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(text[start:end])
            else:
                data = {}

            return Market(
                name=data.get("name", f"{target_company.industry} Market"),
                description=data.get("description", ""),
                category=data.get("category", target_company.industry),
                total_addressable_market=data.get("total_addressable_market"),
                growth_rate=data.get("growth_rate"),
                growth_drivers=data.get("growth_drivers", []),
                maturity=data.get("maturity", "growing"),
                barriers_to_entry=data.get("barriers_to_entry", []),
                key_success_factors=data.get("key_success_factors", []),
                segments=data.get("segments", []),
                major_trends=data.get("major_trends", []),
                disruption_risks=data.get("disruption_risks", []),
                market_leaders=data.get("market_leaders", []),
                concentration=data.get("concentration", "fragmented"),
                research_sources=market_info.get("sources", [])
            )

        except Exception as e:
            print(f"Failed to parse market: {e}")
            return Market(
                name=f"{target_company.industry} Market",
                description="Market information",
                category=target_company.industry
            )

    def _dict_to_company(self, data: Dict, sources: List[str]) -> Company:
        """Convert dictionary to Company model."""

        # Parse products
        products = []
        for p in data.get("products", []):
            tiers = []
            for t in p.get("pricing_tiers", []):
                tiers.append(ProductTier(
                    name=t.get("name", ""),
                    price=t.get("price"),
                    price_unit=t.get("price_unit", "month"),
                    features=t.get("features", [])
                ))

            products.append(CompanyProduct(
                name=p.get("name", ""),
                description=p.get("description", ""),
                category=p.get("category", ""),
                positioning=p.get("positioning", ""),
                key_features=p.get("key_features", []),
                pricing_tiers=tiers,
                target_market=p.get("target_market", ""),
                differentiators=p.get("differentiators", [])
            ))

        # Parse leadership
        leadership = []
        for l in data.get("leadership", []):
            leadership.append(Leader(
                name=l.get("name", ""),
                role=l.get("role", ""),
                background=l.get("background")
            ))

        # Parse employee count
        employee_count = None
        ec = data.get("employee_count")
        if ec:
            try:
                employee_count = CompanySize(ec)
            except ValueError:
                pass

        # Parse funding stage
        funding_stage = None
        fs = data.get("funding_stage")
        if fs:
            try:
                funding_stage = FundingStage(fs)
            except ValueError:
                pass

        # Parse market position
        market_position = MarketPosition.CHALLENGER
        mp = data.get("market_position")
        if mp:
            try:
                market_position = MarketPosition(mp)
            except ValueError:
                pass

        return Company(
            name=data.get("name", "Unknown"),
            description=data.get("description", ""),
            tagline=data.get("tagline"),
            website=data.get("website"),
            industry=data.get("industry", "Unknown"),
            sub_industry=data.get("sub_industry"),
            founded=data.get("founded"),
            headquarters=data.get("headquarters"),
            employee_count=employee_count,
            funding_stage=funding_stage,
            total_funding=data.get("total_funding"),
            revenue_estimate=data.get("revenue_estimate"),
            products=products,
            leadership=leadership,
            market_position=market_position,
            notable_customers=data.get("notable_customers", []),
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            opportunities=data.get("opportunities", []),
            threats=data.get("threats", []),
            direct_competitors=data.get("direct_competitors", []),
            growth_strategy=data.get("growth_strategy"),
            pricing_strategy=data.get("pricing_strategy"),
            research_sources=sources
        )

    def _extract_texts(self, results) -> List[str]:
        """Extract text content from Exa results."""
        texts = []
        if hasattr(results, 'results'):
            for r in results.results:
                if hasattr(r, 'text') and r.text:
                    texts.append(r.text[:2000])  # Limit each text
        return texts

    def _extract_urls(self, results) -> List[str]:
        """Extract URLs from Exa results."""
        urls = []
        if hasattr(results, 'results'):
            for r in results.results:
                if hasattr(r, 'url') and r.url:
                    urls.append(r.url)
        return urls

    def _calculate_confidence(
        self,
        company_info: Dict,
        competitor_info: Dict,
        market_info: Dict
    ) -> float:
        """Calculate overall research confidence."""
        source_count = (
            len(company_info.get("sources", [])) +
            len(competitor_info.get("sources", [])) +
            len(market_info.get("sources", []))
        )

        # More sources = higher confidence
        if source_count >= 20:
            return 0.9
        elif source_count >= 10:
            return 0.8
        elif source_count >= 5:
            return 0.7
        else:
            return 0.6

    # Fallback methods when Exa is not available

    async def _llm_research_company(self, query: str) -> Dict:
        """Fallback to pure LLM research."""
        prompt = f"""You are a business research analyst. Provide detailed information about {query}.

Include:
1. Company overview (description, founding, size, funding)
2. Products and pricing
3. Leadership team
4. Market position

Be specific and factual. If you don't know something, say so."""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return {
            "overview": [response.content[0].text],
            "products": [],
            "leadership": [],
            "sources": ["Claude knowledge base"]
        }

    async def _llm_research_competitors(self, query: str) -> Dict:
        """Fallback competitor research."""
        prompt = f"""List the main competitors of {query} and briefly describe each one.
For each competitor include: name, what they do, their strengths and weaknesses compared to {query}."""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        return {
            "competitors": [response.content[0].text],
            "landscape": [],
            "sources": ["Claude knowledge base"]
        }

    async def _llm_research_market(self, query: str) -> Dict:
        """Fallback market research."""
        prompt = f"""Describe the market that {query} operates in.
Include: market size, growth rate, major trends, key players, and market dynamics."""

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        return {
            "market": [response.content[0].text],
            "sources": ["Claude knowledge base"]
        }
