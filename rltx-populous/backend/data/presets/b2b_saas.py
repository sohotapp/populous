"""
Pre-built B2B SaaS Launch scenario for demos.
"""

from backend.models import (
    Scenario, Segment, DecisionFramework, BehavioralProfile,
    Stakeholder, Competitor, Product, Strategy,
    Messaging, Pricing, GoToMarket, DiscountStrategy, MarketType
)


def get_saas_launch_scenario() -> Scenario:
    """Create the demo B2B SaaS launch scenario"""

    return Scenario(
        id="saas_launch_2024",
        name="B2B SaaS Product Launch",
        description="Launch a project management tool into a competitive market",
        market_type=MarketType.B2B_SAAS,
        total_addressable_market=50000,

        segments=[
            # Enterprise segment (15%)
            Segment(
                id="enterprise",
                name="Enterprise",
                size_pct=0.15,
                decision_framework=DecisionFramework(
                    stages=["Unaware", "Aware", "Considering", "Evaluating", "Decided"],
                    avg_cycle_days=90,
                    stakeholders=[
                        Stakeholder(
                            role="IT Director",
                            influence_weight=0.35,
                            priorities={
                                "security": 0.9,
                                "integrations": 0.8,
                                "scalability": 0.85,
                                "compliance": 0.9,
                                "ease_of_use": 0.5
                            },
                            risk_tolerance=0.2
                        ),
                        Stakeholder(
                            role="CFO/Finance",
                            influence_weight=0.25,
                            priorities={
                                "security": 0.7,
                                "integrations": 0.6,
                                "scalability": 0.7,
                                "compliance": 0.8,
                                "ease_of_use": 0.4
                            },
                            risk_tolerance=0.15
                        ),
                        Stakeholder(
                            role="End Users",
                            influence_weight=0.2,
                            priorities={
                                "security": 0.4,
                                "integrations": 0.7,
                                "scalability": 0.5,
                                "compliance": 0.3,
                                "ease_of_use": 0.95
                            },
                            risk_tolerance=0.5
                        ),
                        Stakeholder(
                            role="Procurement",
                            influence_weight=0.2,
                            priorities={
                                "security": 0.6,
                                "integrations": 0.5,
                                "scalability": 0.5,
                                "compliance": 0.85,
                                "ease_of_use": 0.3
                            },
                            risk_tolerance=0.1
                        )
                    ],
                    triggers={
                        "Unaware->Aware": "Industry event, peer reference, or analyst report",
                        "Aware->Considering": "Active pain point, budget cycle alignment",
                        "Considering->Evaluating": "Demo, security review initiated",
                        "Evaluating->Decided": "Legal/procurement approval, final pricing"
                    },
                    blockers=[
                        "Security audit failure",
                        "Budget reallocation",
                        "Stakeholder departure",
                        "Competitor enterprise agreement"
                    ]
                ),
                behavioral_profile=BehavioralProfile(
                    company_size_range=(1000, 50000),
                    budget_range=(100000, 500000),
                    risk_tolerance=(0.25, 0.1),
                    price_sensitivity=(0.35, 0.1),
                    decision_speed=(0.25, 0.08),
                    influencer_susceptibility=0.4,
                    network_density=0.03
                )
            ),

            # Mid-Market segment (35%)
            Segment(
                id="mid_market",
                name="Mid-Market",
                size_pct=0.35,
                decision_framework=DecisionFramework(
                    stages=["Unaware", "Aware", "Considering", "Evaluating", "Decided"],
                    avg_cycle_days=45,
                    stakeholders=[
                        Stakeholder(
                            role="VP Operations",
                            influence_weight=0.4,
                            priorities={
                                "security": 0.6,
                                "integrations": 0.75,
                                "scalability": 0.65,
                                "compliance": 0.5,
                                "ease_of_use": 0.8
                            },
                            risk_tolerance=0.4
                        ),
                        Stakeholder(
                            role="Team Leads",
                            influence_weight=0.35,
                            priorities={
                                "security": 0.4,
                                "integrations": 0.7,
                                "scalability": 0.5,
                                "compliance": 0.3,
                                "ease_of_use": 0.9
                            },
                            risk_tolerance=0.5
                        ),
                        Stakeholder(
                            role="Finance",
                            influence_weight=0.25,
                            priorities={
                                "security": 0.5,
                                "integrations": 0.5,
                                "scalability": 0.6,
                                "compliance": 0.6,
                                "ease_of_use": 0.4
                            },
                            risk_tolerance=0.3
                        )
                    ],
                    triggers={
                        "Unaware->Aware": "Content marketing, webinar, or peer mention",
                        "Aware->Considering": "Growth pain, tool consolidation initiative",
                        "Considering->Evaluating": "Free trial, sales call",
                        "Evaluating->Decided": "Team buy-in, pricing approved"
                    },
                    blockers=[
                        "Integration complexity",
                        "Budget constraints",
                        "Team resistance to change",
                        "Existing contract lock-in"
                    ]
                ),
                behavioral_profile=BehavioralProfile(
                    company_size_range=(100, 999),
                    budget_range=(20000, 100000),
                    risk_tolerance=(0.45, 0.12),
                    price_sensitivity=(0.55, 0.12),
                    decision_speed=(0.45, 0.1),
                    influencer_susceptibility=0.6,
                    network_density=0.05
                )
            ),

            # SMB segment (50%)
            Segment(
                id="smb",
                name="SMB",
                size_pct=0.50,
                decision_framework=DecisionFramework(
                    stages=["Unaware", "Aware", "Considering", "Evaluating", "Decided"],
                    avg_cycle_days=21,
                    stakeholders=[
                        Stakeholder(
                            role="Founder/CEO",
                            influence_weight=0.6,
                            priorities={
                                "security": 0.4,
                                "integrations": 0.6,
                                "scalability": 0.4,
                                "compliance": 0.3,
                                "ease_of_use": 0.9
                            },
                            risk_tolerance=0.6
                        ),
                        Stakeholder(
                            role="Team",
                            influence_weight=0.4,
                            priorities={
                                "security": 0.3,
                                "integrations": 0.5,
                                "scalability": 0.3,
                                "compliance": 0.2,
                                "ease_of_use": 0.95
                            },
                            risk_tolerance=0.65
                        )
                    ],
                    triggers={
                        "Unaware->Aware": "Social media, review site, word of mouth",
                        "Aware->Considering": "Immediate need, free trial offer",
                        "Considering->Evaluating": "Self-serve trial, quick demo",
                        "Evaluating->Decided": "Team likes it, price works"
                    },
                    blockers=[
                        "Price too high",
                        "Too complex",
                        "No immediate need",
                        "Competitor's free tier"
                    ]
                ),
                behavioral_profile=BehavioralProfile(
                    company_size_range=(5, 99),
                    budget_range=(1000, 20000),
                    risk_tolerance=(0.6, 0.15),
                    price_sensitivity=(0.75, 0.1),
                    decision_speed=(0.7, 0.12),
                    influencer_susceptibility=0.7,
                    network_density=0.08
                )
            )
        ],

        competitors=[
            Competitor(
                id="monday",
                name="Monday.com",
                market_share=0.30,
                price_point=1.0,
                features={
                    "security": 0.7,
                    "integrations": 0.9,
                    "scalability": 0.8,
                    "compliance": 0.7,
                    "ease_of_use": 0.85
                },
                brand_awareness=0.85,
                aggression=0.7,
                response_speed=0.6
            ),
            Competitor(
                id="asana",
                name="Asana",
                market_share=0.25,
                price_point=0.9,
                features={
                    "security": 0.65,
                    "integrations": 0.85,
                    "scalability": 0.75,
                    "compliance": 0.65,
                    "ease_of_use": 0.9
                },
                brand_awareness=0.80,
                aggression=0.5,
                response_speed=0.5
            ),
            Competitor(
                id="jira",
                name="Jira",
                market_share=0.20,
                price_point=1.1,
                features={
                    "security": 0.9,
                    "integrations": 0.9,
                    "scalability": 0.95,
                    "compliance": 0.9,
                    "ease_of_use": 0.45
                },
                brand_awareness=0.75,
                aggression=0.3,
                response_speed=0.3
            )
        ],

        your_product=Product(
            id="nexus",
            name="Nexus",
            price_point=0.85,
            features={
                "security": 0.8,
                "integrations": 0.65,
                "scalability": 0.7,
                "compliance": 0.75,
                "ease_of_use": 0.9
            },
            brand_awareness=0.05
        ),

        simulation_days=90
    )


def get_demo_strategies() -> list[Strategy]:
    """Create demo strategies for comparison"""

    return [
        # Strategy 1: Value Play (SMB-focused)
        Strategy(
            id="value_play",
            name="Value Play",
            description="Lead with price and ease-of-use, target SMB",
            messaging=Messaging(
                value_proposition="Finally, project management that doesn't break the bank",
                primary_claim="Easiest PM tool to adopt, half the price of competitors",
                feature_emphasis={
                    "ease_of_use": 0.9,
                    "integrations": 0.5,
                    "security": 0.3,
                    "scalability": 0.3,
                    "compliance": 0.2
                },
                tone="value",
                full_pitch="""
Tired of paying enterprise prices for basic project management?
Nexus gives your team everything they need—without the complexity or cost.

Get started in minutes, not months. No training required.
Your team will actually use it because it just works.
"""
            ),
            pricing=Pricing(
                base_price=0.7,
                model="per_seat",
                discount=DiscountStrategy(
                    available=True,
                    max_discount_pct=0.20,
                    triggers=["Annual commitment", "Startup program", "Team size > 20"]
                )
            ),
            gtm=GoToMarket(
                channels={
                    "paid_digital": 0.4,
                    "content": 0.3,
                    "events": 0.05,
                    "outbound": 0.15,
                    "partnerships": 0.1
                },
                intensity=0.65,
                target_segments=["smb", "mid_market"]
            ),
            launch_day=0
        ),

        # Strategy 2: Enterprise Premium
        Strategy(
            id="enterprise_premium",
            name="Enterprise Premium",
            description="Lead with security and compliance, target Enterprise",
            messaging=Messaging(
                value_proposition="Enterprise-grade project management with white-glove support",
                primary_claim="Built for companies that can't afford to compromise on security",
                feature_emphasis={
                    "security": 0.9,
                    "compliance": 0.85,
                    "scalability": 0.8,
                    "integrations": 0.7,
                    "ease_of_use": 0.5
                },
                tone="enterprise",
                full_pitch="""
Your company runs critical operations. Your PM tool should be just as serious.

Nexus delivers SOC 2 Type II certified security, GDPR compliance out of the box,
and 99.99% uptime SLA. Backed by dedicated success managers who know your business.

This is project management built for enterprises.
"""
            ),
            pricing=Pricing(
                base_price=1.15,
                model="flat",
                discount=DiscountStrategy(
                    available=False,
                    max_discount_pct=0.0,
                    triggers=[]
                )
            ),
            gtm=GoToMarket(
                channels={
                    "paid_digital": 0.15,
                    "content": 0.2,
                    "events": 0.3,
                    "outbound": 0.25,
                    "partnerships": 0.1
                },
                intensity=0.5,
                target_segments=["enterprise", "mid_market"]
            ),
            launch_day=0
        ),

        # Strategy 3: Blitz
        Strategy(
            id="market_blitz",
            name="Market Blitz",
            description="High intensity across all segments with balanced messaging",
            messaging=Messaging(
                value_proposition="The project management revolution is here",
                primary_claim="Work smarter, not harder—finally, a PM tool that gets it",
                feature_emphasis={
                    "ease_of_use": 0.8,
                    "integrations": 0.7,
                    "security": 0.6,
                    "scalability": 0.6,
                    "compliance": 0.5
                },
                tone="innovative",
                full_pitch="""
Every other project management tool makes you choose:
Easy to use OR powerful. Affordable OR feature-rich.

Nexus breaks the tradeoff. Built from the ground up with modern teams in mind.
AI-powered workflows. Seamless integrations. Actually intuitive UX.

Join the revolution.
"""
            ),
            pricing=Pricing(
                base_price=0.85,
                model="per_seat",
                discount=DiscountStrategy(
                    available=True,
                    max_discount_pct=0.15,
                    triggers=["Annual commitment", "Growth plan"]
                )
            ),
            gtm=GoToMarket(
                channels={
                    "paid_digital": 0.35,
                    "content": 0.25,
                    "events": 0.1,
                    "outbound": 0.2,
                    "partnerships": 0.1
                },
                intensity=0.85,
                target_segments=["smb", "mid_market", "enterprise"]
            ),
            launch_day=0
        )
    ]
