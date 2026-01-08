# RLTX Populous: Complete Implementation Guide

## Reference-First Development Protocol

This document serves as the **single source of truth** for implementing the Populous application from Figma designs. Every component must be verified against this document and the original screenshots before being marked complete.

---

## Part 1: Design System Extraction

### 1.1 Color Palette (Extracted from Figma)

```css
/* Primary Colors */
--color-primary: #2563EB;          /* Blue - buttons, selected states, links */
--color-primary-hover: #1D4ED8;    /* Blue hover state */
--color-primary-light: #DBEAFE;    /* Blue tint for backgrounds */

/* Neutral Colors */
--color-white: #FFFFFF;
--color-gray-50: #F9FAFB;          /* Page background */
--color-gray-100: #F3F4F6;         /* Card backgrounds, table headers */
--color-gray-200: #E5E7EB;         /* Borders, dividers */
--color-gray-300: #D1D5DB;         /* Input borders */
--color-gray-400: #9CA3AF;         /* Placeholder text */
--color-gray-500: #6B7280;         /* Secondary text */
--color-gray-600: #4B5563;         /* Body text */
--color-gray-700: #374151;         /* Headings */
--color-gray-800: #1F2937;         /* Dark headings */
--color-gray-900: #111827;         /* Darkest text */

/* Semantic Colors */
--color-success: #10B981;          /* Green badges, success states */
--color-warning: #F59E0B;          /* Orange/yellow warnings */
--color-error: #EF4444;            /* Red errors */
--color-info: #3B82F6;             /* Blue info */

/* Special - Gender Slider Gradient */
--gradient-gender: linear-gradient(90deg, #3B82F6 0%, #8B5CF6 50%, #EC4899 100%);

/* Prediction Bar Colors */
--color-bar-1: #3B82F6;            /* Primary prediction bar */
--color-bar-2: #60A5FA;            /* Secondary */
--color-bar-3: #93C5FD;            /* Tertiary */
```

### 1.2 Typography Scale

```css
/* Font Family */
--font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Font Sizes */
--text-xs: 0.75rem;      /* 12px - badges, timestamps, hints */
--text-sm: 0.875rem;     /* 14px - body text, labels */
--text-base: 1rem;       /* 16px - primary body */
--text-lg: 1.125rem;     /* 18px - section headings */
--text-xl: 1.25rem;      /* 20px - page titles */
--text-2xl: 1.5rem;      /* 24px - main headings */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* Line Heights */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
```

### 1.3 Spacing System (8px Grid)

```css
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
```

### 1.4 Border Radius

```css
--radius-sm: 0.25rem;   /* 4px - small badges */
--radius-md: 0.375rem;  /* 6px - inputs, buttons */
--radius-lg: 0.5rem;    /* 8px - cards */
--radius-xl: 0.75rem;   /* 12px - modals */
--radius-full: 9999px;  /* Pills, avatars */
```

### 1.5 Shadows

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
```

### 1.6 Layout Dimensions

```css
/* Sidebar */
--sidebar-width-collapsed: 64px;
--sidebar-width-expanded: 240px;

/* Header */
--header-height: 64px;

/* Content */
--content-max-width: 1280px;
--content-padding: 24px;

/* Cards */
--card-padding: 20px;

/* Panels (Survey Builder) */
--panel-min-width: 320px;
```

---

## Part 2: Component Specifications

### 2.1 Global Navigation (Header)

**Reference:** Screenshots 4.29.56, 4.30.59

```
┌─────────────────────────────────────────────────────────────────────────┐
│ [Logo] │ ○ Search anything...                    │ 🔔 ⚙️ [Avatar] [+ New Project] │
└─────────────────────────────────────────────────────────────────────────┘
```

**Specifications:**
- Height: 64px
- Background: white (#FFFFFF)
- Border-bottom: 1px solid #E5E7EB
- Logo: "POPULOUS" with grid icon, left-aligned
- Search: Rounded input, placeholder "Search anything...", magnifying glass icon
- Right section: notification icon, settings icon, user avatar (32px circle), primary button

**Component Props:**
```typescript
interface HeaderProps {
  onSearch: (query: string) => void;
  onNewProject: () => void;
  user: {
    name: string;
    avatarUrl: string;
  };
  notificationCount?: number;
}
```

### 2.2 Sidebar Navigation

**Reference:** Screenshots 4.29.56, 4.30.22, 4.30.59

```
┌────┐
│ □  │  ← Logo icon (collapsed state)
├────┤
│ ⊞  │  ← Projects (grid icon)
│ 👥 │  ← Audiences (users icon)
│ ◎  │  ← Templates (compass/layout icon)
│ 📊 │  ← Analytics (bar chart icon)
│ 📁 │  ← Assets (folder icon)
│ ⚙️ │  ← Settings (cog icon)
└────┘
```

**Specifications:**
- Width collapsed: 64px
- Width expanded: 240px
- Background: white (#FFFFFF)
- Border-right: 1px solid #E5E7EB
- Icon size: 20px
- Icon color default: #6B7280
- Icon color active: #2563EB
- Active indicator: Blue left border (3px) or background tint

**Navigation Items:**
1. Projects (path: `/projects`) - Grid/dashboard icon
2. Audiences (path: `/audiences`) - Users icon
3. Templates (path: `/templates`) - Layout/compass icon
4. Analytics (path: `/analytics`) - Bar chart icon
5. Assets (path: `/assets`) - Folder icon
6. Settings (path: `/settings`) - Cog icon

### 2.3 Project Card

**Reference:** Screenshot 4.29.56

```
┌──────────────────────────────────────┐
│ SparkZero Pricing Study              │
│ Consumer Test • Value Sat • Shipping │
│                                      │
│ 3000          ████████████░░░░  82%  │
│               [progress bar]         │
│                                      │
│ [Running] [+2 tags]                  │
└──────────────────────────────────────┘
```

**Specifications:**
- Background: white
- Border: 1px solid #E5E7EB
- Border-radius: 8px
- Padding: 20px
- Hover: shadow-md, border-color: #D1D5DB

**Data Structure:**
```typescript
interface Project {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'running' | 'completed' | 'paused';
  responsesCollected: number;
  responsesTarget: number;
  completionPercentage: number;
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
}
```

### 2.4 Audience Profiles Table

**Reference:** Screenshot 4.30.22

```
┌──┬────────┬─────┬────────────┬────────────┬─────────┬──────────┐
│☐ │ Name   │ Age │ Education  │ Occupation │ Income  │ Location │
├──┼────────┼─────┼────────────┼────────────┼─────────┼──────────┤
│☐ │○ Ryan S│ 24  │ Undergrad  │ College St │ $40,000 │ Austin   │
│☐ │○ Mark H│ 27  │ High School│ Bartender  │ $35,000 │ Miami    │
└──┴────────┴─────┴────────────┴────────────┴─────────┴──────────┘
```

**Specifications:**
- Header row: background #F9FAFB, font-weight 500
- Row height: 52px
- Avatar: 32px circle with initials or image
- Border-bottom on rows: 1px solid #E5E7EB
- Hover row: background #F9FAFB

**Data Structure:**
```typescript
interface AudienceProfile {
  id: string;
  name: string;
  age: number;
  gender: 'male' | 'female' | 'other';
  education: string;
  occupation: string;
  income: string;
  location: string;
  avatarUrl?: string;
}
```

### 2.5 Create Audience Form

**Reference:** Screenshot 4.30.30

**Form Fields (in order):**

1. **Audience Title**
   - Type: text input
   - Placeholder: "e.g Millennial Pet Owners"
   - Validation: required, min 3 chars

2. **Describe your audience**
   - Type: textarea
   - Placeholder: Long example text about audience description
   - Rows: 4

3. **What are you creating this audience for?**
   - Type: pill/chip select (single)
   - Options:
     - "Pricing analysis" (default selected)
     - "Product launch"
     - "Concept testing"
     - "Positioning"
     - "Market expansion"
     - "General exploration"
   - Layout: 2 rows, 3 per row

4. **How old are the people in this audience?**
   - Type: dual number input
   - Labels: [input] "to" [input]
   - Placeholders: "18 Years", "32 Years"

5. **What should be the Gender Ratio?**
   - Type: custom slider
   - Labels: "Male (30%)" left, "Female (70%)" right
   - Visual: gradient slider from blue to pink/purple

6. **How would you describe their income level?**
   - Type: pill/chip select (single)
   - Options: "Low", "Middle" (default), "Upper-middle", "High"
   - Layout: single row

7. **What matters most when they make decisions?**
   - Type: select dropdown
   - Placeholder: "Select Option"

8. **How precise does this audience need to be?**
   - Type: select dropdown
   - Placeholder: "Select Option"

9. **Upload CSV of real customer attributes**
   - Type: file upload zone
   - Text: "Drag and drop or Choose File"
   - Icon: upload cloud

10. **Generate Audience button**
    - Type: primary button, full width
    - Text: "Generate Audience"

### 2.6 Survey Builder - Three Panel Layout

**Reference:** Screenshots 4.30.59, 4.31.04, 4.31.08

```
┌─────────────────┬─────────────────┬─────────────────┐
│ Question Builder│ Survey Preview  │ Response        │
│                 │                 │ Predictions     │
│ Build your      │ Live respondent │ AI-powered      │
│ survey questions│ view            │ insights        │
│                 │                 │                 │
│ [Content]       │ [Content]       │ [Content]       │
│                 │                 │                 │
│                 │                 │                 │
│                 │                 │                 │
├─────────────────┴─────────────────┴─────────────────┤
│ Audience: [dropdown]  Sample Size: [100]  [Run Survey]│
└─────────────────────────────────────────────────────┘
```

**Panel Specifications:**
- Each panel: white background, border 1px solid #E5E7EB, border-radius 8px
- Panel header: title (font-semibold, text-lg) + subtitle (text-sm, gray-500)
- Min-width per panel: 320px
- Gap between panels: 16px

### 2.7 Question Builder Panel

**Reference:** Screenshot 4.31.04, 4.31.08

**Header:**
- Title: "Question Builder"
- Subtitle: "Build your survey questions"
- Action: "+ Add Question" button (outline style)

**Question List Item:**
```
┌─────────────────────────────────────────────────────┐
│ ≡ Question 01  [Single choice]          ✏️ 🗑️      │
│   What is your primary reason for using our product?│
└─────────────────────────────────────────────────────┘
```
- Drag handle (≡)
- Question number badge: "Question 01" with border
- Type badge: "Single choice" (blue text, blue border)
- Edit/Delete icons on right
- Question text below

**Edit Question Form:**
- "Question Type" - dropdown (Single Choice Radio Button, Multiple Choice, Rating Scale, Open Text)
- "Question Text" - text input
- "Answer Options" - list of inputs with delete buttons
- "+ Add Option" button

**AI Suggestion Banner:**
```
┌─────────────────────────────────────────────────────┐
│ ✨ AI Suggestion                                    │
│                                                     │
│ Based on your goal to understand product usage,     │
│ consider asking about price sensitivity...          │
│                                                     │
│ [Add Suggested Question]  Dismiss                   │
└─────────────────────────────────────────────────────┘
```
- Background: light blue (#DBEAFE or similar)
- Icon: sparkles
- Primary action: blue button
- Secondary: text link

**Bias Warning Banner:**
```
┌─────────────────────────────────────────────────────┐
│ ⚠️ Potential Bias Detected                         │
│                                                     │
│ This question may be leading. Consider rephrasing  │
│ to: "How would you rate the product's pricing?"    │
│                                                     │
│ ○ Apply Suggestions                                │
└─────────────────────────────────────────────────────┘
```
- Background: light yellow/orange
- Icon: warning triangle
- Checkbox to apply

### 2.8 Survey Preview Panel

**Reference:** Screenshots 4.31.04, 4.31.08

**Header:**
- Progress: "Question 1 of 1" + progress bar + "100%"

**Question Display:**
- Question text (font-medium, text-base)
- Answer options as radio buttons or rating scale

**Radio Option (Selected):**
```
● Better Features     ← Blue filled circle
○ Lower price        ← Empty circle
○ Ease of use
○ Customer support
```

**Rating Scale:**
```
Very Dissatisfied                    Very Satisfied
    ○       ○       ○       ●       ○
    1       2       3       4       5
```

**Navigation:**
- "← Back" button (outline)
- "Next →" or "Submit" button (primary)

### 2.9 Response Predictions Panel

**Reference:** Screenshots 4.31.04, 4.31.08

**Header:**
- Title: "Response Predictions"
- Subtitle: "AI-powered insights"

**Confidence Badge:**
```
Overall Confidence  [Low/Medium/High]
```
- Badge colors: Low (gray), Medium (blue), High (green)

**Prediction Card:**
```
┌─────────────────────────────────────────────────────┐
│ Q1: Primary Reasons                          [Low]  │
│                                                     │
│ Better Features  ████████████████████░░░░░░░  85%  │
│ Lower price      ██████████░░░░░░░░░░░░░░░░░  46%  │
│ Ease of use      ████████░░░░░░░░░░░░░░░░░░░  35%  │
│ Customer support ██████░░░░░░░░░░░░░░░░░░░░░  28%  │
└─────────────────────────────────────────────────────┘
```

**Rating Question Prediction:**
```
Q2: Pricing Satisfaction                     [Medium]

Updating predictions...

Mean Score: 3.2/5.0
Distribution: Slightly negative skew expected
```

**Footer Note:**
- Small text: "Predictions based on similar surveys and general audience patterns"
- Icon: info circle

---

## Part 3: Screen-by-Screen Implementation

### Phase 1: Foundation Layer

#### 1.1 Project Setup
```bash
# Create Next.js project
npx create-next-app@latest populous-frontend --typescript --tailwind --eslint --app --src-dir

# Install dependencies
npm install @radix-ui/react-icons @radix-ui/react-slot
npm install class-variance-authority clsx tailwind-merge
npm install @tanstack/react-query axios
npm install react-hook-form @hookform/resolvers zod
npm install framer-motion
npm install recharts  # for charts
```

#### 1.2 File Structure
```
populous-frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout with sidebar
│   │   ├── page.tsx                # Redirect to /projects
│   │   ├── projects/
│   │   │   ├── page.tsx            # All Projects dashboard
│   │   │   └── [id]/
│   │   │       └── page.tsx        # Project detail / Survey builder
│   │   ├── audiences/
│   │   │   ├── page.tsx            # Audiences list
│   │   │   └── create/
│   │   │       └── page.tsx        # Create audience wizard
│   │   └── templates/
│   │       └── page.tsx            # Templates library
│   ├── components/
│   │   ├── ui/                     # Base UI components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── card.tsx
│   │   │   ├── progress.tsx
│   │   │   ├── slider.tsx
│   │   │   ├── table.tsx
│   │   │   ├── tabs.tsx
│   │   │   └── avatar.tsx
│   │   ├── layout/
│   │   │   ├── header.tsx
│   │   │   ├── sidebar.tsx
│   │   │   └── page-container.tsx
│   │   ├── projects/
│   │   │   ├── project-card.tsx
│   │   │   ├── project-grid.tsx
│   │   │   └── project-filters.tsx
│   │   ├── audiences/
│   │   │   ├── audience-list.tsx
│   │   │   ├── audience-detail.tsx
│   │   │   ├── audience-table.tsx
│   │   │   └── create-audience-form.tsx
│   │   ├── survey-builder/
│   │   │   ├── question-builder.tsx
│   │   │   ├── question-item.tsx
│   │   │   ├── question-form.tsx
│   │   │   ├── survey-preview.tsx
│   │   │   ├── predictions-panel.tsx
│   │   │   ├── ai-suggestion.tsx
│   │   │   └── bias-warning.tsx
│   │   └── shared/
│   │       ├── empty-state.tsx
│   │       ├── loading-spinner.tsx
│   │       └── activity-feed.tsx
│   ├── lib/
│   │   ├── api.ts                  # API client
│   │   ├── utils.ts                # Utility functions
│   │   └── constants.ts
│   ├── hooks/
│   │   ├── use-projects.ts
│   │   ├── use-audiences.ts
│   │   └── use-predictions.ts
│   ├── types/
│   │   ├── project.ts
│   │   ├── audience.ts
│   │   ├── survey.ts
│   │   └── api.ts
│   └── styles/
│       └── globals.css             # Design tokens + base styles
```

#### 1.3 Design Tokens (tailwind.config.ts)
```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
        },
        gray: {
          50: '#F9FAFB',
          100: '#F3F4F6',
          200: '#E5E7EB',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280',
          600: '#4B5563',
          700: '#374151',
          800: '#1F2937',
          900: '#111827',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      width: {
        'sidebar': '240px',
        'sidebar-collapsed': '64px',
      },
    },
  },
  plugins: [],
}

export default config
```

### Phase 2: All Projects Dashboard

**Target:** Screenshot 4.29.56, 4.30.16

#### Verification Checklist:
- [ ] Header matches exactly (logo, search, icons, avatar, button)
- [ ] Sidebar matches exactly (icons, active state, width)
- [ ] "All Projects" heading with filter tabs
- [ ] Project cards match (layout, metrics, progress bar, tags)
- [ ] 2-column grid layout
- [ ] Right sidebar with Team Activities (if visible)
- [ ] Hover states on cards
- [ ] Responsive behavior

### Phase 3: Audiences Feature

**Target:** Screenshots 4.30.22, 4.30.30, 4.30.36, 4.30.39

#### 3.1 Audiences List View
**Verification Checklist:**
- [ ] Left sidebar with audience list
- [ ] "+ New Audience" button styling
- [ ] Selected audience highlight (blue background tint)
- [ ] Audience counts in list items
- [ ] Main content area with selected audience detail
- [ ] Stats row with proper badges
- [ ] Profiles table matches exactly

#### 3.2 Create Audience Form
**Verification Checklist:**
- [ ] Modal/page header with close button
- [ ] All 10 form fields in correct order
- [ ] Pill button selections (Pricing analysis selected by default)
- [ ] Age range dual input with "to" label
- [ ] Gender ratio slider with gradient
- [ ] Income level pills (Middle selected by default)
- [ ] Dropdowns with "Select Option" placeholder
- [ ] File upload zone
- [ ] Full-width "Generate Audience" button
- [ ] Right side empty state

#### 3.3 Generation Loading State
**Verification Checklist:**
- [ ] Modal overlay
- [ ] "Generating your Audience" heading
- [ ] Progress bar
- [ ] Cancel button

### Phase 4: Templates Library

**Target:** Screenshots 4.30.47, 4.30.52, 4.30.56

#### Verification Checklist:
- [ ] "Templates" page heading
- [ ] Tab filters (Audiences, Projects, Scenarios)
- [ ] 4-column card grid
- [ ] Card structure (title, description bullets, action button)
- [ ] "Use Audience/Project/Scenario" buttons
- [ ] Consistent card sizing

### Phase 5: Survey Builder

**Target:** Screenshots 4.30.59, 4.31.04, 4.31.08

#### 5.1 Empty State
**Verification Checklist:**
- [ ] Three-panel layout with equal widths
- [ ] Panel headers (title + subtitle)
- [ ] Empty state icons in each panel
- [ ] Empty state text matches exactly
- [ ] "+ Add Your First Question" button
- [ ] Footer with Audience dropdown, Sample Size, Run Survey button

#### 5.2 With Questions
**Verification Checklist:**
- [ ] Question list with drag handles
- [ ] Question badges (number + type)
- [ ] Edit/delete icons
- [ ] Edit Question form fields
- [ ] Survey Preview with progress bar
- [ ] Radio button styling (selected = blue fill)
- [ ] Back/Next navigation buttons
- [ ] Predictions panel with confidence badges
- [ ] Horizontal bar charts for predictions
- [ ] Percentage labels

#### 5.3 AI Features
**Verification Checklist:**
- [ ] AI Suggestion banner (light blue background)
- [ ] Suggestion text and action buttons
- [ ] Bias Warning banner (yellow/orange background)
- [ ] Warning icon and text
- [ ] "Apply Suggestions" checkbox
- [ ] "Updating predictions..." loading state
- [ ] Mean score display for rating questions

---

## Part 4: Backend Integration Points

### 4.1 API Endpoints Required

```typescript
// Projects
GET    /api/projects                    // List all projects
POST   /api/projects                    // Create project
GET    /api/projects/:id                // Get project detail
PUT    /api/projects/:id                // Update project
DELETE /api/projects/:id                // Delete project

// Audiences
GET    /api/audiences                   // List all audiences
POST   /api/audiences                   // Create audience
GET    /api/audiences/:id               // Get audience with profiles
DELETE /api/audiences/:id               // Delete audience
POST   /api/audiences/generate          // Generate audience profiles with AI
POST   /api/audiences/:id/import        // Import profiles from CSV

// Surveys
GET    /api/projects/:id/survey         // Get survey for project
PUT    /api/projects/:id/survey         // Update survey
POST   /api/projects/:id/survey/predict // Get predictions for survey

// AI Features
POST   /api/ai/suggest-question         // Get question suggestions
POST   /api/ai/check-bias               // Check question for bias

// Templates
GET    /api/templates                   // List templates
GET    /api/templates/:id               // Get template detail
POST   /api/templates/:id/use           // Create from template
```

### 4.2 Data Models (TypeScript)

```typescript
// types/project.ts
export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'running' | 'completed' | 'paused';
  audienceId?: string;
  surveyId?: string;
  responsesCollected: number;
  responsesTarget: number;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

// types/audience.ts
export interface Audience {
  id: string;
  name: string;
  description: string;
  purpose: AudiencePurpose;
  ageRange: [number, number];
  genderRatio: { male: number; female: number };
  incomeLevel: IncomeLevel;
  decisionFactors: string[];
  precision: PrecisionLevel;
  profileCount: number;
  profiles: AudienceProfile[];
  createdAt: string;
}

export interface AudienceProfile {
  id: string;
  name: string;
  age: number;
  gender: 'male' | 'female' | 'other';
  education: string;
  occupation: string;
  income: string;
  location: string;
  avatarUrl?: string;
}

export type AudiencePurpose =
  | 'pricing_analysis'
  | 'product_launch'
  | 'concept_testing'
  | 'positioning'
  | 'market_expansion'
  | 'general_exploration';

export type IncomeLevel = 'low' | 'middle' | 'upper_middle' | 'high';
export type PrecisionLevel = 'general' | 'specific' | 'exact';

// types/survey.ts
export interface Survey {
  id: string;
  projectId: string;
  questions: Question[];
  createdAt: string;
  updatedAt: string;
}

export interface Question {
  id: string;
  type: QuestionType;
  text: string;
  options?: string[];
  scaleMin?: number;
  scaleMax?: number;
  scaleLabels?: { min: string; max: string };
  required: boolean;
  order: number;
}

export type QuestionType =
  | 'single_choice'
  | 'multiple_choice'
  | 'rating_scale'
  | 'open_text'
  | 'ranking';

export interface SurveyPrediction {
  questionId: string;
  confidence: 'low' | 'medium' | 'high';
  predictions: { [option: string]: number };
  meanScore?: number;
  distribution?: string;
}

export interface AISuggestion {
  type: 'question' | 'improvement';
  text: string;
  reasoning: string;
  suggestedQuestion?: Question;
}

export interface BiasWarning {
  questionId: string;
  severity: 'warning' | 'error';
  issue: string;
  suggestion: string;
}
```

---

## Part 5: Implementation Order & Verification Protocol

### Build Sequence

```
Week 1: Foundation
├── Day 1-2: Project setup, design tokens, base components
├── Day 3-4: Layout components (Header, Sidebar)
└── Day 5: Page routing, API client setup

Week 2: Projects Dashboard
├── Day 1-2: Project card component
├── Day 3: Project grid + filters
├── Day 4: Backend integration
└── Day 5: Polish + verification

Week 3: Audiences
├── Day 1: Audience list sidebar
├── Day 2: Audience detail view + table
├── Day 3-4: Create audience form
├── Day 5: Generation flow + loading states

Week 4: Survey Builder
├── Day 1-2: Three-panel layout
├── Day 3: Question builder panel
├── Day 4: Survey preview panel
├── Day 5: Predictions panel

Week 5: AI Features + Polish
├── Day 1-2: AI suggestions + bias detection
├── Day 3: Templates library
├── Day 4: Full integration testing
└── Day 5: Final verification + fixes
```

### Verification Protocol

**For Each Component:**

1. **Before Coding:**
   - Re-read this document's specification
   - Re-examine the Figma screenshot
   - Note any ambiguities to resolve

2. **During Coding:**
   - Match dimensions exactly
   - Use design tokens (no hardcoded values)
   - Implement all states (default, hover, active, disabled)

3. **After Coding:**
   - Screenshot the component
   - Compare side-by-side with Figma
   - Check: colors, spacing, typography, borders, shadows
   - Document any intentional deviations

4. **Sign-Off Checklist:**
   ```
   [ ] Visual match verified
   [ ] Hover states work
   [ ] Responsive behavior correct
   [ ] Accessibility (keyboard nav, aria labels)
   [ ] Data binding works
   [ ] Error states handled
   ```

---

## Part 6: Backend Modifications

### 6.1 New Models to Add

```python
# backend/models/project.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"

class Project(BaseModel):
    id: str
    name: str
    description: str
    status: ProjectStatus = ProjectStatus.DRAFT
    audience_id: Optional[str] = None
    survey_id: Optional[str] = None
    responses_collected: int = 0
    responses_target: int = 0
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
```

```python
# backend/models/audience.py
from pydantic import BaseModel
from typing import List, Optional, Tuple
from datetime import datetime
from enum import Enum

class AudiencePurpose(str, Enum):
    PRICING_ANALYSIS = "pricing_analysis"
    PRODUCT_LAUNCH = "product_launch"
    CONCEPT_TESTING = "concept_testing"
    POSITIONING = "positioning"
    MARKET_EXPANSION = "market_expansion"
    GENERAL_EXPLORATION = "general_exploration"

class IncomeLevel(str, Enum):
    LOW = "low"
    MIDDLE = "middle"
    UPPER_MIDDLE = "upper_middle"
    HIGH = "high"

class AudienceProfile(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    education: str
    occupation: str
    income: str
    location: str
    avatar_url: Optional[str] = None

class Audience(BaseModel):
    id: str
    name: str
    description: str
    purpose: AudiencePurpose
    age_range: Tuple[int, int]
    gender_ratio: dict  # {"male": 30, "female": 70}
    income_level: IncomeLevel
    decision_factors: List[str] = []
    precision: str = "general"
    profile_count: int = 0
    profiles: List[AudienceProfile] = []
    created_at: datetime
```

```python
# backend/models/survey.py
from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum

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
    options: List[str] = []
    scale_min: Optional[int] = None
    scale_max: Optional[int] = None
    scale_labels: Optional[Dict[str, str]] = None
    required: bool = True
    order: int

class Survey(BaseModel):
    id: str
    project_id: str
    questions: List[Question] = []

class SurveyPrediction(BaseModel):
    question_id: str
    confidence: str  # "low", "medium", "high"
    predictions: Dict[str, float]
    mean_score: Optional[float] = None
    distribution: Optional[str] = None
```

### 6.2 New API Routes

```python
# backend/api/projects.py - to be created
# backend/api/audiences.py - to be created
# backend/api/surveys.py - to be created
# backend/api/ai_features.py - to be created
```

---

## Appendix: Screenshot Reference Index

| Screenshot | File Name | Primary Content | Components to Extract |
|------------|-----------|-----------------|----------------------|
| 1 | 4.29.56 PM | Projects Dashboard | Header, Sidebar, Project Cards, Activity Feed |
| 2 | 4.30.16 PM | Projects Dashboard (alt) | Same as above, different data |
| 3 | 4.30.22 PM | Audiences View | Audience List, Detail View, Profiles Table |
| 4 | 4.30.30 PM | Create Audience - Empty | Form Fields, Pills, Slider, Upload Zone |
| 5 | 4.30.36 PM | Create Audience - Generating | Loading Modal, Progress Bar |
| 6 | 4.30.39 PM | Create Audience - Created | Populated Form + Generated Profiles |
| 7 | 4.30.47 PM | Templates - Audiences | Template Cards, Tab Filters |
| 8 | 4.30.52 PM | Templates - Projects | Same structure, different content |
| 9 | 4.30.56 PM | Templates - Scenarios | Same structure, different content |
| 10 | 4.30.59 PM | Survey Builder - Empty | Three Panels, Empty States, Footer |
| 11 | 4.31.04 PM | Survey Builder - Question | Question Form, Preview, Predictions |
| 12 | 4.31.08 PM | Survey Builder - AI | AI Suggestion, Bias Warning, Rating Scale |

---

## Success Criteria

The implementation is complete when:

1. **Visual Parity**: Side-by-side comparison with Figma shows no discernible differences
2. **Functional Completeness**: All user flows work end-to-end
3. **Backend Integration**: Frontend communicates with FastAPI backend
4. **Performance**: Pages load in <2 seconds, interactions feel instant
5. **Responsive**: Works on 1920px, 1440px, 1024px viewport widths
6. **Code Quality**: TypeScript strict mode, no errors, consistent patterns

---

*This document should be referenced before starting each component and used for final verification.*
