# Populous: Decision Intelligence Platform

## Status: Building Full Platform with Game Theory

**Tagline:** "There's a future where you win. We engineer that for you."

---

## Architecture Documents

| Document | Purpose |
|----------|---------|
| `docs/ARCHITECTURE-V2.md` | Full system architecture |
| `docs/GAME-THEORY-SPEC.md` | Competitor agent game theory |
| `docs/SURGICAL-BUILD-PLAN.md` | Original backend spec |
| `docs/SURGICAL-BUILD-PLAN-PART2.md` | Engine implementations |
| `docs/SURGICAL-BUILD-PLAN-PART3.md` | API and frontend spec |

---

## What's Built (Backend V1)

### Models (`rltx-populous/backend/models/`)
- `decision.py` - Decision, Option, Constraint, SuccessCriteria
- `world.py` - World, Segment, Competitor, Product
- `generative_agent.py` - Stanford GenerativeAgent with memory
- `simulation.py` - TemporalSimulation, BranchResult
- `trace.py` - Trace, TraceNode, Counterfactual
- `action.py` - Recommendation, ActionItem, Contingency

### Engines (`rltx-populous/backend/engine/`)
- `agent_engine.py` - Stanford perceive/reflect/plan/decide
- `network_engine.py` - Social influence propagation
- `simulation_engine.py` - Monte Carlo simulation
- `trace_engine.py` - Causal analysis
- `recommendation_engine.py` - Execution plans
- `chat_engine.py` - Agent interviews
- `prediction_engine.py` - Survey predictions
- `bias_engine.py` - Question bias detection

### API (`rltx-populous/backend/api/`)
- `decision_intelligence.py` - DI routes at /api/di/*
- `main.py` - Includes DI router

### Frontend (`populous-frontend/src/`)
- `types/index.ts` - TypeScript types
- `lib/api.ts` - API client
- `hooks/use-decision-intelligence.ts` - React hooks

---

## What Needs to Be Built

### Phase 1: Research + Database

**New Backend Files:**

1. `backend/models/company.py`
```python
# Company profile from research
class Company(BaseModel):
    id: str
    name: str
    description: str
    industry: str
    employees: str
    funding: Optional[str]
    revenue: Optional[str]
    products: List[Product]
    leadership: List[Leader]
    recent_news: List[NewsItem]
    strengths: List[str]
    weaknesses: List[str]
    research_sources: List[str]
```

2. `backend/engine/research_engine.py`
```python
# Deep research using Exa API + Claude
class ResearchEngine:
    def __init__(self, exa_client, llm_client):
        self.exa = exa_client
        self.llm = llm_client

    async def research_company(self, query: str) -> Company:
        # 1. Exa search for company info
        # 2. Exa search for competitors
        # 3. Exa search for recent news
        # 4. Claude synthesis into structured Company
        pass

    async def research_market(self, company: Company) -> Market:
        # Market dynamics, growth, trends
        pass
```

3. `backend/db/supabase.py`
```python
# Supabase client and operations
from supabase import create_client

class Database:
    def __init__(self):
        self.client = create_client(url, key)

    async def save_company(self, company: Company) -> str:
        pass

    async def save_decision(self, decision: Decision) -> str:
        pass

    async def save_simulation(self, simulation: Simulation) -> str:
        pass
```

### Phase 2: Game Theory

**New Backend Files:**

1. `backend/models/competitor_agent.py`
```python
class CompetitorAgent(BaseModel):
    id: str
    company: Company
    strategy_type: str  # aggressive, defensive, opportunistic, passive
    risk_tolerance: float
    response_speed: str
    payoff_weights: Dict[str, float]

    def decide_response(self, your_move: Dict, market_state: Dict) -> Optional[Dict]:
        pass
```

2. `backend/engine/competitor_engine.py`
```python
class CompetitorEngine:
    def generate_competitor_agents(self, companies: List[Company]) -> List[CompetitorAgent]:
        pass

    def predict_responses(self, your_move: Dict, competitors: List[CompetitorAgent]) -> Dict:
        pass

    def find_nash_equilibrium(self, payoff_matrix: np.ndarray) -> Tuple:
        pass
```

3. `backend/engine/scenario_engine.py`
```python
class ScenarioEngine:
    def generate_branches(self, your_move: Dict, competitors: List[CompetitorAgent]) -> List[ScenarioBranch]:
        pass

    def calculate_branch_probabilities(self, branches: List[ScenarioBranch]) -> Dict:
        pass
```

### Phase 3: Confidence + Journal

**New Backend Files:**

1. `backend/engine/confidence_engine.py`
```python
class ConfidenceEngine:
    def decompose_confidence(self, simulation: Simulation) -> ConfidenceDecomposition:
        # Break down into: customer model, market assumptions, competitor baseline
        pass

    def calculate_sensitivity(self, component: str, simulation: Simulation) -> float:
        pass
```

2. `backend/engine/journal_engine.py`
```python
class JournalEngine:
    def create_entry(self, decision_id: str, event_type: str, data: Dict):
        pass

    def get_journal(self, decision_id: str) -> DecisionJournal:
        pass

    def export_markdown(self, journal: DecisionJournal) -> str:
        pass

    def export_pdf(self, journal: DecisionJournal) -> bytes:
        pass
```

### Phase 4: Frontend - Canvas System

**Design System:** Linear verbatim (dark mode, Inter font, specific spacing)

**New Frontend Files:**

1. `src/lib/design-system.ts` - Colors, typography, spacing tokens
2. `src/components/canvas/Canvas.tsx` - D3-based infinite canvas
3. `src/components/canvas/Node.tsx` - Base node component
4. `src/components/canvas/Connection.tsx` - Bezier curve connections
5. `src/components/canvas/nodes/DecisionNode.tsx`
6. `src/components/canvas/nodes/ResearchNode.tsx`
7. `src/components/canvas/nodes/WorldNode.tsx`
8. `src/components/canvas/nodes/AudienceNode.tsx`
9. `src/components/canvas/nodes/CompetitorNode.tsx`
10. `src/components/canvas/nodes/SimulationNode.tsx`
11. `src/components/canvas/nodes/ResultsNode.tsx`

### Phase 5: Frontend - Visualizations

1. `src/components/viz/AgentNetwork.tsx` - Force-directed D3
2. `src/components/viz/ScenarioTree.tsx` - Branching visualization
3. `src/components/viz/Timeline.tsx` - Simulation playback
4. `src/components/viz/CausalTrace.tsx` - DAG visualization
5. `src/components/viz/ConfidenceChart.tsx` - Decomposition view

### Phase 6: Frontend - Views

1. `src/app/(dashboard)/canvas/page.tsx` - Main canvas view
2. `src/app/(dashboard)/dashboard/page.tsx` - Traditional dashboard
3. `src/components/views/CEOView.tsx` - Stakeholder view
4. `src/components/views/CFOView.tsx`
5. `src/components/views/CMOView.tsx`
6. `src/components/views/OpsView.tsx`
7. `src/components/views/PresentMode.tsx` - Board presentation

### Phase 7: Chat + Export

1. `src/components/chat/AgentChat.tsx` - Full chat interface
2. `src/components/export/MarkdownExport.tsx`
3. `src/components/export/PDFExport.tsx`

---

## Environment Variables Needed

```bash
# Backend
ANTHROPIC_API_KEY=...       # Claude API
EXA_API_KEY=...             # Exa web search API
SUPABASE_URL=...            # Supabase project URL
SUPABASE_KEY=...            # Supabase anon key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## API Endpoints to Add

### Research
```
POST /api/research/company
  Input: { "query": "Notion" }
  Output: { "company": Company, "competitors": [...], "market": {...} }
```

### Competitors
```
POST /api/competitors/predict
  Input: { "your_move": {...}, "competitor_ids": [...] }
  Output: { "responses": [...], "probabilities": {...} }
```

### Scenarios
```
GET /api/decisions/{id}/branches
  Output: { "branches": [...], "tree": {...} }
```

### Confidence
```
GET /api/decisions/{id}/confidence
  Output: { "overall": 0.73, "components": [...], "sensitivity": {...} }
```

### Journal
```
GET /api/decisions/{id}/journal
  Output: { "entries": [...] }

POST /api/decisions/{id}/export
  Input: { "format": "markdown" | "pdf" }
  Output: File
```

---

## Demo Flow (10 Minutes)

1. **0:00-1:00 - Hook**
   "Raise prices. Board wants data. 6 months, $500K. Or 30 seconds."

2. **1:00-2:00 - Research**
   Type "Notion" → Live research populates company, competitors, market

3. **2:00-3:00 - World Generation**
   Automatic: Segments, competitor agents, customer profiles

4. **3:00-4:00 - Simulation**
   Click Simulate → Watch 90 days. Competitors respond. Customers react.

5. **4:00-5:00 - Scenario Branches**
   "73% retain. 15% competitor undercuts. 12% market shift."

6. **5:00-6:00 - Interview**
   Click churned agent. Ask why. Get real explanation.

7. **6:00-7:00 - Causal Trace**
   DAG: "Churned because → network effect → from Sarah..."

8. **7:00-8:00 - Execution Plan**
   "Do X by Tuesday. If Y, do Z."

9. **8:00-9:00 - Confidence**
   "73% = 90% customer × 85% market × 80% competitor"

10. **9:00-10:00 - Close**
    "Your data. Your market. There's a future where you win."

---

## Verify Backend Works

```bash
cd rltx-populous
source venv/bin/activate
PYTHONPATH=. python -c "
from backend.models.decision import Decision
from backend.models.generative_agent import GenerativeAgent
from backend.engine.agent_engine import AgentEngine
from backend.engine.simulation_engine import SimulationEngine
from backend.api.decision_intelligence import router
print('All imports OK')
"
```

---

## Quick Start

```bash
# Backend
cd rltx-populous
source venv/bin/activate
pip install exa_py supabase  # New dependencies
uvicorn backend.api.main:app --reload

# Frontend
cd populous-frontend
npm install d3 @types/d3  # New dependencies
npm run dev
```

---

## Build Priority

1. **Research Engine** - Makes the demo real
2. **Supabase Integration** - Persistence
3. **Competitor Agents** - Game theory differentiator
4. **Canvas UI** - Visual workflow
5. **Agent Network Viz** - Wow factor
6. **Scenario Branching** - Strategic depth
7. **Confidence Decomposition** - Enterprise trust
8. **Export** - Board-ready outputs
