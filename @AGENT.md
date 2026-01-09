# RLTX POPULOUS - Agent Instructions

## Project Overview
RLTX Populous is a Decision Intelligence platform that simulates synthetic audiences for market research and strategy testing.

## Directory Structure
```
Populous demo/
├── rltx-populous/           # Python backend
│   ├── backend/
│   │   ├── api/             # FastAPI routes
│   │   ├── engine/          # Simulation engine
│   │   ├── models/          # Pydantic models
│   │   └── data/presets/    # Demo scenarios
│   └── requirements.txt
│
├── populous-frontend/       # Next.js frontend
│   ├── src/
│   │   ├── app/             # Page routes
│   │   ├── components/      # React components
│   │   └── lib/             # Utilities
│   └── package.json
│
├── rltx figma images/       # UI design screenshots
├── docs/                    # Documentation
├── CLAUDE.md                # Master specification
├── PROMPT.md                # Build instructions
└── @fix_plan.md             # Task tracking
```

## Running the Application

### Backend (FastAPI)
```bash
cd rltx-populous
source venv/bin/activate  # If venv exists
pip install -r requirements.txt
python -m backend.run
# or
uvicorn backend.api.main:app --reload --port 8000
```

### Frontend (Next.js)
```bash
cd populous-frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

### Environment Variables
```
# Backend (.env in rltx-populous/)
ANTHROPIC_API_KEY=sk-ant-...

# Frontend (.env.local in populous-frontend/)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing

### Backend Tests
```bash
cd rltx-populous
pytest tests/ -v
```

### Frontend Tests
```bash
cd populous-frontend
npm run test
```

## Key Files to Understand

### Backend
- `backend/api/main.py` - API entry point, all routes
- `backend/engine/runner.py` - Monte Carlo simulation
- `backend/engine/decision_engine.py` - Agent decision logic
- `backend/models/scenario.py` - Market/segment definitions
- `backend/models/agent.py` - Synthetic agent model

### Frontend
- `src/app/(dashboard)/layout.tsx` - Dashboard layout
- `src/components/` - Reusable components
- `src/lib/types.ts` - TypeScript definitions

## API Endpoints (Existing)
- `POST /simulations` - Start simulation
- `GET /simulations/{id}/status` - Check status
- `GET /results/{id}` - Get results
- `POST /compare` - Compare strategies
- `POST /agents/{id}/chat` - Chat with agent

## Build Guidelines

1. **Match Figma**: UI must match screenshots in `/rltx figma images/`
2. **Extend, Don't Break**: Add to existing code, preserve working features
3. **Performance First**: Predictions <500ms, generation <30s
4. **Type Safety**: Use TypeScript strictly in frontend
5. **Error Handling**: All API calls need loading/error states

## Common Tasks

### Add New API Endpoint
1. Add route in `backend/api/main.py` or create new router
2. Add Pydantic models in `backend/models/`
3. Implement logic in `backend/engine/`
4. Test endpoint

### Add New Frontend Component
1. Create in `populous-frontend/src/components/`
2. Follow existing patterns (shadcn/ui + Radix)
3. Use Tailwind for styling
4. Match Figma design

### Add New Demo Scenario
1. Create in `backend/data/presets/`
2. Follow pattern in `b2b_saas.py`
3. Include scenario, segments, competitors, strategies
