# RLTX Populous: Figma-to-Implementation Plan

## Executive Summary

This document maps the Figma design screens to the current Populous codebase and outlines the implementation plan to achieve pixel-perfect design parity. The goal is to transform the existing Reflex-based prototype into a polished application matching the Figma designs exactly.

---

## Figma Design Analysis

### Screen Inventory

Based on the 12 Figma screenshots, the application has these core views:

| Screen | Figma File | Description |
|--------|------------|-------------|
| **All Projects Dashboard** | 4.29.56 PM, 4.30.16 PM | Main project listing with cards, filters, team activity feed |
| **Audiences View** | 4.30.22 PM | Audience management with sidebar navigation, data table |
| **Create Audience - Empty** | 4.30.30 PM | Audience creation wizard with form fields |
| **Create Audience - Generating** | 4.30.36 PM | Loading state with modal overlay |
| **Create Audience - Created** | 4.30.39 PM | Populated audience with profile table |
| **Templates - Audiences** | 4.30.47 PM | Template library for audiences |
| **Templates - Projects** | 4.30.52 PM | Template library for projects |
| **Templates - Scenarios** | 4.30.56 PM | Template library for scenarios |
| **New Project - Empty** | 4.30.59 PM | Three-panel project builder (Question Builder, Survey Preview, Response Predictions) |
| **New Project - First Question** | 4.31.04 PM | Active question editing with live preview |
| **New Project - AI Suggestion** | 4.31.08 PM | AI-powered question suggestions with bias detection |

---

## Design System Analysis

### Color Palette
- **Background**: `#FFFFFF` (white), `#F8F9FA` (light gray for panels)
- **Primary Blue**: `#2563EB` (buttons, selected states, progress bars)
- **Text Primary**: `#111827` (headings)
- **Text Secondary**: `#6B7280` (descriptions, labels)
- **Border**: `#E5E7EB` (card borders, dividers)
- **Success**: `#10B981` (green badges)
- **Purple Gradient**: `#8B5CF6` to `#EC4899` (gender ratio slider)

### Typography
- **Font Family**: Inter (or system sans-serif)
- **Headings**: 18-24px, weight 600
- **Body**: 14px, weight 400
- **Labels**: 12px, weight 500
- **Subtext**: 12px, weight 400, color gray

### Layout Grid
- **Sidebar Width**: 240px (collapsible)
- **Content Max Width**: ~1200px
- **Card Grid**: 2-column for projects, 4-column for templates
- **Spacing**: 8px base unit (8, 16, 24, 32px)

### Component Patterns

#### Cards
- Border radius: 8px
- Shadow: subtle `0 1px 3px rgba(0,0,0,0.1)`
- Padding: 16-24px
- Hover state: slight shadow increase

#### Buttons
- Primary: Blue background, white text, 8px radius
- Secondary: White background, gray border
- Ghost: No background, blue text

#### Pills/Chips
- Selected: Blue background, white text
- Unselected: White background, gray border

#### Data Tables
- Header: Light gray background
- Rows: White with bottom border
- Row hover: Light blue tint

---

## Current Build Assessment

### What Exists (Backend - Ready)
| Component | File | Status |
|-----------|------|--------|
| Agent Models | `backend/models/agent.py` | Complete |
| Scenario Models | `backend/models/scenario.py` | Complete |
| Strategy Models | `backend/models/strategy.py` | Complete |
| Results Models | `backend/models/results.py` | Complete |
| Decision Engine | `backend/engine/decision_engine.py` | Complete |
| Market Dynamics | `backend/engine/market_dynamics.py` | Complete |
| Agent Factory | `backend/engine/agent_factory.py` | Complete |
| Simulation Runner | `backend/engine/runner.py` | Complete |
| FastAPI Routes | `backend/api/main.py` | Complete |
| Demo Presets | `backend/data/presets/b2b_saas.py` | Complete |

### What Exists (Frontend - Needs Redesign)
| Component | File | Status |
|-----------|------|--------|
| Basic Reflex App | `frontend/app.py` | Functional but doesn't match Figma |

### What's Missing (Figma Features)
1. **Sidebar Navigation** - Current app uses tabs, Figma has persistent sidebar
2. **Project Cards** - Need redesign with progress bars, metrics, tags
3. **Audience Management** - New feature entirely
4. **Audience Profiles Table** - New feature with AI-generated personas
5. **Template Library** - New browsing/filtering system
6. **Survey Builder UI** - Three-panel layout with live preview
7. **AI Suggestions** - Question suggestions with bias detection
8. **Team Activity Feed** - Right sidebar with notifications
9. **Search** - Global search in header

---

## Implementation Architecture

### Recommended Stack Change

The Figma designs show a sophisticated UI that would be better served by a React/Next.js frontend rather than Reflex. However, to maintain the current Python-centric approach, here's the plan:

**Option A: Enhanced Reflex (Faster, Python-only)**
- Upgrade Reflex components to match Figma
- Use custom CSS for precise styling
- Leverage Reflex's Tailwind integration

**Option B: Next.js Frontend (Recommended for Production)**
- Build React frontend with Tailwind CSS
- Keep FastAPI backend unchanged
- Better performance, more design flexibility

For this plan, we'll pursue **Option A** with a path to **Option B**.

---

## Component Mapping

### 1. Navigation Sidebar

**Figma Elements:**
- Logo + App name at top
- Search bar
- Icon + text nav items:
  - Projects (grid icon)
  - Audiences (users icon)
  - Templates (layout icon)
  - Analytics (bar-chart icon)
  - Assets (folder icon)
  - Settings (cog icon)
- Collapsed state support

**Backend Model Needed:** None (UI-only)

**New Reflex Component:**
```python
def sidebar() -> rx.Component:
    return rx.box(
        logo_section(),
        search_bar(),
        nav_items(),
        position="fixed",
        left="0",
        top="0",
        width="240px",
        height="100vh",
        border_right="1px solid #E5E7EB",
        background="#FFFFFF",
    )
```

---

### 2. All Projects Dashboard

**Figma Elements:**
- Header: "All Projects" + "New Project" button
- Filter tabs: All Projects, Active, Running, Completed
- Sort dropdown
- Project cards in 2-column grid
- Each card shows:
  - Project name
  - Description snippet
  - Completion metric (e.g., "3000 / 5000")
  - Progress bar
  - Completion percentage
  - Status tags (Running, Completed, etc.)
  - Date/time info

**Backend Model Needed:**
```python
# New model for Projects (extends Scenario)
class Project(BaseModel):
    id: str
    name: str
    description: str
    scenario_id: Optional[str]
    strategy_ids: List[str]
    audience_id: Optional[str]

    # Progress tracking
    status: str  # "draft", "running", "completed"
    responses_collected: int = 0
    responses_target: int = 0

    # Metadata
    created_at: datetime
    updated_at: datetime
    owner_id: str

    # Tags
    tags: List[str] = []
```

**API Endpoints Needed:**
- `GET /projects` - List all projects
- `POST /projects` - Create project
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

---

### 3. Audiences Management

**Figma Elements:**
- Left sidebar: List of audiences with counts
- Main area: Selected audience details
  - Name, description
  - Stats (age range, income, gender split)
- Audience Profiles Table:
  - Avatar (initials)
  - Name
  - Age
  - Education
  - Occupation
  - Income
  - Location

**Backend Model Needed:**
```python
class AudienceProfile(BaseModel):
    """Individual persona in an audience"""
    id: str
    name: str
    age: int
    gender: str
    education: str
    occupation: str
    income: str  # Range like "$80,000"
    location: str
    avatar_url: Optional[str] = None

class Audience(BaseModel):
    """A collection of synthetic personas"""
    id: str
    name: str
    description: str

    # Generation parameters
    purpose: str  # "pricing_analysis", "product_launch", etc.
    age_range: tuple[int, int]
    gender_ratio: tuple[float, float]  # male%, female%
    income_level: str  # "low", "middle", "upper-middle", "high"

    # Decision factors
    decision_factors: List[str]
    precision_level: str  # "general", "specific", "exact"

    # Generated profiles
    profiles: List[AudienceProfile] = []
    profile_count: int = 0

    # Metadata
    created_at: datetime
    source_csv: Optional[str] = None
```

**API Endpoints Needed:**
- `GET /audiences` - List audiences
- `POST /audiences` - Create audience
- `POST /audiences/generate` - Generate audience with AI
- `GET /audiences/{id}` - Get audience with profiles
- `GET /audiences/{id}/profiles` - Paginated profiles
- `POST /audiences/{id}/import` - Import from CSV

---

### 4. Create Audience Wizard

**Figma Elements (Form Fields):**
1. Audience Title (text input)
2. Description (textarea)
3. Purpose pills: Pricing analysis, Product launch, Concept testing, Positioning, Market expansion, General exploration
4. Age range (dual input: from/to)
5. Gender ratio slider (Male 30% / Female 70%)
6. Income level pills: Low, Middle, Upper-middle, High
7. Decision factors dropdown
8. Precision level dropdown
9. CSV upload zone
10. "Generate Audience" button

**Loading State:**
- Modal overlay
- "Generating your Audience" message
- Progress bar
- Cancel button

**Backend Logic:**
```python
@app.post("/audiences/generate")
async def generate_audience(request: AudienceGenerationRequest):
    """
    Uses Claude to generate realistic personas matching criteria
    """
    # 1. Validate input
    # 2. Create audience record
    # 3. Call Claude API to generate profiles
    # 4. Store profiles
    # 5. Return audience with profiles
```

---

### 5. Templates Library

**Figma Elements:**
- Tab filters: Audiences, Projects, Scenarios
- Card grid (4 columns)
- Each template card:
  - Title
  - Description
  - Bullet points of features
  - "Use Audience/Project/Scenario" button

**Backend Model:**
```python
class Template(BaseModel):
    id: str
    type: str  # "audience", "project", "scenario"
    name: str
    description: str
    features: List[str]

    # The actual template data
    template_data: Dict[str, Any]

    # Metadata
    category: str
    popularity: int = 0
```

---

### 6. New Project / Survey Builder

**Figma Layout (3 Panels):**

**Panel 1: Question Builder**
- "Add Question" button
- Question list with:
  - Question number
  - Type badge (Single choice, Rating scale, etc.)
  - Question text
  - Edit/Delete icons
- Selected question edit form:
  - Question Type dropdown
  - Question Text input
  - Answer Options (add/remove)

**Panel 2: Survey Preview**
- Live respondent view
- Progress indicator ("Question 1 of 1")
- Question rendering
- Answer options (radio buttons, sliders, etc.)
- Back/Next/Submit buttons

**Panel 3: Response Predictions**
- Overall Confidence badge
- Prediction cards per question
- Distribution bars (Better Features: 85%, Lower price: 46%, etc.)
- Mean score for rating questions
- "Updating predictions..." loading state

**Footer:**
- Audience selector dropdown
- Sample size dropdown
- Estimated runtime
- "Run Survey" button

**Backend Models:**
```python
class QuestionType(str, Enum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    RATING_SCALE = "rating_scale"
    OPEN_TEXT = "open_text"
    RANKING = "ranking"

class Question(BaseModel):
    id: str
    type: QuestionType
    text: str
    options: List[str] = []  # For choice questions
    scale_min: Optional[int] = None  # For rating scale
    scale_max: Optional[int] = None
    required: bool = True

class Survey(BaseModel):
    id: str
    project_id: str
    questions: List[Question]

class SurveyPrediction(BaseModel):
    question_id: str
    confidence: str  # "low", "medium", "high"
    predictions: Dict[str, float]  # option -> predicted %
    mean_score: Optional[float] = None
    distribution_note: Optional[str] = None

class AIQuestionSuggestion(BaseModel):
    suggested_text: str
    reasoning: str
    potential_bias: Optional[str] = None
    bias_severity: Optional[str] = None  # "warning", "error"
```

---

### 7. AI Suggestions Feature

**Figma Elements:**
- Blue "AI Suggestion" banner
- Suggested question text
- "Add Suggested Question" / "Dismiss" buttons
- "Potential Bias Detected" warning banner
- Original vs suggested text comparison
- "Apply Suggestions" button

**Backend Endpoint:**
```python
@app.post("/surveys/{survey_id}/suggest")
async def suggest_questions(survey_id: str):
    """
    Analyzes current questions and suggests improvements
    """
    # Uses Claude to:
    # 1. Analyze survey goals
    # 2. Identify gaps in coverage
    # 3. Detect potential bias
    # 4. Suggest rewording

@app.post("/questions/{question_id}/check-bias")
async def check_question_bias(question_id: str):
    """
    Checks a single question for leading language, bias
    """
```

---

### 8. Team Activity Feed (Right Sidebar)

**Figma Elements:**
- "Team Activities" header
- Activity items:
  - User avatar
  - User name
  - Action text
  - Timestamp
- Alert section:
  - Warning icon
  - Alert title
  - Alert description

**Backend Model:**
```python
class Activity(BaseModel):
    id: str
    user_id: str
    user_name: str
    user_avatar: Optional[str]
    action: str  # "created", "updated", "completed", etc.
    target_type: str  # "project", "audience", "survey"
    target_id: str
    target_name: str
    timestamp: datetime

class Alert(BaseModel):
    id: str
    severity: str  # "info", "warning", "error"
    title: str
    description: str
    target_type: Optional[str]
    target_id: Optional[str]
    dismissed: bool = False
```

---

## Implementation Phases

### Phase 1: Foundation (Design System + Navigation)
1. Create design tokens (colors, typography, spacing)
2. Build sidebar navigation component
3. Build header with search
4. Create base layout wrapper
5. Style all existing components to match Figma

**Files to Create/Modify:**
- `frontend/styles/tokens.css` - Design tokens
- `frontend/components/sidebar.py` - Navigation
- `frontend/components/header.py` - Header with search
- `frontend/components/layout.py` - Page wrapper

### Phase 2: Projects Dashboard
1. Create Project model in backend
2. Build project card component
3. Build projects grid
4. Add filtering and sorting
5. Implement "New Project" flow

**Files to Create/Modify:**
- `backend/models/project.py` - Project model
- `backend/api/projects.py` - Project endpoints
- `frontend/pages/projects.py` - Dashboard page
- `frontend/components/project_card.py` - Card component

### Phase 3: Audiences Feature
1. Create Audience and AudienceProfile models
2. Build audience list sidebar
3. Build audience detail view with profiles table
4. Implement Create Audience wizard
5. Add AI generation integration

**Files to Create/Modify:**
- `backend/models/audience.py` - Audience models
- `backend/api/audiences.py` - Audience endpoints
- `backend/engine/audience_generator.py` - AI generation
- `frontend/pages/audiences.py` - Audiences page
- `frontend/components/audience_table.py` - Profiles table
- `frontend/components/create_audience.py` - Wizard

### Phase 4: Survey Builder
1. Create Survey, Question models
2. Build three-panel layout
3. Build question builder panel
4. Build survey preview panel
5. Build predictions panel
6. Add real-time prediction updates

**Files to Create/Modify:**
- `backend/models/survey.py` - Survey models
- `backend/api/surveys.py` - Survey endpoints
- `backend/engine/survey_predictor.py` - Prediction engine
- `frontend/pages/new_project.py` - Survey builder page
- `frontend/components/question_builder.py`
- `frontend/components/survey_preview.py`
- `frontend/components/predictions_panel.py`

### Phase 5: AI Features
1. Implement question suggestion endpoint
2. Implement bias detection endpoint
3. Build AI suggestion UI component
4. Build bias warning component
5. Integrate with survey builder

**Files to Create/Modify:**
- `backend/api/ai.py` - AI feature endpoints
- `backend/engine/question_analyzer.py` - Analysis logic
- `frontend/components/ai_suggestion.py`
- `frontend/components/bias_warning.py`

### Phase 6: Templates & Polish
1. Create Template model and presets
2. Build templates page with filtering
3. Implement "Use Template" flow
4. Build team activity feed
5. Final styling polish

**Files to Create/Modify:**
- `backend/models/template.py`
- `backend/data/templates/*.py` - Template presets
- `frontend/pages/templates.py`
- `frontend/components/activity_feed.py`

---

## File Structure After Implementation

```
rltx-populous/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app + routes
│   │   ├── projects.py      # NEW: Project CRUD
│   │   ├── audiences.py     # NEW: Audience CRUD
│   │   ├── surveys.py       # NEW: Survey CRUD
│   │   ├── ai.py            # NEW: AI features
│   │   └── templates.py     # NEW: Templates
│   ├── models/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── scenario.py
│   │   ├── strategy.py
│   │   ├── results.py
│   │   ├── project.py       # NEW
│   │   ├── audience.py      # NEW
│   │   ├── survey.py        # NEW
│   │   └── template.py      # NEW
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── agent_factory.py
│   │   ├── decision_engine.py
│   │   ├── market_dynamics.py
│   │   ├── runner.py
│   │   ├── audience_generator.py    # NEW
│   │   ├── survey_predictor.py      # NEW
│   │   └── question_analyzer.py     # NEW
│   ├── data/
│   │   ├── presets/
│   │   │   └── b2b_saas.py
│   │   └── templates/       # NEW
│   │       ├── audiences.py
│   │       ├── projects.py
│   │       └── scenarios.py
│   └── run.py
├── frontend/
│   ├── styles/
│   │   └── tokens.css       # NEW: Design system
│   ├── components/
│   │   ├── sidebar.py       # NEW
│   │   ├── header.py        # NEW
│   │   ├── layout.py        # NEW
│   │   ├── project_card.py  # NEW
│   │   ├── audience_table.py # NEW
│   │   ├── create_audience.py # NEW
│   │   ├── question_builder.py # NEW
│   │   ├── survey_preview.py # NEW
│   │   ├── predictions_panel.py # NEW
│   │   ├── ai_suggestion.py # NEW
│   │   ├── bias_warning.py  # NEW
│   │   └── activity_feed.py # NEW
│   ├── pages/
│   │   ├── projects.py      # NEW
│   │   ├── audiences.py     # NEW
│   │   ├── new_project.py   # NEW
│   │   └── templates.py     # NEW
│   ├── app.py               # UPDATED
│   └── rxconfig.py
├── tests/
├── .env.example
├── requirements.txt         # UPDATED
└── README.md
```

---

## Key Technical Decisions

### 1. State Management
The Figma designs show complex state (wizard flows, real-time updates, multi-panel sync). Reflex's built-in state should handle this, but consider:
- Use computed vars for derived state
- Keep API calls in separate event handlers
- Use background tasks for long operations

### 2. Real-Time Predictions
The "Response Predictions" panel updates as questions change. Implementation:
```python
# Debounced prediction updates
async def update_predictions(self):
    if self.debounce_timer:
        self.debounce_timer.cancel()
    self.debounce_timer = asyncio.create_task(
        self._delayed_prediction_update()
    )

async def _delayed_prediction_update(self):
    await asyncio.sleep(0.5)  # 500ms debounce
    # Call prediction API
```

### 3. Audience Generation
Large audience generation (100+ profiles) should run as background task with progress:
```python
@app.post("/audiences/{id}/generate")
async def generate_profiles(id: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        _generate_profiles_task,
        audience_id=id,
        count=100
    )
    return {"status": "generating"}
```

### 4. Survey Preview Rendering
The preview panel shows a live survey as respondents would see it. Options:
- Render within Reflex (current approach)
- Embed an iframe with actual survey renderer
- Use Reflex's dynamic component rendering

---

## Migration Path to React (Optional)

If you decide Reflex can't achieve the Figma fidelity:

1. **Keep FastAPI backend unchanged** - All API endpoints work
2. **Create Next.js project** in separate folder
3. **Use Tailwind CSS** for styling (matches Figma export)
4. **Components library**: shadcn/ui or Radix (similar to Reflex's Radix base)
5. **State**: React Query for server state, Zustand for UI state
6. **Deploy**: Frontend on Vercel, Backend on any Python host

---

## Testing Checklist

### Visual Regression
- [ ] All pages match Figma designs at 1440px width
- [ ] All pages are responsive at 1024px, 768px
- [ ] Dark mode support (if applicable)
- [ ] All interactive states (hover, focus, active, disabled)

### Functional
- [ ] Project CRUD operations
- [ ] Audience generation completes successfully
- [ ] Survey builder saves questions correctly
- [ ] Predictions update in real-time
- [ ] AI suggestions appear for appropriate triggers
- [ ] Template application creates correct records

### Performance
- [ ] Initial page load < 2s
- [ ] Audience generation < 30s for 100 profiles
- [ ] Survey predictions update < 1s
- [ ] Project list loads < 500ms

---

## Conclusion

The current Populous build has a solid backend foundation. The primary work is:

1. **Redesigning the frontend** to match Figma designs exactly
2. **Adding new features**: Audiences, Survey Builder, Templates
3. **Integrating AI features**: Suggestions, bias detection, predictions

The backend simulation engine (agent factory, decision engine, Monte Carlo runner) is production-ready and can power the new survey prediction features.

Estimated effort: 4-6 weeks for full implementation with one developer.
