# PREDICTION ARCHITECTURE - Technical Specification

## Production-Grade Startup Prediction System

---

## Executive Summary

The current system extracts surface-level data and applies generic weights. A real prediction system needs:
1. **Deep, structured data extraction** - specific data points, not summaries
2. **Multiple corroborating sources** - confidence from triangulation
3. **Historical calibration** - backtest against known outcomes
4. **Proper simulation** - model the actual startup lifecycle

---

## 1. DATA REQUIREMENTS (SPECIFIC)

### 1.1 Team Score (30% weight)

| Data Point | Type | Source Priority | Scoring Method |
|------------|------|-----------------|----------------|
| `prior_exits_count` | int | Crunchbase, LinkedIn | 0=0.0, 1=0.2, 2+=0.3 bonus |
| `prior_exit_value_usd` | float | Crunchbase, PitchBook | <$10M=0.1, $10-100M=0.2, $100M+=0.3 |
| `years_total_experience` | int | LinkedIn | <5=0.05, 5-10=0.10, 10+=0.15 |
| `years_domain_experience` | int | LinkedIn | <2=0.0, 2-5=0.05, 5+=0.10 |
| `education_tier` | enum | LinkedIn | Tier1=0.05, Tier2=0.03, Other=0.01 |
| `prior_company_tier` | enum | LinkedIn | FAANG/Unicorn=0.05, YC-backed=0.03 |
| `linkedin_connections` | int | LinkedIn API | >500=0.02, >1000=0.03, >5000=0.05 |
| `yc_network_member` | bool | YC Directory | True=0.10 |
| `github_contributions` | int | GitHub API | >1000=0.03 |
| `patents_filed` | int | USPTO | >0=0.02, >5=0.05 |

**Prior Exit Scoring Formula:**
```python
def score_prior_exits(exits: List[Exit]) -> float:
    score = 0.0
    for exit in exits:
        base = 0.15
        value_mult = min(1.0, math.log10(max(1, exit.value_usd)) / 9)
        recency = 0.95 ** exit.years_since
        role_weight = {"founder": 1.0, "c_suite": 0.7, "vp": 0.4}.get(exit.role, 0.3)
        score += base * value_mult * recency * role_weight
    return min(0.4, score)
```

**Network Strength Definition:**
- Strong (>0.7): 3+ top-tier VC connections, YC alumni, 2+ successful co-founders
- Medium (0.4-0.7): 1-2 VC connections, some accelerator network
- Weak (<0.4): No VC connections, no accelerator, network <1000

**Education Tier:**
- Tier 1: Stanford, MIT, Harvard, Berkeley, Caltech, Princeton, Yale, CMU
- Tier 2: UCLA, Michigan, UT Austin, Georgia Tech, Penn, Duke, Northwestern
- Tier 3: Any accredited with relevant degree

### 1.2 Market Score (25% weight)

| Metric | Data Type | Source | Validation |
|--------|-----------|--------|------------|
| `tam_usd` | float | Gartner, IDC, Statista | Cross-reference 3 sources |
| `sam_usd` | float | Analyst reports | TAM * addressable_pct |
| `market_growth_rate_yoy` | float | IBISWorld, Statista | 5-year CAGR |
| `competition_hhi` | float | Crunchbase | Herfindahl-Hirschman Index |
| `winner_take_all_score` | float | Derived | Network effects, switching costs |

**TAM Acquisition Priority:**
1. Industry analyst reports (Gartner, IDC) - confidence 0.95
2. Public company filings in same market - confidence 0.9
3. Aggregated startup claims (discount 0.6) - confidence 0.5
4. Bottom-up: customer count × ARPU
5. Top-down from adjacent market

**Competition Intensity:**
```python
intensity = (
    (1 - hhi) * 0.30 +                    # Market fragmentation
    (competitor_count / 20) * 0.25 +       # Number of funded players
    (total_vc_funding / tam * 10) * 0.25 + # Funding intensity
    (recent_entrants / 10) * 0.20          # New entrant rate
)
```

### 1.3 Traction Score (20% weight)

**Revenue Estimation Methods (when not public):**

| Method | Formula | Confidence |
|--------|---------|------------|
| Employee count | employees × $150K/employee | 0.5 |
| Customer count | customers × industry_ARPU × 12 | 0.6 |
| Web traffic | visitors × 2% × $100 × 12 | 0.4 |
| Funding efficiency | funding × 0.5 × (months/24) | 0.3 |

**Revenue Per Employee Benchmarks:**
- SaaS Early: $100K
- SaaS Growth: $200K
- Marketplace: $500K
- Enterprise: $250K
- Fintech: $350K

**Growth Signal Proxies:**
- Hiring velocity: engineering +1.5x, sales +2.0x
- Web traffic growth (SimilarWeb)
- GitHub stars growth
- Social mention growth
- Job posting count

**Product-Market Fit Indicators:**
- High NPS (>50)
- Low churn mentions
- Expansion revenue >10%
- Word-of-mouth references
- DAU/MAU >20%
- Inbound demand signals

### 1.4 Timing Score (15% weight)

**Market Cycle Phases:**
| Phase | Signals | Score |
|-------|---------|-------|
| Nascent | Market undefined, no leader, enabling tech | 0.6 |
| Emerging | First unicorn, major adoption, regulatory clarity | 0.9 |
| Growth | Multiple players, proven models, consolidation | 0.7 |
| Mature | Concentration, price wars, commoditization | 0.4 |
| Declining | Disruption, customer shift, obsolescence | 0.2 |

**Regulatory Risk by Industry:**
- High Risk (0.2-0.4): fintech, healthcare, crypto, defense
- Moderate (0.5-0.7): edtech, proptech, insurtech
- Low Risk (0.8-1.0): SaaS, dev tools, productivity

### 1.5 Capital Score (10% weight)

**Funding Trajectory Scoring:**
- Valuation step-up ≥2x: +0.10
- Valuation step-up ≥1x: +0.05
- Down round: -0.15
- Round pace 12-24 months: +0.05
- Round pace >36 months: -0.05

**Capital Efficiency Benchmarks:**
| Model | Excellent | Good | Average |
|-------|-----------|------|---------|
| SaaS | ARR/Funding = 1.0 | 0.5 | 0.25 |
| Marketplace | GMV/Funding = 5.0 | 2.0 | 1.0 |
| Consumer | Users/M$ = 100K | 50K | 10K |

---

## 2. DATA SOURCES & APIs

### 2.1 Free APIs

| Source | Data | Quality | Limits |
|--------|------|---------|--------|
| **Exa API** | Web search | High | 1000/day free |
| **GitHub API** | Repos, stars | High | 5000/hr |
| **Crunchbase Basic** | Overview | High | 200/month |
| **Twitter API** | Followers | Medium | 1500/15min |
| **SEC EDGAR** | Filings | High | Unlimited |
| **USPTO** | Patents | High | Unlimited |
| **Product Hunt** | Launches | Medium | 450/day |

### 2.2 Paid APIs (Recommended)

| Source | Data | Cost | Priority |
|--------|------|------|----------|
| **Crunchbase Pro** | Full funding | $99/mo | P1 |
| **Proxycurl (LinkedIn)** | Profiles | $49/mo | P1 |
| **SimilarWeb** | Traffic | $500/mo | P2 |
| **BuiltWith** | Tech stack | $295/mo | P3 |

**Monthly Cost: ~$650 for comprehensive data**

### 2.3 Alternative Data Signals

| Signal | Proxy For | Source |
|--------|-----------|--------|
| Job postings | Growth, burn | Indeed, Lever |
| Web traffic | Traction | SimilarWeb |
| App downloads | Consumer traction | App Annie |
| GitHub stars | Developer adoption | GitHub |
| G2 reviews | B2B adoption | G2 |
| Patent filings | Technical moat | USPTO |

---

## 3. PREDICTION MODELS

### 3.1 Current Factor Model
```python
composite = (
    team_score * 0.30 +
    market_score * 0.25 +
    traction_score * 0.20 +
    timing_score * 0.15 +
    capital_score * 0.10
)

# Logistic transformation calibrated to 1.6% base rate
odds_multiplier = math.exp(4 * (composite - 0.5))
unicorn_prob = min(0.6, 0.016 * odds_multiplier)
```

**Pros:** Interpretable, fast, stable, explainable
**Cons:** Weights not validated, linear, no uncertainty

### 3.2 ML Model (XGBoost)
- Train on 500+ YC companies with known outcomes
- Handle 1.6% class imbalance with SMOTE
- Calibrate with isotonic regression
- Feature importance for explainability

**Training Data Required:**
- 500+ YC companies, 5+ years old
- Known outcomes (unicorn/exit/failed/active)
- 80%+ feature coverage

### 3.3 Monte Carlo Simulation
- Model startup lifecycle as Markov chain
- Stages: Seed → Series A → B → C → Growth → Exit
- Adjust transition probabilities by factors
- 10,000 simulations per startup
- Output: probability distribution, not point estimate

### 3.4 RECOMMENDED: Ensemble Approach
```python
ensemble_prob = (
    factor_model_pred * 0.30 +
    ml_model_pred * 0.40 +
    simulation_pred * 0.30
)

uncertainty = std(model_predictions)
confidence_interval = (prob - 2*std, prob + 2*std)
```

**Benefits:**
- Factor model provides interpretability
- ML captures non-linear interactions
- Simulation provides uncertainty quantification
- Model disagreement signals low confidence

---

## 4. CALIBRATION STRATEGY

### 4.1 Backtest on Historical Batches
- Test on W14-S18 batches (7+ years old)
- Compare predictions to actual outcomes
- Calculate Brier score, ROC-AUC, calibration error

### 4.2 Target Metrics
| Metric | Excellent | Good | Acceptable |
|--------|-----------|------|------------|
| Brier Score | <0.01 | <0.02 | <0.05 |
| ROC-AUC | >0.80 | >0.70 | >0.60 |
| Calibration Error | <2% | <5% | <10% |

### 4.3 Continuous Recalibration
- Monthly calibration check
- Trigger recalibration if error >5%
- Use isotonic regression for probability adjustment

---

## 5. IMPLEMENTATION ROADMAP

### Phase 1: Enhanced Data Collection (2-3 weeks)
**What we can do NOW with Exa + Claude:**

1. **Multi-query research strategy:**
```python
QUERIES = {
    "founder": ["{name} founder CEO background", "{name} founder exits"],
    "traction": ["{name} customers revenue growth", "{name} ARR MRR"],
    "market": ["{name} TAM market size", "{name} competitors"],
    "funding": ["site:crunchbase.com {name}", "{name} Series funding"]
}
```

2. **Structured extraction prompts** with confidence ratings
3. **Per-field confidence scoring**
4. **Source triangulation**

### Phase 2: API Integration (3-4 weeks)
1. Crunchbase Pro ($99/mo) - definitive funding data
2. Proxycurl/LinkedIn ($49/mo) - founder profiles
3. SimilarWeb ($500/mo) - traffic signals
4. GitHub API (free) - technical signals

### Phase 3: ML/Simulation (4-6 weeks)
1. Collect training data from W12-S18 batches
2. Implement XGBoost classifier
3. Build Monte Carlo simulator
4. Create ensemble predictor
5. Backtest and calibrate

---

## 6. QUICK WINS (This Week)

1. **Enhance Exa queries** - 4 queries per startup instead of 1
2. **Structured extraction** - JSON with confidence per field
3. **Source counting** - higher confidence with more sources
4. **Better prompts** - ask for specific metrics, not summaries
5. **Fallback estimates** - use proxies when direct data unavailable

---

## Files to Modify

1. `backend/engine/startup_engine.py` - Core prediction logic
2. `backend/api/startups.py` - API endpoints
3. Create: `backend/engine/data_sources/` - API integrations
4. Create: `backend/engine/calibration.py` - Calibration tracking
