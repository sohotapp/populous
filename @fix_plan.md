# RLTX POPULOUS - Build Task List

## Phase 1: Core Backend (P0)

### Survey Prediction Engine
- [ ] Create `backend/engine/survey_predictor.py`
- [ ] Implement `predict_responses(audience, questions)` function
- [ ] Add caching for repeated predictions
- [ ] Create `/api/predictions/survey` endpoint
- [ ] Test prediction latency (<500ms)

### Bias Detection
- [ ] Create `backend/engine/bias_detector.py`
- [ ] Implement leading phrase detection
- [ ] Add suggested rephrasing logic
- [ ] Create `/api/bias/check` endpoint
- [ ] Test with various biased questions

### AI Suggestions
- [ ] Create `backend/engine/suggestion_engine.py`
- [ ] Implement context-aware suggestions
- [ ] Create `/api/suggestions/question` endpoint
- [ ] Test suggestion relevance

### Stanford Agent Architecture
- [ ] Create `backend/engine/generative_agent.py`
- [ ] Implement Memory dataclass
- [ ] Implement Reflection dataclass
- [ ] Implement GenerativeDecisionAgent class
- [ ] Add perceive(), _reflect(), retrieve_relevant_context()
- [ ] Add plan(), decide(), update_beliefs()
- [ ] Integrate with existing simulation

## Phase 2: Survey Builder Frontend (P0)

### Components
- [ ] Create `QuestionBuilder.tsx` component
- [ ] Create `SurveyPreview.tsx` component
- [ ] Create `ResponsePredictions.tsx` component
- [ ] Create `AISuggestion.tsx` component
- [ ] Create `BiasWarning.tsx` component
- [ ] Create `ConfidenceBadge.tsx` component

### Integration
- [ ] Create API client (`src/lib/api.ts`)
- [ ] Connect QuestionBuilder to prediction API
- [ ] Implement real-time prediction updates
- [ ] Add debouncing for API calls
- [ ] Style to match Figma exactly

### Survey Builder Page
- [ ] Create `/projects/new/page.tsx`
- [ ] Implement 3-panel layout
- [ ] Add audience selector
- [ ] Add sample size selector
- [ ] Add "Run Survey" functionality

## Phase 3: Decision Layer (P0)

### Backend
- [ ] Create `backend/engine/decision_layer.py`
- [ ] Implement `compute_optimal_decision()`
- [ ] Implement `generate_execution_plan()`
- [ ] Implement `identify_contingencies()`
- [ ] Create `/api/decisions/generate` endpoint

### Frontend
- [ ] Create `DecisionOutput.tsx` component
- [ ] Display execution plan with dates
- [ ] Display contingencies
- [ ] Display approval gates
- [ ] Display confidence score

## Phase 4: Audience Features (P0)

### Generation
- [ ] Complete CreateAudienceForm
- [ ] Add generation progress modal
- [ ] Generate 100+ profiles via Claude API
- [ ] Display generated profiles

### Agent Chat
- [ ] Create `AgentChat.tsx` modal component
- [ ] Implement chat interface
- [ ] Connect to agent chat API
- [ ] Test coherent responses

## Phase 5: Remaining Pages (P1)

### Projects Dashboard
- [ ] Complete `/projects/page.tsx`
- [ ] Implement ProjectCard component
- [ ] Add status badges
- [ ] Add filtering/sorting

### Audiences Page
- [ ] Complete `/audiences/page.tsx`
- [ ] Implement master-detail layout
- [ ] Add AudienceList sidebar
- [ ] Add AudienceDetail main content

### Templates Library
- [ ] Complete `/templates/page.tsx`
- [ ] Implement 3 tabs (Audiences, Projects, Scenarios)
- [ ] Add template cards
- [ ] Add "Use Template" functionality

### Results Dashboard
- [ ] Create `/projects/[id]/results/page.tsx`
- [ ] Add response distribution charts
- [ ] Add confidence intervals
- [ ] Add segment breakdown
- [ ] Add export functionality

## Phase 6: Demo Scenarios (P1)

### Scenarios
- [ ] Create SparkZero Pricing Study
- [ ] Create EcoSpark Launch Test
- [ ] Create Enterprise Expansion Study
- [ ] Pre-generate audiences for each

### Demo Content
- [ ] Add realistic questions
- [ ] Configure expected results
- [ ] Test full demo flow

## Phase 7: Polish & Deploy (P2)

### Testing
- [ ] End-to-end demo flow testing
- [ ] Performance testing
- [ ] Error handling
- [ ] Loading states

### Production
- [ ] Secure environment variables
- [ ] Railway deployment
- [ ] Health checks
- [ ] Final verification

---

## Current Status
- Phase: Not Started
- Blocking Issues: None
- Next Task: Create `backend/engine/survey_predictor.py`
