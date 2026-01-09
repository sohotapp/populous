# Populous: Decision Intelligence Platform - Architecture V2

## Vision

"There's a future where you win. We engineer that for you."

Populous is a decision intelligence platform for F500 leaders that:
1. Researches companies and markets in real-time
2. Generates synthetic populations with game-theoretic competitor agents
3. Simulates futures with full causality tracking
4. Provides execution plans, not just probabilities

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              POPULOUS PLATFORM                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   RESEARCH  │───▶│    WORLD    │───▶│  SIMULATION │───▶│   DECISION  │  │
│  │   ENGINE    │    │  GENERATOR  │    │   ENGINE    │    │    LAYER    │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                  │                  │                  │          │
│         ▼                  ▼                  ▼                  ▼          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         SUPABASE (PostgreSQL + Vector)               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    FRONTEND (Next.js + D3 Canvas)                    │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │   │
│  │  │ Workflow │  │  Agent   │  │ Scenario │  │  Trace   │             │   │
│  │  │  Canvas  │  │ Network  │  │  Branch  │  │   DAG    │             │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Backend Components

### 1. Research Engine (`research_engine.py`)

**Purpose:** Deep company and market research using live web data

**APIs:**
- Exa API for semantic web search
- Claude for synthesis and analysis

**Flow:**
```
Input: "Notion"
    ↓
Exa Search: Company info, competitors, pricing, news
    ↓
Claude Synthesis: Structure into World model
    ↓
Output: Complete Company Profile + Market Context
```

**Data Gathered:**
- Company overview (size, funding, revenue, employees)
- Product details (features, pricing tiers, positioning)
- Competitors (direct and indirect)
- Market dynamics (growth rate, trends, disruptions)
- Customer segments (who buys, why, pain points)
- Recent news (last 6 months of announcements)
- Leadership (key decision makers, their backgrounds)

### 2. Competitor Engine (`competitor_engine.py`)

**Purpose:** Game-theoretic competitor agents that respond strategically

**Game Theory Implementation:**
- Each competitor has: Goals, Resources, Strategy, Risk Tolerance
- Competitors observe your moves and respond
- Response timing: Immediate, Delayed, Never
- Response types: Match, Undercut, Differentiate, Ignore

**Nash Equilibrium Calculation:**
```python
class CompetitorAgent:
    def calculate_best_response(self, your_move, market_state):
        """
        Given your move and market state, calculate optimal response.
        Uses backward induction for sequential games.
        """
        payoff_matrix = self.build_payoff_matrix(your_move, market_state)
        best_response = self.find_nash_equilibrium(payoff_matrix)
        return best_response
```

**Competitor Strategies:**
- **Aggressive:** Match or undercut any price move
- **Defensive:** Protect market share, match if threatened
- **Opportunistic:** Wait for weakness, then strike
- **Passive:** Focus on own roadmap, ignore competitors

### 3. Scenario Engine (`scenario_engine.py`)

**Purpose:** Generate and track branching futures

**Structure:**
```
                    [Your Decision]
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
    [Competitor A    [Competitor B   [No Competitor
     Responds]        Responds]       Response]
         │                │               │
    ┌────┴────┐      ┌────┴────┐     ┌────┴────┐
    ▼         ▼      ▼         ▼     ▼         ▼
[High      [Low   [High     [Low  [High     [Low
 Churn]    Churn]  Churn]   Churn] Churn]   Churn]
 (15%)     (35%)   (12%)    (23%)  (8%)     (52%)
```

**Probability Calculation:**
- Each branch has probability based on:
  - Competitor likelihood to respond
  - Customer segment sensitivity
  - Market conditions
- Monte Carlo within branches for statistical rigor

### 4. Confidence Engine (`confidence_engine.py`)

**Purpose:** Decompose confidence into interpretable components

**Components:**
```
Overall Confidence: 73%
├── Customer Behavior Model: 90%
│   ├── Historical validation: 95%
│   ├── Segment coverage: 85%
│   └── Recency of data: 90%
├── Market Assumptions: 85%
│   ├── Growth rate stability: 90%
│   ├── No major disruptions: 80%
│   └── Regulatory stability: 85%
├── Competitor Baseline: 80%
│   ├── Known strategy: 85%
│   ├── Resource constraints: 75%
│   └── Historical patterns: 80%
└── Execution Feasibility: 88%
    ├── Internal capability: 90%
    ├── Timeline realism: 85%
    └── Resource availability: 90%
```

**Sensitivity Analysis:**
- Which component, if wrong, causes biggest outcome change?
- Highlight for validation focus

### 5. Journal Engine (`journal_engine.py`)

**Purpose:** Audit trail for compliance and learning

**Captured:**
- Decision created: timestamp, user, inputs
- Research performed: sources, findings
- Simulation run: parameters, branches, outcomes
- Recommendation made: confidence, alternatives
- Actual decision: what was chosen
- Outcome tracking: predicted vs actual (future)

**Format:**
```json
{
  "decision_id": "dec_123",
  "timeline": [
    {"event": "created", "timestamp": "...", "data": {...}},
    {"event": "research_completed", "timestamp": "...", "sources": [...]},
    {"event": "simulation_run", "timestamp": "...", "branches": 100},
    {"event": "recommendation_generated", "timestamp": "...", "confidence": 0.73},
    {"event": "decision_made", "timestamp": "...", "chosen": "option_a"}
  ]
}
```

---

## Data Models

### Company
```python
class Company(BaseModel):
    id: str
    name: str
    description: str
    industry: str
    founded: int
    employees: str  # "100-500", "1000-5000", etc.
    funding: Optional[str]
    revenue: Optional[str]
    headquarters: str

    products: List[Product]
    leadership: List[Leader]
    recent_news: List[NewsItem]

    market_position: str  # "leader", "challenger", "niche"
    strengths: List[str]
    weaknesses: List[str]

    created_at: datetime
    research_sources: List[str]
```

### CompetitorAgent
```python
class CompetitorAgent(BaseModel):
    id: str
    company: Company

    # Strategy parameters
    strategy_type: str  # "aggressive", "defensive", "opportunistic", "passive"
    risk_tolerance: float  # 0-1
    response_speed: str  # "immediate", "delayed", "slow"
    price_sensitivity: float  # How likely to respond to price changes

    # Resources
    marketing_budget: str  # "low", "medium", "high"
    product_velocity: str  # How fast they ship

    # Game theory
    payoff_weights: Dict[str, float]  # What they optimize for

    def respond_to_move(self, move: Dict, market: Dict) -> Optional[Dict]:
        """Calculate and return best response to a move"""
        pass
```

### ScenarioBranch
```python
class ScenarioBranch(BaseModel):
    id: str
    parent_id: Optional[str]

    trigger: str  # What caused this branch
    probability: float  # Likelihood of this branch

    competitor_responses: Dict[str, Dict]  # competitor_id -> response
    customer_outcomes: Dict[str, float]  # metric -> value

    children: List[str]  # child branch IDs

    timeline: List[DailySnapshot]
    final_metrics: Dict[str, float]
```

### ConfidenceDecomposition
```python
class ConfidenceComponent(BaseModel):
    name: str
    value: float  # 0-1
    children: List['ConfidenceComponent']
    sensitivity: float  # How much overall changes if this is wrong
    validation_suggestions: List[str]

class ConfidenceDecomposition(BaseModel):
    overall: float
    components: List[ConfidenceComponent]
    weakest_link: str
    validation_priority: List[str]
```

### DecisionJournalEntry
```python
class JournalEntry(BaseModel):
    id: str
    decision_id: str
    event_type: str
    timestamp: datetime
    user_id: Optional[str]
    data: Dict

class DecisionJournal(BaseModel):
    decision_id: str
    entries: List[JournalEntry]

    def add_entry(self, event_type: str, data: Dict):
        pass

    def export_markdown(self) -> str:
        pass

    def export_pdf(self) -> bytes:
        pass
```

---

## Frontend Architecture

### Design System: Linear Verbatim

**Colors:**
```css
--bg-primary: #0A0A0B;
--bg-secondary: #141415;
--bg-tertiary: #1C1C1E;
--border: #2A2A2D;
--text-primary: #FFFFFF;
--text-secondary: #8A8A8E;
--text-tertiary: #5C5C5F;
--accent: #5E6AD2;
--accent-hover: #6E7AE2;
--success: #3CCB7F;
--warning: #F5A623;
--error: #E5484D;
```

**Typography:**
```css
--font-family: 'Inter', -apple-system, sans-serif;
--font-size-xs: 11px;
--font-size-sm: 12px;
--font-size-base: 13px;
--font-size-lg: 14px;
--font-size-xl: 16px;
--font-size-2xl: 20px;
--font-size-3xl: 24px;
```

**Spacing:**
```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
```

**Components:**
- Buttons: Ghost, Secondary, Primary
- Inputs: Dark with subtle borders
- Cards: Subtle elevation, rounded corners
- Modals: Centered, backdrop blur
- Tooltips: Dark, compact
- Dropdowns: Animated, keyboard navigable

### Canvas System (Custom D3)

**Features:**
- Infinite pan/zoom (like Figma)
- Node placement and connection
- Snap-to-grid (optional)
- Multi-select
- Copy/paste
- Undo/redo
- Keyboard shortcuts

**Node Types:**
1. **Decision Node** - Starting point, defines the question
2. **Research Node** - Shows company/market research
3. **World Node** - Market context configuration
4. **Audience Node** - Synthetic population
5. **Competitor Node** - Game-theoretic competitor
6. **Simulation Node** - Run and configure simulation
7. **Results Node** - Aggregate outcomes
8. **Branch Node** - Scenario branch point
9. **Trace Node** - Causal analysis
10. **Plan Node** - Execution recommendations

**Connections:**
- Bezier curves with arrows
- Animated data flow
- Click to inspect data passing between nodes

### Visualizations

**1. Agent Network (Force-Directed)**
```
- 500 nodes, clustered by segment
- Node size = influence
- Node color = state (retained/churned/evaluating)
- Edge thickness = relationship strength
- Hover: Show agent summary
- Click: Open agent detail/chat
- Animation: Influence cascade over time
```

**2. Scenario Branching Tree**
```
- Vertical tree layout
- Branch width = probability
- Color = outcome quality
- Click branch to explore
- Hover: Show key metrics
- Collapse/expand branches
```

**3. Timeline Playback**
```
- Horizontal timeline
- Scrub through simulation days
- Event markers (announcements, responses)
- State distribution area chart
- Speed controls (1x, 2x, 4x)
```

**4. Causal Trace DAG**
```
- Directed acyclic graph
- Nodes = events/decisions/outcomes
- Edges = causal relationships
- Edge thickness = causal strength
- Click path to see explanation
- Highlight critical path
```

**5. Confidence Decomposition**
```
- Treemap or sunburst chart
- Size = contribution to confidence
- Color = sensitivity
- Click to drill down
- Hover: Validation suggestions
```

### Views

**1. Canvas View (Default)**
- Workflow nodes for process
- Entity exploration post-simulation
- Pan/zoom navigation

**2. Dashboard View**
- Metrics cards
- Charts and tables
- Traditional BI-style layout

**3. Stakeholder Views**
- CEO: Strategic summary, key risks, recommendation
- CFO: Financial impact, ROI, cost analysis
- CMO: Customer sentiment, segment breakdown, messaging
- Ops: Execution timeline, resource needs, dependencies

**4. Present Mode**
- Full-screen
- Keyboard navigation
- Presenter notes
- Board-ready formatting

---

## API Endpoints

### Research
```
POST /api/research/company
  Input: { "query": "Notion", "depth": "deep" }
  Output: { "company": Company, "competitors": [Company], "market": Market }

GET /api/research/{research_id}
  Output: Full research results with sources
```

### Decisions
```
POST /api/decisions
  Input: CreateDecisionInput
  Output: { "id": str, "decision": Decision }

GET /api/decisions/{id}
  Output: Decision with all related data

POST /api/decisions/{id}/simulate
  Input: SimulationConfig
  Output: { "simulation_id": str, "status": "running" }

GET /api/decisions/{id}/branches
  Output: { "branches": [ScenarioBranch], "probabilities": {...} }

GET /api/decisions/{id}/confidence
  Output: ConfidenceDecomposition

GET /api/decisions/{id}/journal
  Output: DecisionJournal

POST /api/decisions/{id}/export
  Input: { "format": "markdown" | "pdf" }
  Output: File
```

### Simulation
```
GET /api/simulations/{id}/status
  Output: { "status": str, "progress": float, "eta": str }

GET /api/simulations/{id}/timeline
  Input: { "day": int }
  Output: DailySnapshot

GET /api/simulations/{id}/agents
  Output: { "agents": [GenerativeAgent] }

POST /api/simulations/{id}/agents/{agent_id}/chat
  Input: { "message": str }
  Output: AgentChatResponse
```

### Competitors
```
GET /api/competitors
  Output: { "competitors": [CompetitorAgent] }

POST /api/competitors/{id}/predict-response
  Input: { "your_move": Move }
  Output: { "response": CompetitorResponse, "probability": float }
```

---

## Database Schema (Supabase)

### Tables

```sql
-- Companies (from research)
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  data JSONB NOT NULL,
  research_sources TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Decisions
CREATE TABLE decisions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT,
  status TEXT DEFAULT 'draft',
  company_id UUID REFERENCES companies(id),
  world_data JSONB,
  options JSONB,
  constraints JSONB,
  success_criteria JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Simulations
CREATE TABLE simulations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  decision_id UUID REFERENCES decisions(id),
  config JSONB NOT NULL,
  status TEXT DEFAULT 'pending',
  progress FLOAT DEFAULT 0,
  results JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Agents (stored for reuse and chat)
CREATE TABLE agents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  simulation_id UUID REFERENCES simulations(id),
  data JSONB NOT NULL,
  memory_stream JSONB DEFAULT '[]',
  final_state TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Scenario Branches
CREATE TABLE branches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  simulation_id UUID REFERENCES simulations(id),
  parent_id UUID REFERENCES branches(id),
  trigger TEXT,
  probability FLOAT,
  outcomes JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Decision Journal
CREATE TABLE journal_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  decision_id UUID REFERENCES decisions(id),
  event_type TEXT NOT NULL,
  data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Recommendations
CREATE TABLE recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  decision_id UUID REFERENCES decisions(id),
  simulation_id UUID REFERENCES simulations(id),
  recommended_option TEXT,
  confidence FLOAT,
  execution_plan JSONB,
  contingencies JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Vector Store (for semantic search)

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Agent embeddings for similarity search
CREATE TABLE agent_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id UUID REFERENCES agents(id),
  embedding vector(1536),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Research embeddings for retrieval
CREATE TABLE research_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID REFERENCES companies(id),
  chunk_text TEXT,
  embedding vector(1536),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## External APIs

### Exa API (Web Research)
```python
from exa_py import Exa

exa = Exa(api_key=os.getenv("EXA_API_KEY"))

# Semantic search for company info
results = exa.search_and_contents(
    query=f"{company_name} company overview competitors pricing",
    num_results=20,
    use_autoprompt=True,
    text=True
)
```

### Anthropic API (Claude)
```python
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Research synthesis
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=[{"role": "user", "content": synthesis_prompt}]
)
```

---

## Deployment (Railway)

### Services
1. **populous-api** - FastAPI backend
2. **populous-web** - Next.js frontend

### Environment Variables
```
# Backend
ANTHROPIC_API_KEY=...
EXA_API_KEY=...
SUPABASE_URL=...
SUPABASE_KEY=...

# Frontend
NEXT_PUBLIC_API_URL=https://populous-api.railway.app
```

### Build Commands
```
# Backend
pip install -r requirements.txt
uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT

# Frontend
npm install
npm run build
npm start
```

---

## Demo Flow (10 Minutes)

### 0:00-1:00 - Hook
"You're about to raise prices. Board wants data. Traditional: 6 months, $500K. Watch."

### 1:00-2:00 - Research
Type "Notion" → Watch live research populate company, competitors, market.

### 2:00-3:00 - World Generation
Automatic: Segments, competitor agents, customer profiles appear.

### 3:00-4:00 - Simulation
Click "Simulate" → Watch 90 days unfold. Competitors respond. Customers react.

### 4:00-5:00 - Branching Futures
Show scenario tree: "In 73% of futures, you retain. In 15%, competitor undercuts..."

### 5:00-6:00 - Interview
Click an agent who churned. Ask why. Get real explanation with memory.

### 6:00-7:00 - Causal Trace
Show DAG: "Churned because → network effect → from Sarah → who churned because..."

### 7:00-8:00 - Execution Plan
"Based on 100 futures: Do X by Tuesday. If Y happens, do Z."

### 8:00-9:00 - Confidence
"73% = 90% customer × 85% market × 80% competitor. Biggest risk: competitor."

### 9:00-10:00 - Close
"This was with public data. Imagine YOUR data. There's a future where you win."

---

## Success Metrics

### Demo Success
- "I need this" response from viewer
- Specific follow-up questions about integration
- Request for enterprise pricing

### Platform Success
- Decision confidence > 70%
- Execution plan specificity (dates, owners, thresholds)
- Causal explanations that are interrogable
- Game-theoretic predictions that match real competitor behavior

---

## Build Order

### Phase 1: Research + Database
1. Set up Supabase
2. Implement research_engine.py with Exa
3. Create company research API endpoints

### Phase 2: Game Theory
1. Implement competitor_engine.py
2. Add game-theoretic response logic
3. Create competitor prediction endpoints

### Phase 3: Scenario Branching
1. Implement scenario_engine.py
2. Branch tracking in simulation
3. Probability calculations

### Phase 4: Confidence Decomposition
1. Implement confidence_engine.py
2. Component breakdown
3. Sensitivity analysis

### Phase 5: Frontend Canvas
1. D3 canvas with pan/zoom
2. Node components
3. Connection drawing

### Phase 6: Visualizations
1. Agent network (force-directed)
2. Scenario tree
3. Timeline playback
4. Causal DAG
5. Confidence chart

### Phase 7: Polish
1. Linear design system
2. Animations
3. Export (markdown, PDF)
4. Present mode

### Phase 8: Deploy
1. Railway configuration
2. Environment setup
3. Production testing
