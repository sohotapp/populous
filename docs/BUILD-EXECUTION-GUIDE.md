# RLTX POPULOUS - Build Execution Guide
## Complete Reference for End-to-End Implementation

---

# QUICK START

## Plan Documents
1. **SURGICAL-BUILD-PLAN.md** - Architecture + Data Models
2. **SURGICAL-BUILD-PLAN-PART2.md** - Backend Engines
3. **SURGICAL-BUILD-PLAN-PART3.md** - API Layer + Frontend + Build Sequence

---

# ARCHITECTURE AT A GLANCE

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js 14)                   │
│  8 Screens: Projects, Audiences, Survey Builder, Results   │
│  Components: ~25 React components with React Query          │
└─────────────────────────────────┬───────────────────────────┘
                                  │ REST API
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                       │
│  API: 15+ endpoints across 8 domains                        │
│  Engines: 7 AI-powered engines (Agent, Simulation, Trace,   │
│           Decision, Chat, Prediction, Bias)                 │
│  Models: 6 Pydantic model files                             │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                       │
│  Anthropic Claude API (claude-sonnet-4-20250514)                      │
│  Future: PostgreSQL, Redis, Neo4j                           │
└─────────────────────────────────────────────────────────────┘
```

---

# COMPLETE FILE INVENTORY

## Backend (35 files)

### Models (6 files)
```
backend/models/
├── decision.py      # Decision, Option, Constraint, SuccessCriteria
├── world.py         # World, Segment, Competitor, Product
├── agent.py         # Agent, Memory, Reflection, Belief, Relationship
├── simulation.py    # Simulation, SimulationConfig, BranchResult, DailySnapshot
├── trace.py         # Trace, TraceNode, TraceEdge, Counterfactual, Sensitivity
└── action.py        # Recommendation, ActionItem, Contingency, ApprovalGate
```

### Engines (7 files)
```
backend/engine/
├── agent_engine.py       # Stanford architecture: perceive, reflect, plan, decide
├── network_engine.py     # Social network: build, propagate, cascade
├── simulation_engine.py  # Monte Carlo: temporal, events, snapshots
├── trace_engine.py       # Causal analysis: drivers, counterfactuals
├── decision_engine.py    # Recommendations: ranking, execution plans
├── chat_engine.py        # Agent interviews: context, memory retrieval
├── prediction_engine.py  # Survey predictions: real-time response forecasts
└── bias_engine.py        # Bias detection: rule-based + LLM checks
```

### API (1 file)
```
backend/api/
└── main.py               # All routes in single FastAPI app
```

## Frontend (25+ files)

### Core Infrastructure (3 files)
```
src/lib/
├── types.ts          # All TypeScript interfaces
├── api.ts            # API client functions
└── hooks.ts          # React Query hooks
```

### Components (~20 files)
```
src/components/
├── survey/
│   ├── QuestionBuilder.tsx
│   ├── SurveyPreview.tsx
│   ├── ResponsePredictions.tsx
│   ├── BiasWarning.tsx
│   ├── ConfidenceBadge.tsx
│   └── AISuggestion.tsx
│
├── audience/
│   ├── AudienceList.tsx
│   ├── AudienceDetail.tsx
│   ├── CreateAudienceForm.tsx
│   ├── AgentCard.tsx
│   └── AgentChat.tsx
│
├── simulation/
│   ├── SimulationProgress.tsx
│   ├── TimelineChart.tsx
│   ├── OutcomeDistribution.tsx
│   └── ConfidenceInterval.tsx
│
├── trace/
│   ├── TraceViewer.tsx
│   ├── CausalChain.tsx
│   └── CounterfactualCard.tsx
│
└── decision/
    ├── RecommendationCard.tsx
    ├── ExecutionPlan.tsx
    └── RiskMatrix.tsx
```

### Pages (8 routes)
```
src/app/(dashboard)/
├── layout.tsx                    # Dashboard shell
├── page.tsx                      # Overview
├── projects/
│   ├── page.tsx                  # Projects list
│   ├── new/page.tsx              # Survey builder
│   └── [id]/results/page.tsx     # Results dashboard
├── audiences/
│   ├── page.tsx                  # Audiences list
│   ├── new/page.tsx              # Create audience
│   └── [id]/page.tsx             # Audience detail
├── decisions/
│   └── [id]/trace/page.tsx       # Trace viewer
└── templates/page.tsx            # Templates library
```

---

# BUILD PHASES

## Phase 1: Backend Foundation (Days 1-2)
**Goal:** Working API skeleton with data models

| Task | File | Dependencies |
|------|------|--------------|
| Create Decision model | backend/models/decision.py | None |
| Create World model | backend/models/world.py | None |
| Create Agent model | backend/models/agent.py | None |
| Create Simulation model | backend/models/simulation.py | None |
| Create Trace model | backend/models/trace.py | None |
| Create Action model | backend/models/action.py | None |
| Create API skeleton | backend/api/main.py | All models |

**Verification:** `curl http://localhost:8000/health` returns 200

## Phase 2: Core Engines (Days 3-5)
**Goal:** Stanford agents + Monte Carlo simulation working

| Task | File | Dependencies |
|------|------|--------------|
| Build Agent Engine | backend/engine/agent_engine.py | Agent model |
| Build Network Engine | backend/engine/network_engine.py | Agent model |
| Build Simulation Engine | backend/engine/simulation_engine.py | Agent + Network engines |
| Add simulation routes | backend/api/main.py | Simulation engine |

**Verification:** Run a 10-branch simulation via API

## Phase 3: Intelligence Engines (Days 6-8)
**Goal:** Causal traces + recommendations working

| Task | File | Dependencies |
|------|------|--------------|
| Build Trace Engine | backend/engine/trace_engine.py | Simulation results |
| Build Decision Engine | backend/engine/decision_engine.py | Trace engine |
| Build Chat Engine | backend/engine/chat_engine.py | Agent model |
| Build Prediction Engine | backend/engine/prediction_engine.py | Agent model |
| Build Bias Engine | backend/engine/bias_engine.py | None |
| Complete all API routes | backend/api/main.py | All engines |

**Verification:** All API endpoints return valid data

## Phase 4: Frontend Foundation (Days 9-10)
**Goal:** Types + API client + basic layout

| Task | File | Dependencies |
|------|------|--------------|
| Define TypeScript types | src/lib/types.ts | None |
| Build API client | src/lib/api.ts | Types |
| Build React Query hooks | src/lib/hooks.ts | API client |
| Build dashboard layout | src/app/(dashboard)/layout.tsx | None |
| Create page shells | All page.tsx files | Layout |

**Verification:** Pages render, API calls work

## Phase 5: Survey Builder (Days 11-13)
**Goal:** Core feature complete and polished

| Task | File | Dependencies |
|------|------|--------------|
| Build QuestionBuilder | src/components/survey/QuestionBuilder.tsx | Types |
| Build BiasWarning | src/components/survey/BiasWarning.tsx | Bias API |
| Build ResponsePredictions | src/components/survey/ResponsePredictions.tsx | Prediction API |
| Build ConfidenceBadge | src/components/survey/ConfidenceBadge.tsx | None |
| Build AISuggestion | src/components/survey/AISuggestion.tsx | Suggestions API |
| Build SurveyPreview | src/components/survey/SurveyPreview.tsx | All above |
| Build Survey page | src/app/(dashboard)/projects/new/page.tsx | All components |

**Verification:** Full survey creation flow works

## Phase 6: Audiences (Days 14-16)
**Goal:** Audience generation + agent interviews

| Task | File | Dependencies |
|------|------|--------------|
| Build AudienceList | src/components/audience/AudienceList.tsx | Audiences API |
| Build CreateAudienceForm | src/components/audience/CreateAudienceForm.tsx | Worlds API |
| Build AgentCard | src/components/audience/AgentCard.tsx | Agent types |
| Build AudienceDetail | src/components/audience/AudienceDetail.tsx | All above |
| Build AgentChat | src/components/audience/AgentChat.tsx | Chat API |
| Build Audiences pages | All audience page.tsx | All components |

**Verification:** Generate audience, chat with agent

## Phase 7: Simulation & Results (Days 17-19)
**Goal:** Run simulations, see results

| Task | File | Dependencies |
|------|------|--------------|
| Build SimulationProgress | src/components/simulation/SimulationProgress.tsx | Simulation API |
| Build TimelineChart | src/components/simulation/TimelineChart.tsx | Recharts |
| Build OutcomeDistribution | src/components/simulation/OutcomeDistribution.tsx | Results data |
| Build ConfidenceInterval | src/components/simulation/ConfidenceInterval.tsx | Stats data |
| Build Results page | src/app/(dashboard)/projects/[id]/results/page.tsx | All above |

**Verification:** Run simulation, see timeline + results

## Phase 8: Trace & Decisions (Days 20-22)
**Goal:** Causal analysis + action plans

| Task | File | Dependencies |
|------|------|--------------|
| Build TraceViewer | src/components/trace/TraceViewer.tsx | D3/React Flow |
| Build CausalChain | src/components/trace/CausalChain.tsx | Trace data |
| Build CounterfactualCard | src/components/trace/CounterfactualCard.tsx | Counterfactual data |
| Build RecommendationCard | src/components/decision/RecommendationCard.tsx | Recommendation API |
| Build ExecutionPlan | src/components/decision/ExecutionPlan.tsx | Action items |
| Build trace + decision pages | All decision page.tsx | All above |

**Verification:** View trace, see recommendation

## Phase 9: Polish (Days 23-25)
**Goal:** Production ready

| Task | File | Dependencies |
|------|------|--------------|
| Build Templates page | src/app/(dashboard)/templates/page.tsx | Templates API |
| Build Projects page | src/app/(dashboard)/projects/page.tsx | Decisions API |
| Add loading states | All components | None |
| Add error handling | All components | None |
| Style to Figma | All components | Figma screenshots |
| Deploy to Railway | railway.toml | All above |

**Verification:** Full demo flow works end-to-end

---

# KEY INTEGRATION PATTERNS

## 1. Real-time Bias Check (Survey Builder)
```typescript
// Debounce 300ms, then check bias
const debouncedBiasCheck = useDebouncedCallback(
  async (question: string) => {
    const result = await checkBias(question);
    setBiasResult(result);
  },
  300
);

// In QuestionBuilder
onChange={(text) => {
  setQuestion(text);
  debouncedBiasCheck(text);
}}
```

## 2. Polling Simulation Progress
```typescript
// useSimulation hook polls every 1s while running
const { data: simulation } = useSimulation(simId);

// In component
{simulation?.status === 'running' && (
  <SimulationProgress progress={simulation.progress} />
)}

{simulation?.status === 'completed' && (
  <ResultsDashboard results={simulation.aggregate_results} />
)}
```

## 3. Agent Chat with Memory
```typescript
// Maintain conversation history
const [history, setHistory] = useState<Message[]>([]);

const sendMessage = async (text: string) => {
  const response = await chatWithAgent(audienceId, agentId, text, history);
  setHistory([
    ...history,
    { role: 'user', content: text },
    { role: 'assistant', content: response.response }
  ]);
};
```

## 4. Background Audience Generation
```typescript
// Create audience triggers background generation
const { mutate: createAudience } = useCreateAudience();

createAudience(data, {
  onSuccess: (result) => {
    // Show progress modal
    setGenerating(true);
    setAudienceId(result.id);
  }
});

// Poll until ready
const { data: audience } = useAudience(audienceId);
useEffect(() => {
  if (audience?.status === 'ready') {
    setGenerating(false);
  }
}, [audience?.status]);
```

---

# DEMO FLOW

The complete demo that sells:

1. **Start** - User sees Projects dashboard
2. **Create Project** - User clicks "New Project"
3. **Survey Builder** - User types survey questions
   - AI suggests improvements (BiasWarning)
   - Real-time predictions appear (ResponsePredictions)
   - Confidence badges show certainty
4. **Select Audience** - User picks or creates audience
5. **Run Simulation** - User clicks "Run Simulation"
   - Progress bar shows completion
   - Timeline chart builds in real-time
6. **View Results** - User sees outcome distribution
   - Retention rates with confidence intervals
   - Segment-by-segment breakdown
7. **Explore Trace** - User clicks "Why did this happen?"
   - Causal chain visualization
   - Counterfactual analysis
8. **Talk to Customers** - User clicks an agent
   - Natural conversation
   - Agent explains their journey
9. **Get Recommendation** - User clicks "Generate Plan"
   - Clear recommendation with confidence
   - Execution plan with dates
   - Contingencies for risks
10. **Export** - User downloads board-ready report

---

# SUCCESS CRITERIA

## Performance
- Survey predictions: < 500ms response
- Bias check: < 300ms response
- Simulation (100 branches): < 30s total
- Agent chat: < 2s response

## Quality
- All 8 screens match Figma designs
- No TypeScript errors
- All API endpoints tested
- Loading states for all async operations
- Error states for all failure modes

## Demo Ready
- 3 pre-built audience templates
- 3 pre-built scenario templates
- SparkZero pricing study demo scenario
- Full end-to-end flow works without errors

---

# READY TO BUILD

This plan is complete. Every file is specified. Every integration is documented. Every phase is sequenced.

**Start with:** `backend/models/decision.py`

**End with:** A production-grade Decision Intelligence platform.
