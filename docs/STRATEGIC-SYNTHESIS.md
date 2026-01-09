# RLTX POPULOUS: Strategic Synthesis & Implementation Blueprint
## Decision Advantage for the World's Best Leaders

---

# PART 1: CLARIFICATION ON RALPH

## What Ralph Actually Is

**Ralph is NOT a library to integrate into your codebase.**

Ralph is a **standalone CLI tool** that creates continuous autonomous development loops. It:
- Runs Claude Code repeatedly until objectives are complete
- Tracks progress through task lists
- Detects completion signals automatically
- Handles rate limits and errors gracefully
- Monitors for stuck loops and circuit-breaks

## How to Use Ralph for This Project

```bash
# 1. Install Ralph globally (one-time)
git clone https://github.com/frankbria/ralph-claude-code.git
cd ralph-claude-code
./install.sh

# 2. Set up the RLTX project for Ralph
cd "/Users/owenshar/Desktop/RLTX/Demos/Populous demo"
ralph-import  # or ralph-setup for fresh projects

# 3. Create PROMPT.md with build specification
# (we'll create this below)

# 4. Run Ralph with monitoring
ralph --monitor
```

Ralph will then continuously run Claude Code, building the application until it matches the Figma designs and all tests pass.

---

# PART 2: THE FIGMA UI/UX SPECIFICATION

## Complete Screen Inventory (from your 12 screenshots)

### Screen 1-2: Projects Dashboard
```
┌─────────────────────────────────────────────────────────────────────────┐
│  🔍 Search anything...                    🔔  ⚙️  👤  [+ New Project]    │
├──────────┬──────────────────────────────────────────────┬───────────────┤
│          │                                              │               │
│ Projects │  All Projects                [+ New Project] │ Team          │
│ Audiences│  ────────────────────────────────────────────│ Activities    │
│ Templates│  All Projects 32 | Drafts | Running | Archived              │
│ Insights │  🔍 Search...                    ≡ Sort By   │ • John Carter │
│ Integr.. │                                              │   2h ago      │
│ Help     │  ┌─────────────┐  ┌─────────────┐            │ • Sarah Malik │
│          │  │ SparkZero   │  │ SparkZero   │            │   2h ago      │
│          │  │ Pricing     │  │ Pricing     │            │               │
│          │  │ Study       │  │ Study       │            │ Alerts        │
│          │  │ ACTIVE      │  │ DRAFT       │            │ ────────────  │
│          │  │             │  │             │            │ ⬇ Purchase    │
│          │  │ Sample: 3000│  │ Sample: 3000│            │   intent -9%  │
│          │  │ Intent: 62% │  │ Intent: 62% │            │               │
│          │  │ Updated 2h  │  │ Updated 2h  │            │ ⬆ Price sens. │
│          │  └─────────────┘  └─────────────┘            │   exceeded    │
│          │                                              │               │
│          │  ┌─────────────┐  ┌─────────────┐            │ ⚠ Variance    │
│          │  │ EcoSpark    │  │ EcoSpark    │            │   detected    │
│          │  │ Launch Test │  │ Launch Test │            │               │
│          │  │ PAUSED      │  │ ACTIVE      │            │               │
│          │  └─────────────┘  └─────────────┘            │               │
└──────────┴──────────────────────────────────────────────┴───────────────┘
```

**Components needed:**
- Sidebar navigation with icons
- Project cards (2-column grid)
- Status badges (ACTIVE/green, DRAFT/gray, PAUSED/orange, RUNNING/blue, ARCHIVED/gray)
- Team Activities feed
- Smart Alerts panel
- Search, sort, filter

### Screen 3: Audiences Page (Master-Detail)
```
┌─────────────────────────────────────────────────────────────────────────┐
│  Audiences                              [+ New Audience]                │
├──────────┬──────────────────────────────────────────────────────────────┤
│ Sidebar  │  Urban Gen Z Shoppers (US)                                   │
│ ──────── │  👥 456 people • 📁 5 Projects • Created by Jhon Carter      │
│ Urban    │                                                              │
│ Gen Z    │  DESCRIPTION                                                 │
│ Shoppers │  Young urban adults aged 18-29 in the United States who     │
│ 456 ppl  │  frequently try new consumer brands, value sustainability,  │
│ 5 proj   │  and demonstrate medium-high sensitivity to price increases │
│          │                                                              │
│ Millen.  │  ┌────────┬────────┬────────────┬──────────┐                 │
│ Pet Own  │  │ AGE    │LOCATION│EST. POP    │CITY SIZE │                 │
│ 956 ppl  │  │18-24   │Urban   │~12.4M      │Large     │                 │
│          │  │(55%)   │USA     │people      │          │                 │
│ Tech     │  └────────┴────────┴────────────┴──────────┘                 │
│ Enthus.  │                                                              │
│ 223 ppl  │  Audience Profiles                    🔍 Search   ≡ Sort By  │
│          │  ┌─────────────────────────────────────────────────────────┐ │
│ Budget   │  │ NAME    │AGE│EDUCATION  │OCCUPATION      │INCOME│ACTION│ │
│ Millen.  │  │ Maya R. │24 │Bachelor's │Marketing Asst. │$58K  │View ▸│ │
│ 2k ppl   │  │ Ethan T.│19 │Undergrad  │College Student │$28K  │View ▸│ │
│          │  │ Olivia H│25 │Bachelor's │Social Media Mgr│$88K  │View ▸│ │
└──────────┴──┴─────────┴───┴───────────┴────────────────┴──────┴──────┴─┘
```

**Components needed:**
- Master-detail layout
- Audience list sidebar
- Audience detail header with actions (Import, Duplicate, Edit)
- Demographics cards
- Profiles data table with pagination

### Screen 4-6: Create Audience Flow
```
┌─────────────────────────────────────────────────────────────────────────┐
│  Create Audience                                    [Create Audience] X │
├─────────────────────────────────┬───────────────────────────────────────┤
│                                 │                                       │
│  Audience Title                 │                                       │
│  ┌───────────────────────────┐  │      Create your first audience       │
│  │ e.g. Millennial Pet Owners│  │         by answering few              │
│  └───────────────────────────┘  │            questions.                 │
│                                 │                                       │
│  Describe your audience         │          👥                           │
│  ┌───────────────────────────┐  │                                       │
│  │ BCT attack to seize OBJ   │  │  ─────────────────────────────────    │
│  │ IRON, enemy reinforced... │  │  (After generation, profiles appear)  │
│  └───────────────────────────┘  │                                       │
│                                 │                                       │
│  What are you creating for?     │                                       │
│  [Pricing✓] [Product] [Concept] │                                       │
│  [Position] [Market] [General]  │                                       │
│                                 │                                       │
│  How old are the people?        │                                       │
│  [18 Years] ─────────── [32 Yrs]│                                       │
│                                 │                                       │
│  Gender Ratio?                  │                                       │
│  Male(30%) ════════════ Fem(70%)│                                       │
│                                 │                                       │
│  Income level?                  │                                       │
│  [Low] [Middle✓] [Upper] [High] │                                       │
│                                 │                                       │
│  What matters most in decisions?│                                       │
│  [Select Option            ▼]   │                                       │
│                                 │                                       │
│  How precise?                   │                                       │
│  [Select Option            ▼]   │                                       │
│                                 │                                       │
│  Upload CSV of real attributes  │                                       │
│  ┌───────────────────────────┐  │                                       │
│  │  📤 Drag and drop or      │  │                                       │
│  │     Choose File           │  │                                       │
│  └───────────────────────────┘  │                                       │
│                                 │                                       │
│  [████████ Generate Audience ████████]                                  │
└─────────────────────────────────┴───────────────────────────────────────┘
```

**States:**
1. Empty state (form only)
2. Generating state (modal with progress bar)
3. Created state (profiles appear on right)

### Screen 7-9: Templates Library
```
┌─────────────────────────────────────────────────────────────────────────┐
│  Templates                                                              │
│  Speed up your workflows with pre-made Audience, Projects and Scenarios │
├─────────────────────────────────────────────────────────────────────────┤
│  [Audience 94] [Projects 143] [Scenarios 432]                           │
│  🔍 Search...                                        ≡ Sort By          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Audience Tab:                                                          │
│  ┌─────────────────────┐  ┌─────────────────────┐                       │
│  │ Urban Gen Z (US)    │  │ Millennial Parents  │                       │
│  │ Young, urban 18-29  │  │ Parents aged 28-40  │                       │
│  │ who try new brands  │  │ with young children │                       │
│  │                     │  │                     │                       │
│  │ COMMON USES:        │  │ COMMON USES:        │                       │
│  │ • Concept testing   │  │ • Product testing   │                       │
│  │ • Pricing explor.   │  │ • Brand research    │                       │
│  │                     │  │                     │                       │
│  │ [  Use Audience  ]  │  │ [  Use Audience  ]  │                       │
│  └─────────────────────┘  └─────────────────────┘                       │
│                                                                         │
│  Projects Tab:                                                          │
│  ┌─────────────────────┐  ┌─────────────────────┐                       │
│  │ Pricing Sensitivity │  │ Brand Perception    │                       │
│  │ Study               │  │ Study               │                       │
│  │                     │  │                     │                       │
│  │ INCLUDES:           │  │ INCLUDES:           │                       │
│  │ • Price scenarios   │  │ • Brand questions   │                       │
│  │ • Purchase intent   │  │ • Competitor comp.  │                       │
│  │ • Benchmark comp.   │  │ • NPS metric        │                       │
│  │                     │  │                     │                       │
│  │ [   Use Project   ] │  │ [   Use Project   ] │                       │
│  └─────────────────────┘  └─────────────────────┘                       │
│                                                                         │
│  Scenarios Tab:                                                         │
│  ┌─────────────────────┐  ┌─────────────────────┐                       │
│  │ Price Increase      │  │ Competitor Entry    │                       │
│  │ Stress Test         │  │ Simulation          │                       │
│  │                     │  │                     │                       │
│  │ WHAT THIS CHANGES:  │  │ WHAT THIS CHANGES:  │                       │
│  │ • Price (+5-20%)    │  │ • Market share      │                       │
│  │ • Perceived value   │  │ • Price pressure    │                       │
│  │                     │  │                     │                       │
│  │ BEST FOR:           │  │ BEST FOR:           │                       │
│  │ [Pricing] [Revenue] │  │ [Strategy] [Risk]   │                       │
│  │                     │  │                     │                       │
│  │ [  Use Scenario   ] │  │ [  Use Scenario   ] │                       │
│  └─────────────────────┘  └─────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────┘
```

### Screen 10-12: Survey Builder (THE CORE FEATURE)
```
┌─────────────────────────────────────────────────────────────────────────┐
│  New Project                                                            │
├─────────────────────┬──────────────────────┬────────────────────────────┤
│  Question Builder   │  Survey Preview      │  Response Predictions      │
│  Build your survey  │  Live respondent view│  AI-powered insights       │
│  [+ Add Question]   │                      │                            │
├─────────────────────┼──────────────────────┼────────────────────────────┤
│                     │                      │                            │
│ ┌─────────────────┐ │  Question 1 of 2     │  Overall Confidence [Med]  │
│ │ 💡 AI Suggestion│ │  ════════════════ 100%                            │
│ │ Based on your   │ │                      │  Predictions will improve  │
│ │ goal, consider  │ │  What is your primary│  as you add more context   │
│ │ asking about    │ │  reason for using    │                            │
│ │ price sensitiv..│ │  our product?        │  ────────────────────────  │
│ │                 │ │                      │  Q1: Primary Reasons [Med] │
│ │ [Add Suggested] │ │  ● Better Features   │                            │
│ │ Dismiss         │ │  ○ Lower price       │  Better Features ████ 35%  │
│ └─────────────────┘ │  ○ Ease of use       │  Lower price     ███  28%  │
│                     │  ○ Customer support  │  Ease of use     ██   25%  │
│ ⋮⋮ Question 01      │                      │  Customer supp.  █    12%  │
│   [Single choice]   │                      │                            │
│   What is your      │                      │  ────────────────────────  │
│   primary reason... │       [← Back] [Next →]  Q2: Pricing Sat. [Med]   │
│                     │                      │                            │
│ ⋮⋮ Question 02      │                      │  Mean Score: 3.2/5.0       │
│   [Rating Scale]    │                      │  Distribution: Slightly    │
│   How satisfied...  │                      │  negative skew expected    │
│                     │                      │                            │
│ ┌─────────────────┐ │                      │                            │
│ │ ⚠️ Potential Bias│ │                      │                            │
│ │ This question   │ │                      │                            │
│ │ may be leading. │ │                      │                            │
│ │ Consider...     │ │                      │                            │
│ │                 │ │                      │                            │
│ │ [Apply Suggest.]│ │                      │                            │
│ └─────────────────┘ │                      │                            │
├─────────────────────┴──────────────────────┴────────────────────────────┤
│  Audience: [General Consumer (18-65) ▼]  Sample: [500 ▼]               │
│  Estimated runtime: ~30 Seconds                    [🚀 Run Survey]      │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Features:**
1. **Three-panel layout**: Question Builder | Survey Preview | Response Predictions
2. **Drag-and-drop questions** with type badges (Single choice, Rating Scale, etc.)
3. **Live preview** showing exactly what respondents see
4. **Real-time AI predictions** showing expected response distributions
5. **AI Suggestions** for better questions (blue card)
6. **Bias Detection** warnings (orange card)
7. **Confidence scoring** (Low/Medium/High badges)
8. **Audience selector** and sample size at bottom
9. **Estimated runtime** indicator
10. **Run Survey button**

---

# PART 3: THE VALUE PROPOSITION (DEEP ANALYSIS)

## What "Decision Advantage" Means for Fortune 500 Leaders

### The Problem They Face

**CEOs, CMOs, and Strategy VPs at Fortune 500 companies:**

| Pain Point | Traditional Solution | Time | Cost |
|------------|---------------------|------|------|
| "Will this price increase kill us?" | Commission market research | 3-6 months | $300K-$1M |
| "Which positioning resonates?" | Focus groups + surveys | 2-3 months | $150K-$400K |
| "How will competitors respond?" | Strategy consultants | 4-8 weeks | $500K-$2M |
| "What's the optimal launch strategy?" | Internal analysis + gut | Weeks | Opportunity cost |

**The meta-problem**: By the time you have the data, the market has moved.

### What RLTX Delivers

```
┌─────────────────────────────────────────────────────────────────┐
│                    DECISION ADVANTAGE                           │
│                                                                 │
│  "Before you commit, we've already run it."                     │
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │  SIMULATE   │ ──▶ │   DECIDE    │ ──▶ │   EXECUTE   │       │
│  │             │     │             │     │             │       │
│  │ 5,000       │     │ AI-optimal  │     │ Execution   │       │
│  │ synthetic   │     │ decision    │     │ plan with   │       │
│  │ customers   │     │ with 73%    │     │ dates and   │       │
│  │ in 30 sec   │     │ confidence  │     │ contingenc. │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│                                                                 │
│  Result: You test 10 strategies before competitors test 1.      │
└─────────────────────────────────────────────────────────────────┘
```

### The Killer Differentiator

**Aaru (and all competitors) stop here:**
> "Strategy A has 67% probability of success"

**RLTX goes further:**
> "Execute Strategy A. Allocate $2.3M to Channel X by March 15. If Competitor B drops price >15% within 30 days, trigger Playbook 7. Approval gate at $500K spend."

### What the Demo Must Prove

For enterprise buyers to write a $100K+ check, the demo must demonstrate:

| Capability | How We Show It | Emotional Impact |
|------------|----------------|------------------|
| **Speed** | "I just simulated 5,000 customers in 30 seconds" | "This would take my team 6 months" |
| **Accuracy** | "90%+ correlation with real surveys" | "I can trust this" |
| **Actionability** | "Here's exactly what to do, by when" | "I can act on this NOW" |
| **Explainability** | "Here's why this is optimal" | "My board will accept this" |
| **Depth** | "Interview any synthetic customer" | "This is real intelligence, not a black box" |

### The Emotional Journey of the Demo

```
1. SKEPTICISM
   "Another AI tool? Sure..."

2. CURIOSITY
   "Wait, it's predicting responses in real-time as I type questions?"

3. SURPRISE
   "It detected bias in my question and suggested a fix?"

4. ENGAGEMENT
   "Let me try a different pricing scenario..."

5. REALIZATION
   "This would have taken my research team 3 months and $500K"

6. DESIRE
   "How do I get this for my team?"
```

---

# PART 4: BACK-PROPAGATING FROM VALUE TO FEATURES

## What Features Drive What Value

```
VALUE                          FEATURE                        BACKEND REQUIREMENT
─────────────────────────────────────────────────────────────────────────────────
Speed                    ──▶  Real-time predictions    ──▶  Pre-computed agent responses
                                                             + fast LLM inference

Accuracy                 ──▶  90%+ survey correlation  ──▶  Stanford agent architecture
                                                             (Memory + Reflection + Planning)

Actionability            ──▶  Execution plans          ──▶  Decision Layer with
                                                             contingency generation

Explainability           ──▶  "Why" explanations       ──▶  Audit trail + LLM reasoning
                                                             chain capture

Depth                    ──▶  Interview synthetic      ──▶  Agent chat with memory
                              customers                      retrieval

Credibility              ──▶  Bias detection           ──▶  Question analysis LLM
                              + AI suggestions              + suggestion engine

Enterprise Trust         ──▶  Team activities          ──▶  User management +
                              + audit trail                  event logging
```

## Feature Priority Matrix

| Feature | User Value | Demo Impact | Build Effort | Priority |
|---------|-----------|-------------|--------------|----------|
| Survey Builder with real-time predictions | Critical | High | High | P0 |
| AI suggestions for questions | High | Very High | Medium | P0 |
| Bias detection warnings | High | Very High | Medium | P0 |
| Audience generation | High | High | Done (partial) | P0 |
| Projects dashboard | Medium | Medium | Medium | P1 |
| Templates library | Medium | High | Low | P1 |
| Team activities feed | Low | Medium | Medium | P2 |
| Smart alerts | Medium | High | High | P2 |
| Agent interview (chat) | High | Very High | Done (partial) | P1 |

---

# PART 5: THE EXACT IMPLEMENTATION PLAN

## Phase 0: Setup Ralph (30 minutes)

```bash
# Install Ralph globally
git clone https://github.com/frankbria/ralph-claude-code.git ~/ralph-claude-code
cd ~/ralph-claude-code
./install.sh

# Navigate to project
cd "/Users/owenshar/Desktop/RLTX/Demos/Populous demo"

# Create Ralph project structure
ralph-import
```

## Phase 1: Backend Foundation (Week 1)

### 1.1 Stanford Agent Architecture
```
Files to create/modify:
- backend/engine/generative_agent.py (NEW)
  - Memory dataclass
  - Reflection dataclass
  - GenerativeDecisionAgent class with:
    - perceive()
    - _rate_importance()
    - _reflect()
    - retrieve_relevant_context()
    - plan()
    - decide()
    - update_beliefs()

- backend/models/memory.py (NEW)
  - Memory, Reflection, Plan Pydantic models
```

### 1.2 Survey Prediction Engine
```
Files to create/modify:
- backend/engine/survey_predictor.py (NEW)
  - predict_responses(audience, question) → distribution
  - suggest_improvements(question) → List[Suggestion]
  - detect_bias(question) → Optional[BiasWarning]
  - estimate_confidence(survey, audience) → float

- backend/api/surveys.py (MODIFY)
  - POST /surveys/predict-live (real-time predictions)
  - POST /surveys/suggest
  - POST /surveys/bias-check
```

### 1.3 Decision Layer
```
Files to create/modify:
- backend/engine/decision_layer.py (NEW)
  - compute_optimal_decision()
  - generate_execution_plan()
  - identify_contingencies()
  - generate_explanation()

- backend/api/decisions.py (NEW)
  - POST /decisions/compute
  - GET /decisions/{id}
  - GET /decisions/{id}/explanation
```

## Phase 2: Frontend Implementation (Week 2)

### 2.1 Connect to Backend
```
Files to create/modify:
- populous-frontend/src/lib/api.ts (NEW)
  - API client with all endpoints
  - React Query hooks

- populous-frontend/src/lib/types.ts (MODIFY)
  - Add all backend response types
```

### 2.2 Build Exact Figma UI
```
Pages to implement:
1. /projects (Dashboard)
   - ProjectCard with status badges
   - TeamActivities sidebar
   - SmartAlerts panel

2. /audiences (Master-Detail)
   - AudienceList sidebar
   - AudienceDetail main
   - ProfilesTable

3. /audiences/create (Form)
   - CreateAudienceForm
   - GeneratingModal
   - ProfilesPreview

4. /templates (Library)
   - TemplatesTabs (Audience/Projects/Scenarios)
   - TemplateCard variants

5. /projects/new (Survey Builder) - THE CORE
   - QuestionBuilder panel
   - SurveyPreview panel
   - ResponsePredictions panel
   - AISuggestion component
   - BiasWarning component
   - ConfidenceBadge component
```

### 2.3 Real-time Predictions
```
Implementation:
- Debounced API calls as user types
- Streaming updates for predictions
- Confidence score animation
- Response distribution charts (Recharts)
```

## Phase 3: Polish & Demo (Week 3)

### 3.1 Demo Scenarios
```
Create pre-built scenarios:
1. "SparkZero Pricing Study" - Consumer beverage pricing
2. "EcoSpark Launch Test" - Sustainable product concept
3. "Enterprise SaaS Expansion" - B2B market entry
```

### 3.2 Demo Script
```
Write word-for-word demo flow:
1. Show empty dashboard
2. Click "Use Template" for Pricing Study
3. Watch AI generate audience
4. Build survey with real-time predictions
5. See AI suggestion appear
6. See bias warning on leading question
7. Run simulation
8. Show results with confidence intervals
9. Interview a synthetic customer
10. Show execution plan
```

### 3.3 Production Deployment
```
- Railway configuration
- Environment variables secured
- Health checks
- Error monitoring
```

---

# PART 6: THE RALPH PROMPT.md

Create this file at the project root:

```markdown
# RLTX POPULOUS BUILD SPECIFICATION

## MISSION
Build a production-grade Decision Intelligence platform that matches the Figma
designs exactly, implementing the full Stanford generative agents architecture
and real-time survey prediction engine.

## SUCCESS CRITERIA
1. All Figma screens implemented pixel-perfect
2. Real-time response predictions working
3. AI suggestions appearing as user types
4. Bias detection functional
5. All API endpoints working
6. Frontend connected to backend
7. Demo scenarios loadable
8. Agent interview (chat) working

## ARCHITECTURE

### Backend (Python/FastAPI)
- Stanford generative agents (memory + reflection + planning)
- Survey prediction engine with LLM
- Decision layer with execution plans
- All existing simulation engine preserved

### Frontend (Next.js/TypeScript)
- Exact Figma UI implementation
- Real-time API integration
- Responsive design

## BUILD ORDER

### Phase 1: Backend
1. Implement GenerativeDecisionAgent class
2. Implement SurveyPredictor class
3. Implement DecisionLayer class
4. Add new API endpoints
5. Write tests

### Phase 2: Frontend
1. Create API client
2. Build Projects Dashboard
3. Build Audiences pages
4. Build Templates Library
5. Build Survey Builder (core feature)
6. Connect all to backend

### Phase 3: Polish
1. Create demo scenarios
2. Test end-to-end
3. Fix bugs
4. Deploy

## FIGMA REFERENCE
Images located at: /rltx figma images/
- Screenshot 1-2: Projects Dashboard
- Screenshot 3: Audiences page
- Screenshot 4-6: Create Audience flow
- Screenshot 7-9: Templates library
- Screenshot 10-12: Survey Builder

## KEY TECHNICAL REQUIREMENTS

### Real-time Predictions
As user types survey questions, immediately show:
- Predicted response distribution
- Confidence score
- AI suggestions for improvement
- Bias warnings if detected

### Stanford Agent Architecture
Each synthetic agent must have:
- Memory stream (all perceptions stored)
- Reflection (insights from accumulated memories)
- Planning (action sequences)
- Utility function (what they optimize for)
- Belief state (updatable via Bayesian inference)

### UI Components
Must match Figma exactly:
- Color scheme (blue primary, gray neutrals)
- Typography (Inter or system font)
- Spacing (8px grid)
- Border radius (8px cards)
- Shadows (subtle, elevation-based)

## TESTING REQUIREMENTS
- All API endpoints have tests
- Simulation engine produces realistic results
- Frontend renders correctly
- Real-time predictions respond in <500ms

## DO NOT
- Break existing simulation engine
- Remove working features
- Skip error handling
- Ignore Figma specifications
```

---

# PART 7: NEXT STEPS

## Immediate Actions

1. **Review this document** - Does this match your vision?

2. **Install Ralph**:
   ```bash
   git clone https://github.com/frankbria/ralph-claude-code.git ~/ralph-claude-code
   cd ~/ralph-claude-code
   ./install.sh
   ```

3. **Set up PROMPT.md** in project root with the specification above

4. **Run Ralph**:
   ```bash
   cd "/Users/owenshar/Desktop/RLTX/Demos/Populous demo"
   ralph --monitor
   ```

5. **Monitor progress** - Ralph will continuously build until success criteria met

## Questions for You

Before I start building:

1. **Authentication**: Should we add auth now or defer to later?
2. **Database**: SQLite for demo, or PostgreSQL from start?
3. **Hosting**: Stay on Railway, or move to Vercel/other?
4. **Timeline**: Is the 3-week estimate realistic for your needs?
5. **Demo audience**: Who specifically will see the first demo?

---

# SUMMARY

## What We're Building
A production-grade Decision Intelligence platform that:
- Simulates synthetic audiences in real-time
- Predicts survey responses as questions are written
- Suggests improvements and detects bias
- Generates execution plans, not just predictions
- Provides audit trails and explainability

## How We're Building It
- Ralph CLI for continuous autonomous development
- Stanford generative agents architecture
- Exact Figma UI implementation
- Full backend-frontend integration

## Why It Matters
Fortune 500 leaders will pay $100K+/year because:
- Speed: 30 seconds vs. 6 months
- Accuracy: 90%+ survey correlation
- Actionability: "Do X by Tuesday" not "67% probability"
- Credibility: Interview any synthetic customer
- Trust: Audit trail for boards and regulators

This is Decision Advantage.
