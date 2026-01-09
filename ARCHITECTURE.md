# POPULOUS - Production Architecture Specification

## Decision Intelligence Engine - 27-Node System

---

## EXECUTIVE SUMMARY

This document specifies the production architecture for the Populous Decision Intelligence Engine.
Every node must output **real data** - no mocks, no placeholders.

**Core Principle**: Data flows through the graph. Each node transforms input data and produces
structured output that downstream nodes consume.

---

## DATA FLOW ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              DATA INPUT LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────┐    ┌──────────┐    ┌───────────────┐    ┌────────────────┐            │
│  │  BATCH  │───▶│ RESEARCH │───▶│ MARKET_SCANNER│───▶│ ALTERNATIVE_   │            │
│  │         │    │          │    │               │    │ DATA           │            │
│  └────┬────┘    └────┬─────┘    └───────┬───────┘    └───────┬────────┘            │
│       │              │                  │                    │                     │
│       │    ┌─────────┴──────────┐       │                    │                     │
│       │    │    NETWORK_GRAPH   │       │                    │                     │
│       │    └─────────┬──────────┘       │                    │                     │
│       │              │                  │                    │                     │
│       │    ┌─────────┴──────────┐  ┌────┴────────┐  ┌───────┴────────┐            │
│       │    │ FINANCIAL_SIGNALS  │  │ HISTORICAL  │  │    Exa API     │            │
│       │    └────────────────────┘  │  OUTCOMES   │  │  + Claude LLM  │            │
│       │                            └─────────────┘  └────────────────┘            │
│       ▼                                                                            │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              ANALYSIS LAYER                                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────────────┐          │
│  │ PREDICTION │───▶│ MONTE_CARLO │───▶│ SENSITIVITY │───▶│ COHORT_      │          │
│  │ (5-factor) │    │ (10K sims)  │    │  ANALYSIS   │    │ COMPARISON   │          │
│  └─────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬───────┘          │
│        │                  │                  │                  │                  │
│        │    ┌─────────────┴──────────┐       │                  │                  │
│        │    │   RISK_DECOMPOSITION   │◀──────┘                  │                  │
│        │    └─────────────┬──────────┘                          │                  │
│        │                  │                                     │                  │
│        │    ┌─────────────┴──────────┐    ┌─────────────────────┴───────┐          │
│        │    │    MARKET_TIMING       │    │  COMPETITIVE_DYNAMICS       │          │
│        │    └─────────────┬──────────┘    └──────────────┬──────────────┘          │
│        │                  │                              │                         │
│        │    ┌─────────────┴──────────┐    ┌──────────────┴──────────────┐          │
│        └───▶│  PORTFOLIO_OPTIMIZER   │◀───│    SCENARIO_PLANNER         │          │
│             └─────────────┬──────────┘    └──────────────┬──────────────┘          │
│                           │                              │                         │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              SIMULATION LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌────────────────┐    ┌───────────────┐    ┌──────────────────┐                   │
│  │ TRAJECTORY_SIM │───▶│  EXIT_MODELER │───▶│ FUNDING_SCENARIOS │                   │
│  │  (7yr growth)  │    │ (IPO/M&A/Fail)│    │   (Cap table)    │                   │
│  └────────┬───────┘    └───────┬───────┘    └────────┬─────────┘                   │
│           │                    │                     │                             │
└───────────┴────────────────────┴─────────────────────┴─────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              OUTPUT LAYER                                            │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌──────┐  ┌─────────────┐  ┌────────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │ CHAT │  │DECISION_BRIEF│  │INVESTMENT_MEMO │  │ RISK_REPORT │  │  COMPARISON  │  │
│  └──────┘  └─────────────┘  └────────────────┘  └─────────────┘  │   _MATRIX    │  │
│                                                                  └──────────────┘  │
│  ┌───────────────┐  ┌─────────────┐  ┌─────────────────┐  ┌──────────────────────┐│
│  │PORTFOLIO_DASH │  │ALERT_SYSTEM │  │STAKEHOLDER_VIEWS│  │WHATIF_EXPLORER       ││
│  └───────────────┘  └─────────────┘  └─────────────────┘  └──────────────────────┘│
│                                                                                    │
│  ┌────────────────────┐                                                            │
│  │ TIMELINE_PROJECTION│                                                            │
│  └────────────────────┘                                                            │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## NODE SPECIFICATIONS

### 1. DATA INPUT NODES

#### 1.1 BATCH (`/api/nodes/batch`)
**Status**: ✅ REAL (exists)
**Backend**: `api/startups.py` → `analyze_yc_batch()`

**Input**:
```json
{
  "batch_code": "W24",
  "max_companies": 10
}
```

**Output**:
```json
{
  "batch_name": "YC W24",
  "companies": ["Simular", "Greptile", ...],
  "batch_context": {
    "size": 200,
    "historical_unicorn_rate": 0.016,
    "theme": "AI/ML heavy"
  }
}
```

---

#### 1.2 RESEARCH (`/api/nodes/research`)
**Status**: ✅ REAL (exists)
**Backend**: `engine/data_sources.py` → `MultiSourceResearchEngine`

**Input**:
```json
{
  "company_name": "Greptile",
  "batch_context": { ... }
}
```

**Output**:
```json
{
  "founders": [
    {
      "name": "...",
      "linkedin": "...",
      "prior_exits": 0,
      "experience_years": 5,
      "education_tier": 1,
      "confidence": 0.8
    }
  ],
  "funding": {
    "total_raised": 2500000,
    "last_round": "Seed",
    "investors": ["YC", "..."],
    "confidence": 0.9
  },
  "traction": {
    "revenue_estimate": 500000,
    "users_estimate": 5000,
    "github_stars": 1200,
    "confidence": 0.6
  },
  "market": {
    "tam_estimate": 50000000000,
    "growth_rate": 0.25,
    "competitors": ["GitHub Copilot", "..."],
    "confidence": 0.7
  },
  "source_count": 18,
  "data_quality": "medium"
}
```

---

#### 1.3 MARKET_SCANNER (`/api/nodes/market_scanner`)
**Status**: ❌ NEEDS IMPLEMENTATION
**Purpose**: Real-time market intelligence

**Implementation**:
- Use Exa API to search for recent funding news, M&A, sector trends
- Search queries:
  - `"{sector} startup funding 2024"`
  - `"{sector} market trends"`
  - `"{sector} acquisitions"`
- Extract and aggregate signals

**Input**:
```json
{
  "sector": "developer tools",
  "companies": ["Greptile", "..."],
  "time_window_days": 90
}
```

**Output**:
```json
{
  "sector_funding_velocity": 0.15,  // % change in funding volume
  "recent_deals": [
    { "company": "...", "amount": 50000000, "date": "2024-01-15" }
  ],
  "sentiment_score": 0.72,
  "market_cycle_phase": "growth",
  "key_trends": ["AI code generation", "developer productivity"],
  "competitor_moves": [
    { "company": "GitHub", "move": "Launched Copilot X", "impact": "high" }
  ]
}
```

---

#### 1.4 NETWORK_GRAPH (`/api/nodes/network_graph`)
**Status**: ❌ NEEDS IMPLEMENTATION (engine exists: `network_engine.py`)
**Purpose**: Map investor/founder relationships

**Implementation**:
- Build graph from research data
- Use existing `NetworkEngine` logic
- Expose via API

**Input**:
```json
{
  "companies": ["Greptile", "Simular", ...],
  "include_investors": true,
  "include_founders": true,
  "depth": 2
}
```

**Output**:
```json
{
  "nodes": [
    { "id": "yc", "type": "investor", "name": "Y Combinator" },
    { "id": "greptile", "type": "company", "name": "Greptile" },
    { "id": "founder_1", "type": "person", "name": "..." }
  ],
  "edges": [
    { "from": "yc", "to": "greptile", "type": "invested" },
    { "from": "founder_1", "to": "greptile", "type": "founded" }
  ],
  "clusters": [
    { "id": "ai_cluster", "companies": ["Greptile", "Simular"], "common_investors": ["YC"] }
  ],
  "influence_scores": {
    "yc": 0.95,
    "a16z": 0.92
  }
}
```

---

#### 1.5 ALTERNATIVE_DATA (`/api/nodes/alternative_data`)
**Status**: ❌ NEEDS IMPLEMENTATION
**Purpose**: Non-traditional signals (job postings, GitHub, traffic)

**Implementation**:
- GitHub API for repo metrics
- Exa search for job postings
- Traffic estimation from proxy methods

**Input**:
```json
{
  "company_name": "Greptile",
  "signals": ["github", "jobs", "social"]
}
```

**Output**:
```json
{
  "github": {
    "repos": 5,
    "total_stars": 1500,
    "contributors": 12,
    "commit_velocity": 45,  // commits/week
    "star_growth_rate": 0.15
  },
  "jobs": {
    "open_positions": 8,
    "engineering_roles": 5,
    "growth_roles": 2,
    "hiring_velocity": "accelerating"
  },
  "social": {
    "twitter_followers": 2500,
    "linkedin_followers": 1200,
    "mention_sentiment": 0.8
  },
  "traffic_estimate": {
    "monthly_visits": 50000,
    "growth_rate": 0.12,
    "confidence": "low"
  }
}
```

---

#### 1.6 FINANCIAL_SIGNALS (`/api/nodes/financial_signals`)
**Status**: ❌ NEEDS IMPLEMENTATION
**Purpose**: Public comps, M&A data, valuation multiples

**Implementation**:
- Exa search for public company financials
- Extract revenue multiples by sector
- Recent M&A transactions

**Input**:
```json
{
  "sector": "developer tools",
  "stage": "seed",
  "geography": "US"
}
```

**Output**:
```json
{
  "public_comps": [
    { "name": "GitLab", "ticker": "GTLB", "revenue_multiple": 8.5, "market_cap": 7000000000 },
    { "name": "Atlassian", "ticker": "TEAM", "revenue_multiple": 12.0, "market_cap": 45000000000 }
  ],
  "recent_ma": [
    { "target": "Figma", "acquirer": "Adobe", "value": 20000000000, "multiple": 50 }
  ],
  "median_multiples": {
    "revenue": 10.5,
    "arr": 12.0,
    "users": 500
  },
  "sector_benchmarks": {
    "median_seed_valuation": 12000000,
    "median_series_a": 50000000,
    "capital_efficiency": 0.8
  }
}
```

---

#### 1.7 HISTORICAL_OUTCOMES (`/api/nodes/historical_outcomes`)
**Status**: ⚠️ PARTIAL (YC stats exist)
**Purpose**: Calibration data from historical outcomes

**Input**:
```json
{
  "accelerator": "YC",
  "vintage_years": [2018, 2019, 2020],
  "outcome_types": ["unicorn", "acquisition", "failure"]
}
```

**Output**:
```json
{
  "unicorn_rate": 0.016,
  "centaur_rate": 0.05,
  "acquisition_rate": 0.25,
  "failure_rate": 0.30,
  "median_time_to_exit": 7,
  "outcome_distribution": {
    "unicorn": { "count": 82, "median_years": 8 },
    "centaur": { "count": 250, "median_years": 6 },
    "acquisition": { "count": 1250, "median_years": 4 },
    "failure": { "count": 1500, "median_years": 3 }
  },
  "factor_correlations": {
    "team_prior_exits": 0.35,
    "market_tam": 0.28,
    "traction_growth": 0.42
  }
}
```

---

### 2. ANALYSIS NODES

#### 2.1 PREDICTION (`/api/nodes/prediction`)
**Status**: ✅ REAL (exists)
**Backend**: `engine/enhanced_prediction.py`

**Input**: Research data from upstream nodes
**Output**: Full PredictionResult with 5-factor scores

---

#### 2.2 MONTE_CARLO (`/api/nodes/monte_carlo`)
**Status**: ⚠️ PARTIAL (exists in scenario_engine, needs exposure)
**Purpose**: 10K simulations for uncertainty quantification

**Implementation**:
- Sample from factor distributions
- Run 10,000 simulations
- Return full distribution

**Input**:
```json
{
  "prediction": { ... },
  "factor_distributions": {
    "team": { "mean": 0.65, "std": 0.15 },
    "market": { "mean": 0.70, "std": 0.20 }
  },
  "simulations": 10000
}
```

**Output**:
```json
{
  "simulations": 10000,
  "outcome_distribution": {
    "unicorn_probability": {
      "mean": 0.082,
      "std": 0.045,
      "p5": 0.02,
      "p25": 0.05,
      "p50": 0.08,
      "p75": 0.11,
      "p95": 0.18
    }
  },
  "scenario_paths": [
    { "path_id": 1, "outcome": "unicorn", "years": 6, "valuation": 1500000000 },
    { "path_id": 2, "outcome": "acquisition", "years": 4, "valuation": 200000000 }
  ]
}
```

---

#### 2.3 SENSITIVITY (`/api/nodes/sensitivity`)
**Status**: ⚠️ PARTIAL (exists in confidence_engine)
**Purpose**: Which factors matter most?

**Input**:
```json
{
  "prediction": { ... },
  "variables": ["team", "market", "traction", "timing", "capital"],
  "range": 0.20
}
```

**Output**:
```json
{
  "sensitivity_matrix": {
    "team": { "impact_on_unicorn_prob": 0.15, "direction": "positive" },
    "market": { "impact_on_unicorn_prob": 0.12, "direction": "positive" },
    "traction": { "impact_on_unicorn_prob": 0.18, "direction": "positive" }
  },
  "factor_importance": [
    { "factor": "traction", "importance": 0.35 },
    { "factor": "team", "importance": 0.30 },
    { "factor": "market", "importance": 0.20 }
  ],
  "inflection_points": [
    { "factor": "traction", "threshold": 0.6, "impact": "unicorn_prob jumps 3x" }
  ]
}
```

---

#### 2.4 COHORT_COMPARISON (`/api/nodes/cohort_comparison`)
**Status**: ❌ NEEDS IMPLEMENTATION
**Purpose**: Compare current batch to historical cohorts

**Input**:
```json
{
  "current_batch": "YC W24",
  "current_predictions": [ ... ],
  "comparison_cohorts": ["YC W21", "YC W22", "YC W23"]
}
```

**Output**:
```json
{
  "percentile_rank": 72,  // Current batch is 72nd percentile vs history
  "cohort_comparison": [
    { "cohort": "YC W21", "avg_unicorn_prob": 0.05, "current_vs": "+15%" },
    { "cohort": "YC W22", "avg_unicorn_prob": 0.04, "current_vs": "+28%" }
  ],
  "trend_direction": "improving",
  "notable_patterns": [
    "AI-focused batches showing 2x higher unicorn rates",
    "Current batch has stronger team scores than W22"
  ]
}
```

---

#### 2.5 RISK_DECOMPOSITION (`/api/nodes/risk_decomposition`)
**Status**: ⚠️ PARTIAL (confidence_engine has this)
**Purpose**: Break down failure probability into specific risks

**Input**:
```json
{
  "prediction": { ... },
  "risk_categories": ["team", "market", "execution", "competition", "timing"]
}
```

**Output**:
```json
{
  "risk_breakdown": {
    "team_risk": 0.15,
    "market_risk": 0.10,
    "execution_risk": 0.25,
    "competition_risk": 0.20,
    "timing_risk": 0.10,
    "total_risk": 0.80
  },
  "failure_modes": [
    { "mode": "execution_failure", "probability": 0.35, "description": "Unable to ship product fast enough" },
    { "mode": "market_timing", "probability": 0.25, "description": "Market not ready for solution" }
  ],
  "mitigations": [
    { "risk": "execution_risk", "action": "Hire senior engineers", "impact": -0.10 }
  ],
  "residual_risk": 0.55
}
```

---

#### 2.6 MARKET_TIMING (`/api/nodes/market_timing`)
**Status**: ❌ NEEDS IMPLEMENTATION (internal scoring exists)
**Purpose**: Analyze market cycle position

**Input**:
```json
{
  "sector": "AI/ML",
  "current_date": "2024-01-15",
  "macro_indicators": {
    "interest_rates": 5.25,
    "vc_dry_powder": 290000000000,
    "tech_index": 15000
  }
}
```

**Output**:
```json
{
  "cycle_phase": "growth",
  "timing_score": 0.75,
  "sector_momentum": {
    "funding_trend": "accelerating",
    "deal_count_trend": "stable",
    "valuation_trend": "increasing"
  },
  "optimal_entry_window": {
    "start": "2024-01",
    "end": "2024-06",
    "confidence": 0.7
  },
  "macro_sentiment": 0.65,
  "comparable_periods": [
    { "period": "2020-Q3", "outcome": "Strong returns, AI boom" }
  ]
}
```

---

#### 2.7 COMPETITIVE_DYNAMICS (`/api/nodes/competitive_dynamics`)
**Status**: ✅ REAL (competitor_engine exists)
**Backend**: `engine/competitor_engine.py`

---

#### 2.8 PORTFOLIO_OPTIMIZER (`/api/nodes/portfolio_optimizer`)
**Status**: ❌ NEEDS IMPLEMENTATION
**Purpose**: Markowitz-style portfolio allocation

**Input**:
```json
{
  "companies": [
    { "name": "Greptile", "unicorn_prob": 0.08, "expected_return": 15.0, "sector": "devtools" },
    { "name": "Simular", "unicorn_prob": 0.12, "expected_return": 20.0, "sector": "AI" }
  ],
  "risk_tolerance": 0.7,
  "max_concentration": 0.25,
  "min_diversification": 5
}
```

**Output**:
```json
{
  "optimal_weights": {
    "Greptile": 0.18,
    "Simular": 0.22,
    "Company_3": 0.15
  },
  "expected_return": 3.5,  // 3.5x
  "portfolio_risk": 0.45,
  "sharpe_ratio": 2.1,
  "diversification_score": 0.78,
  "efficient_frontier": [
    { "risk": 0.3, "return": 2.0 },
    { "risk": 0.5, "return": 3.5 },
    { "risk": 0.7, "return": 4.5 }
  ]
}
```

---

#### 2.9 SCENARIO_PLANNER (`/api/nodes/scenario_planner`)
**Status**: ✅ REAL (scenario_engine exists)
**Backend**: `engine/scenario_engine.py`

---

### 3. SIMULATION NODES

#### 3.1 TRAJECTORY_SIM (`/api/nodes/trajectory_sim`)
**Status**: ❌ NEEDS IMPLEMENTATION
**Purpose**: 7-year growth simulation

**Input**:
```json
{
  "company": { ... },
  "prediction": { ... },
  "years": 7,
  "simulations": 1000
}
```

**Output**:
```json
{
  "growth_curves": {
    "revenue": [
      { "year": 1, "p10": 500000, "p50": 1000000, "p90": 2000000 },
      { "year": 2, "p10": 1500000, "p50": 4000000, "p90": 10000000 }
    ],
    "employees": [ ... ],
    "valuation": [ ... ]
  },
  "milestone_probabilities": {
    "series_a": { "probability": 0.85, "median_year": 1.5 },
    "series_b": { "probability": 0.55, "median_year": 3.0 },
    "unicorn": { "probability": 0.08, "median_year": 7.0 }
  },
  "stage_transitions": [
    { "from": "seed", "to": "series_a", "probability": 0.85 },
    { "from": "series_a", "to": "series_b", "probability": 0.65 }
  ]
}
```

---

#### 3.2 EXIT_MODELER (`/api/nodes/exit_modeler`)
**Status**: ❌ NEEDS IMPLEMENTATION
**Purpose**: Model exit paths (IPO, M&A, failure)

**Input**:
```json
{
  "company": { ... },
  "trajectory": { ... },
  "market_conditions": { ... }
}
```

**Output**:
```json
{
  "exit_probabilities": {
    "ipo": 0.05,
    "strategic_acquisition": 0.35,
    "acqui_hire": 0.15,
    "private_equity": 0.10,
    "failure": 0.35
  },
  "expected_multiples": {
    "ipo": 25.0,
    "strategic_acquisition": 8.0,
    "acqui_hire": 1.5
  },
  "exit_timing": {
    "ipo": { "median_years": 8, "range": [6, 12] },
    "acquisition": { "median_years": 5, "range": [3, 8] }
  },
  "potential_acquirers": [
    { "company": "Microsoft", "probability": 0.15, "strategic_fit": "high" },
    { "company": "Google", "probability": 0.10, "strategic_fit": "medium" }
  ]
}
```

---

#### 3.3 FUNDING_SCENARIOS (`/api/nodes/funding_scenarios`)
**Status**: ❌ NEEDS IMPLEMENTATION
**Purpose**: Model future rounds and dilution

**Input**:
```json
{
  "current_cap_table": {
    "founders": 0.60,
    "investors": 0.30,
    "option_pool": 0.10
  },
  "current_valuation": 15000000,
  "trajectory": { ... }
}
```

**Output**:
```json
{
  "future_rounds": [
    {
      "round": "Series A",
      "probability": 0.85,
      "timing_months": 18,
      "amount": 10000000,
      "pre_money": 40000000,
      "dilution": 0.20
    },
    {
      "round": "Series B",
      "probability": 0.55,
      "timing_months": 36,
      "amount": 30000000,
      "pre_money": 120000000,
      "dilution": 0.20
    }
  ],
  "ownership_evolution": {
    "founders_at_exit": 0.35,
    "early_investors_at_exit": 0.25
  },
  "total_dilution": 0.55
}
```

---

### 4. OUTPUT NODES

#### 4.1 CHAT (`/api/nodes/chat`)
**Status**: ✅ REAL (exists)

---

#### 4.2 DECISION_BRIEF (`/api/nodes/decision_brief`)
**Status**: ❌ NEEDS IMPLEMENTATION
**Purpose**: One-page executive summary

**Input**: All upstream analysis data
**Output**: Structured document with recommendation

---

#### 4.3 INVESTMENT_MEMO (`/api/nodes/investment_memo`)
**Status**: ❌ NEEDS IMPLEMENTATION (export_engine exists)
**Purpose**: Full investment thesis document

---

#### 4.4 RISK_REPORT (`/api/nodes/risk_report`)
**Status**: ❌ NEEDS IMPLEMENTATION
**Purpose**: Comprehensive risk assessment

---

#### 4.5 PORTFOLIO_DASHBOARD (`/api/nodes/portfolio_dashboard`)
**Status**: ❌ NEEDS IMPLEMENTATION
**Purpose**: Real-time portfolio monitoring

---

#### 4.6 COMPARISON_MATRIX (`/api/nodes/comparison_matrix`)
**Status**: ❌ NEEDS IMPLEMENTATION
**Purpose**: Side-by-side company comparison

---

#### 4.7 ALERT_SYSTEM (`/api/nodes/alert_system`)
**Status**: ❌ NEEDS IMPLEMENTATION
**Purpose**: Trigger-based notifications

---

#### 4.8 STAKEHOLDER_VIEWS (`/api/nodes/stakeholder_views`)
**Status**: ❌ NEEDS IMPLEMENTATION
**Purpose**: Role-specific dashboards

---

#### 4.9 WHATIF_EXPLORER (`/api/nodes/whatif_explorer`)
**Status**: ❌ NEEDS IMPLEMENTATION
**Purpose**: Interactive sensitivity UI

---

#### 4.10 TIMELINE_PROJECTION (`/api/nodes/timeline_projection`)
**Status**: ❌ NEEDS IMPLEMENTATION
**Purpose**: Gantt-style milestone visualization

---

## IMPLEMENTATION PRIORITY

### Phase 1: Core Pipeline (Week 1)
1. ✅ BATCH - exists
2. ✅ RESEARCH - exists
3. ✅ PREDICTION - exists
4. ✅ CHAT - exists
5. 🔨 MONTE_CARLO - expose existing
6. 🔨 SENSITIVITY - expose existing
7. 🔨 RISK_DECOMPOSITION - expose existing

### Phase 2: Market Intelligence (Week 2)
8. 🔨 MARKET_SCANNER - new
9. 🔨 FINANCIAL_SIGNALS - new
10. 🔨 ALTERNATIVE_DATA - new
11. 🔨 MARKET_TIMING - new
12. 🔨 HISTORICAL_OUTCOMES - enhance

### Phase 3: Advanced Analysis (Week 2-3)
13. 🔨 NETWORK_GRAPH - expose existing
14. 🔨 COHORT_COMPARISON - new
15. 🔨 PORTFOLIO_OPTIMIZER - new
16. ✅ COMPETITIVE_DYNAMICS - exists
17. ✅ SCENARIO_PLANNER - exists

### Phase 4: Simulation (Week 3)
18. 🔨 TRAJECTORY_SIM - new
19. 🔨 EXIT_MODELER - new
20. 🔨 FUNDING_SCENARIOS - new

### Phase 5: Output Generation (Week 4)
21. 🔨 DECISION_BRIEF - new
22. 🔨 INVESTMENT_MEMO - new
23. 🔨 RISK_REPORT - new
24. 🔨 COMPARISON_MATRIX - new
25. 🔨 PORTFOLIO_DASHBOARD - new
26. 🔨 ALERT_SYSTEM - new
27. 🔨 STAKEHOLDER_VIEWS - new
28. 🔨 WHATIF_EXPLORER - new
29. 🔨 TIMELINE_PROJECTION - new

---

## API DESIGN

All node endpoints follow a consistent pattern:

```
POST /api/nodes/{node_type}
Content-Type: application/json

{
  "input": { ... node-specific input ... },
  "upstream_data": { ... data from connected nodes ... },
  "config": { ... optional configuration ... }
}
```

Response:
```json
{
  "node_type": "monte_carlo",
  "status": "complete",
  "execution_time_ms": 1250,
  "output": { ... node-specific output ... },
  "metadata": {
    "data_quality": "high",
    "confidence": 0.85,
    "sources": ["exa", "claude", "github"]
  }
}
```

---

## FRONTEND INTEGRATION

The frontend should:

1. **Execute nodes in dependency order**
2. **Pass output from completed nodes as input to downstream nodes**
3. **Display real-time progress and intermediate results**
4. **Cache node outputs for re-use**

Example flow:
```typescript
async function runPipeline(batchCode: string) {
  // Layer 1: Input
  const batchResult = await api.nodes.batch({ batch_code: batchCode });

  // Layer 2: Research (parallel for each company)
  const researchResults = await Promise.all(
    batchResult.companies.map(c => api.nodes.research({ company_name: c }))
  );

  // Layer 3: Analysis
  const predictions = await Promise.all(
    researchResults.map(r => api.nodes.prediction({ research_data: r }))
  );

  // Layer 4: Monte Carlo
  const monteCarloResults = await api.nodes.monte_carlo({
    predictions,
    simulations: 10000
  });

  // ... continue through all connected nodes
}
```
