# RLTX Populous

**Decision Intelligence Simulation Platform**

Simulate thousands of possible market futures to test go-to-market strategies before you execute them.

## What This Does

- **Monte Carlo Simulation**: Run 200-1000 parallel simulation branches to generate probability distributions
- **Hybrid LLM + Math**: Fast mathematical decisions + LLM for explanations and personas
- **Agent Deep-Dive**: Chat with synthetic buyers to understand their decision reasoning
- **Explainability**: Natural language insights about why strategies win/lose

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env to add your ANTHROPIC_API_KEY

# 4. Run CLI demo
python scripts/demo.py

# 5. Or run API server
python -m backend.run
# Then visit http://localhost:8000/docs
```

## Demo Scenario

**B2B SaaS Product Launch**
- 50,000 potential buyers
- 3 segments: Enterprise, Mid-Market, SMB
- 3 competitors: Monday.com, Asana, Jira
- 3 strategies to compare

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Reflex)                        │
│   Scenario Builder  │  Strategy Config  │  Results  │  Agent Chat│
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API LAYER (FastAPI)                         │
│  POST /scenarios    POST /simulate    POST /compare   /agent-chat│
└───────────────────────────────┬─────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────┐
        ▼                       ▼                   ▼
┌───────────────┐       ┌───────────────┐   ┌───────────────┐
│  MESA ENGINE  │       │   CLAUDE API  │   │   DATA STORE  │
│ • Agents      │       │ • Agent gen   │   │ • Scenarios   │
│ • Scheduler   │       │ • Reasoning   │   │ • Results     │
│ • Batch run   │       │ • Explain     │   │               │
└───────────────┘       └───────────────┘   └───────────────┘
```

## Key Files

| File | Purpose |
|------|---------|
| `backend/engine/runner.py` | Monte Carlo simulation runner |
| `backend/engine/decision_engine.py` | Agent decision logic |
| `backend/engine/agent_factory.py` | Creates synthetic buyers |
| `backend/data/presets/b2b_saas.py` | Demo scenario |
| `backend/api/main.py` | REST API endpoints |
| `scripts/demo.py` | CLI demo |
| `frontend/app.py` | Web UI |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| GET | /scenarios | List scenarios |
| GET | /strategies | List strategies |
| POST | /compare | Compare strategies |
| POST | /agents/{id}/chat | Chat with agent |

## Run Tests

```bash
pytest tests/ -v
```

## Build Log

See `BUILD-LOG.md` for development history and what to build next.
