# RLTX BUILD PROMPTS FOR AGENTIC CODING
## Socratic Sequence for Letta (Ralph Mode) / Claude Code / Cursor

---

## THE SOCRATIC APPROACH (From Your Screenshot)

The key insight from the viral tweet you saved:

> "The most productive users start with questions that force the agent to load the right files and understand the abstractions. They keep going until both they AND the agent understand the shape of the problem."

**This is the difference between slop and production code.**

---

## PHASE 1: CONTEXT LOADING

### Prompt 1.1 — Understanding the Landscape

```
Before we build anything, I need you to understand the competitive landscape
and technical foundations.

TASK: Research and summarize the following:

1. AARU (aaru.com)
   - What do they do?
   - What's their technical approach?
   - What's their limitation?

2. STANFORD GENERATIVE AGENTS (Park et al. 2023)
   - What's the memory stream?
   - What triggers reflection?
   - How does planning work?

3. MESA (Python agent-based modeling)
   - How do agents step?
   - How does the scheduler work?
   - How do you collect data?

Don't write code yet. Just summarize what you learn.
```

### Prompt 1.2 — Clarifying the Gap

```
Good. Now let me explain what we're building.

AARU does:
- Behavioral Models (synthetic decision-makers)
- Simulation Engine (run scenarios)
- OUTPUT: "Strategy A has 67% probability of success"

WE DO:
- Everything Aaru does, PLUS:
- Data Foundation (unified knowledge graph)
- Operational Ontology (how decisions happen at THIS org)
- Decision Layer (execution plans)
- OUTPUT: "Execute Strategy A. Do X by Tuesday. If Y happens, pivot to Z."

The key differentiator: We don't just predict. We DECIDE.

Questions before we continue:
1. What's unclear about this distinction?
2. What technical challenges do you foresee?
3. What should we build first?
```

---

## PHASE 2: ARCHITECTURE DESIGN

### Prompt 2.1 — Data Models

```
Let's design the data models before any implementation.

We need schemas for:

1. Memory (Stanford architecture)
   - timestamp
   - description
   - importance score (1-10)
   - embedding (optional)

2. Reflection
   - timestamp
   - content (the insight)
   - source_memory_indices

3. Agent
   - persona (dict)
   - memory_stream (List[Memory])
   - reflections (List[Reflection])
   - current_plan (List[str])
   - utility_function (what they optimize for)
   - belief_state (dict)
   - constraints (List)

4. Simulation
   - scenario (market/context)
   - strategy (what we're testing)
   - agents (List[Agent])
   - event_log

5. Decision (THE OUTPUT)
   - recommended_option
   - confidence
   - execution_plan (List[Action])
   - contingencies (List[Contingency])
   - explanation (str)
   - audit_trail

Write Pydantic models for all of these. Don't implement logic yet.
```

### Prompt 2.2 — Class Structure

```
Now design the class structure. No implementation, just signatures.

class GenerativeDecisionAgent(Agent):
    """Stanford-style generative agent for enterprise decisions"""

    def __init__(self, unique_id, model, persona, llm_client): ...

    def perceive(self, observation: str) -> None:
        """Add observation to memory stream"""

    def _rate_importance(self, observation: str) -> float:
        """LLM rates 1-10"""

    def _reflect(self) -> None:
        """Generate higher-level insights"""

    def retrieve_relevant_context(self, query: str, k: int = 20) -> List[Memory]:
        """Memory retrieval by recency + importance + relevance"""

    def plan(self, goal: str) -> List[str]:
        """Generate action plan"""

    def decide(self, options: List[dict]) -> dict:
        """Choose optimal option given utility function"""

    def update_beliefs(self, evidence: dict) -> None:
        """Bayesian belief update"""

    def step(self) -> None:
        """Mesa step function"""

class DecisionSimulation(Model):
    """Monte Carlo simulation across branching futures"""

    def __init__(self, scenario, strategy, num_agents): ...
    def inject_intervention(self, intervention: dict) -> None: ...
    def step(self) -> None: ...
    def run(self, steps: int) -> dict: ...

class DecisionLayer:
    """The RLTX differentiator - turns predictions into decisions"""

    def compute_optimal_decision(self, context, options, constraints) -> dict: ...
    def _generate_execution_plan(self, decision, rules, constraints) -> List[dict]: ...
    def _identify_contingencies(self, results, chosen) -> List[dict]: ...
    def _generate_explanation(self, rankings, results) -> str: ...
    def execute_and_learn(self, decision_id, actual_outcome) -> None: ...

Does this structure make sense? What's missing?
```

---

## PHASE 3: IMPLEMENTATION (Iterative)

### Prompt 3.1 — Memory Stream

```
Let's implement the memory stream first. This is foundational.

REQUIREMENTS:
1. Every perception gets stored
2. Each memory has: timestamp, description, importance
3. Importance is rated by LLM (1-10 scale)
4. Memories can be retrieved by recency + importance + relevance

IMPLEMENTATION NOTES:
- Use Anthropic Claude API for importance rating
- Keep prompts minimal (this will be called frequently)
- For MVP, skip embeddings (use keyword matching for relevance)

Write the Memory dataclass and the perceive() + _rate_importance() methods.
Include error handling.
```

### Prompt 3.2 — Reflection

```
Now implement reflection. This is what makes agents coherent over time.

FROM STANFORD PAPER:
- Reflection triggers when accumulated importance exceeds threshold
- Default threshold: 100 (sum of importance scores)
- Reflection asks: "What are the 3 most salient high-level questions?"
- Outputs insights that become new memories (recursive)

IMPLEMENTATION:
1. Track accumulated_importance since last reflection
2. When threshold exceeded, call _reflect()
3. _reflect() summarizes recent memories into insights
4. Each insight becomes a new memory with [Reflection] prefix
5. Reset accumulated_importance to 0

Write the _reflect() method. Test with a simple scenario.
```

### Prompt 3.3 — Planning

```
Now implement planning. Agents need to generate action sequences.

FROM STANFORD PAPER:
- Plans are hierarchical: Day → Hour → 5-minute chunks
- Plans are generated from: persona + reflections + current state
- Plans adapt when environment changes

FOR RLTX:
- Plans are more specific: actual actions with dates
- Plans include contingencies: "if X happens, do Y"
- Plans include approval gates: "requires approval if > $threshold"

Write the plan() method. Test by giving an agent a goal and seeing the output.
```

### Prompt 3.4 — Monte Carlo

```
Now let's make it scale. We need to run 1000+ branches in parallel.

REQUIREMENTS:
1. Fork simulation state at decision points
2. Each branch has different random seed → different emergent behavior
3. Run branches in parallel (ProcessPoolExecutor)
4. Aggregate results into probability distributions

IMPLEMENTATION:
1. run_monte_carlo(scenario, strategy, num_branches=1000)
2. Each branch: create model, run N steps, collect results
3. Aggregate: win rates, outcome distributions, sensitivity analysis

Write the Monte Carlo runner. Test with 100 branches.
```

### Prompt 3.5 — Decision Layer

```
This is the differentiator. Aaru stops at simulation. We go further.

THE DECISION LAYER MUST:
1. Run simulations for each option
2. Rank options by expected utility
3. Generate execution plan for winner
4. Identify contingencies (what would change the decision)
5. Generate board-ready explanation
6. Create audit trail

IMPLEMENTATION:
1. compute_optimal_decision() orchestrates everything
2. _generate_execution_plan() turns decision into specific actions
3. _identify_contingencies() finds scenarios where decision fails
4. _generate_explanation() creates trustworthy narrative

Write DecisionLayer class. Test with a simple A/B decision.
```

---

## PHASE 4: INTEGRATION & TESTING

### Prompt 4.1 — End-to-End Test

```
Let's test the full pipeline.

SCENARIO: B2B SaaS Product Launch
- 500 synthetic buyers (3 segments: Enterprise, Mid-Market, SMB)
- 3 competitors (Monday, Asana, Jira style)
- 3 strategies to compare

TEST:
1. Create 500 agents with varied personas
2. Run 100 Monte Carlo branches per strategy
3. Output: Which strategy wins? Why?
4. Output: Execution plan for winning strategy
5. Output: Contingencies

Run this and show me the output.
```

### Prompt 4.2 — Agent Interview

```
From Stanford paper: You can "interview" agents to verify believability.

IMPLEMENT:
1. After simulation, select random agent
2. Allow user to ask questions in natural language
3. Agent responds in character, referencing their memories

This is our killer demo feature. Prospects can literally talk to their
synthetic customers.

Add an agent_chat() method. Test by interviewing an agent about their
purchase decision.
```

---

## PHASE 5: DEMO POLISH

### Prompt 5.1 — API

```
Wrap everything in FastAPI.

ENDPOINTS:
- POST /scenarios - Create new scenario
- POST /strategies - Create strategy to test
- POST /simulate - Run simulation
- GET /results/{id} - Get simulation results
- POST /decisions - Get optimal decision
- POST /agents/{id}/chat - Interview an agent

Use Pydantic for request/response schemas.
Add proper error handling.
```

### Prompt 5.2 — Frontend

```
Create a simple demo UI.

OPTIONS:
- Streamlit (fastest)
- Reflex (pure Python, nicer)

PAGES:
1. Scenario Builder - Define market, segments, competitors
2. Strategy Comparison - Side-by-side simulation results
3. Decision Output - Execution plan, contingencies, explanation
4. Agent Explorer - Browse and interview synthetic buyers

Build in Streamlit for speed. We can upgrade later.
```

---

## PHASE 6: THE DEMO SCRIPT

### Prompt 6.1 — Pre-Built Scenario

```
Create a compelling demo scenario for PE Operating Partners.

SCENARIO: "AI Rollout Decision for Software Portfolio"

CONTEXT:
- Fund has 50 portfolio companies
- Deciding: Mandate AI adoption OR Let portcos self-select OR Hybrid

AGENTS:
- 500 CIOs at portfolio companies
- 50 AI vendors
- 10 Operating Partners

SEGMENTS:
- High performers (top quartile EBITDA)
- Mid performers
- Turnaround situations

STRATEGIES:
1. Full Mandate - Everyone adopts by Q4
2. Self-Select - Incentives but no requirement
3. Hybrid - Top performers first, then cascade

Create this scenario with realistic agent personas.
```

### Prompt 6.2 — Demo Flow

```
Write the word-for-word demo script.

STRUCTURE (10 minutes):
1. "Here's the decision Vista is actually facing" (show scenario)
2. "These are the 500 CIOs making adoption decisions" (show agents)
3. "Let's simulate all three strategies" (run simulation)
4. "Strategy 3 wins 73% of the time. Here's why." (show results)
5. "Here's the execution plan" (show decision output)
6. "Let's interview a CIO who resisted" (agent chat)
7. "This is what decision intelligence looks like."

Write transitions and key phrases to use.
```

---

## DEBUGGING PROMPTS

### When agents aren't coherent:
```
The agent's responses don't feel coherent over time.
Looking at the memory stream, it seems like retrieval is pulling irrelevant memories.

Let's debug the retrieve_relevant_context() method.
Show me the scoring for a specific query across all memories.
Where is relevance failing?
```

### When simulation is too slow:
```
Monte Carlo with 1000 branches takes 15 minutes. Too slow for demo.

Options:
1. Reduce LLM calls (pre-generate personas, batch API calls)
2. Hybrid approach (LLM for 100 agents, math for 900)
3. Caching (reuse agent decisions for similar scenarios)

Which approach makes most sense? Implement it.
```

### When explanations aren't trustworthy:
```
The generated explanations sound generic. Boards won't trust this.

Requirements for trustworthy explanation:
1. Specific numbers, not vague claims
2. References to actual simulation data
3. Acknowledgment of uncertainty
4. Clear comparison to alternatives

Rewrite _generate_explanation() with these constraints.
```

---

## THE ULTIMATE RALPH MODE PROMPT

Copy this entire block into Letta/Claude Code to start:

```
/ralph

I'm building RLTX Decision Layer.

CONTEXT:
- Aaru does prediction intelligence (90% survey correlation, $1B valuation)
- We do decision intelligence (predictions → decisions → execution plans)
- The gap: Aaru tells you probabilities. We tell you what to do.

ARCHITECTURE:
1. Data Foundation - Knowledge graph
2. Operational Ontology - Decision rules
3. Behavioral Models - Stanford generative agents (memory + reflection + planning)
4. Simulation Engine - Mesa + Monte Carlo
5. Decision Layer - THE DIFFERENTIATOR

BUILD ORDER:
1. Understand Stanford generative agents architecture
2. Build GenerativeDecisionAgent class
3. Build Monte Carlo simulation
4. Build Decision Layer
5. Wrap in API + simple frontend

SUCCESS CRITERIA:
Demo shows:
- 1000 agents making decisions
- Probability distributions
- Optimal decision recommendation
- Specific execution plan with dates
- Contingencies
- Board-ready explanation

START BY:
1. Asking me clarifying questions
2. Confirming you understand the Stanford architecture
3. Proposing a file structure
4. Building incrementally with tests

Begin.
```

---

## NOTES ON USING LETTA SPECIFICALLY

From the screenshots you shared:

### Ralph Mode Basics
- `/ralph` - Start Ralph mode (infinite loop until task complete)
- `/yolo-ralph` - More aggressive (fewer confirmations)
- `shift+tab` - Exit Ralph mode

### Letta Features
- `/pin` - Save + name your agent
- `/init` - Initialize agent's memory
- `/remember` - Teach your agent
- `/agents` - List agents
- `/ade` - Open in browser

### Teleportation
```
letta --agent <agent-id>
```
Teleport an agent to where you are. Useful for continuing work across sessions.

### Best Practices
1. **Start with context** - Upload this build guide first
2. **Use Socratic mode** - Force understanding before implementation
3. **Test incrementally** - Run after each major component
4. **Save checkpoints** - `/pin` when something works

---

That's it. This is how you build a billion-dollar Decision Intelligence platform
using agentic coding tools.

The key: Don't tell the agent what to build. Make it understand WHY first.
Then watch it ralph through the implementation.
