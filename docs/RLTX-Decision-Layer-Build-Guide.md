# RLTX DECISION LAYER — END-TO-END BUILD GUIDE
## From Prediction Intelligence (Aaru) to Decision Intelligence (RLTX)

---

# PART 1: THE CORE INSIGHT

## What Aaru Does (Prediction Intelligence)

Aaru builds **Layers 03-04** of your stack:
- **Behavioral Models**: LLM-based agents that simulate human decision-making
- **Simulation Engine**: Run thousands of agents across scenarios

**Output**: "Strategy A has 67% chance of success"

**Validation**: 90%+ correlation with traditional surveys (EY study)

**Limitation**: They tell you *what will happen*. They don't tell you *what to do*.

---

## What RLTX Builds (Decision Intelligence)

RLTX builds **Layers 01-05** — the full stack:

```
┌─────────────────────────────────────────────────────────┐
│  05. PREDICTION + EXECUTION (THE DECISION LAYER)        │
│  "Do X by Tuesday. If competitor responds with Y,       │
│   pivot to Z. Approve budget at threshold Q."           │
├─────────────────────────────────────────────────────────┤
│  04. SIMULATION ENGINE                                  │
│  "Branch 10,000 scenarios. Monte Carlo the outcomes."   │
├─────────────────────────────────────────────────────────┤
│  03. BEHAVIORAL MODELS                                  │
│  "Synthetic decision-makers with utility functions"     │
├─────────────────────────────────────────────────────────┤
│  02. OPERATIONAL ONTOLOGY                               │
│  "How decisions actually get made here"                 │
├─────────────────────────────────────────────────────────┤
│  01. DATA FOUNDATION                                    │
│  "Unified causal graph. One source of truth."           │
└─────────────────────────────────────────────────────────┘
```

**Output**: "Execute Strategy A. Specifically: allocate $2.3M to Channel X by March 15. If Competitor B drops price >15% within 30 days, trigger Playbook 7. Approval gate at $500K spend."

**The key difference**:
- Aaru = Analysis → Human decides → Human acts
- RLTX = Analysis → Recommended decision → Approved action → Execution

You're not replacing research. You're replacing the entire decision-making apparatus.

---

## The Gap Aaru Can't Fill

| Dimension | Aaru | RLTX |
|-----------|------|------|
| Stack depth | Layers 03-04 | Layers 01-05 |
| Output | Probability | Decision + Action |
| Validation | Survey correlation | Outcome calibration |
| Multi-agent dynamics | Limited | Full network effects |
| Closed-loop learning | No | Yes (every outcome trains) |
| Defense credibility | No | "Validated in mission" |

**Your wedge**: You don't just predict what will happen. You tell them what to do, why it's optimal, and execute it with audit trails.

---

# PART 2: THE ARCHITECTURE

## Stanford Generative Agents Core (Memory → Reflection → Planning)

From Park et al. (2023), the three critical components:

### 1. Memory Stream
```
- Every perception → stored in memory
- Each memory = {timestamp, description, importance_score}
- Importance = LLM rates "mundane (1) to poignant (10)"
- Grows continuously
```

### 2. Reflection
```
- Triggered when accumulated importance exceeds threshold
- LLM synthesizes: "What are the 3 most salient high-level questions?"
- Generates insights: "Klaus is a dedicated professor who values his research"
- Reflections become new memories (recursive)
```

### 3. Planning
```
- Daily plan generated from reflection + goals
- Hierarchical: Day → Hour → 5-minute chunks
- Reacts to events: plan adjusts when environment changes
```

**For RLTX Decision Layer**: This becomes the "Decision Agent" that:
1. **Observes** the enterprise state (data foundation)
2. **Remembers** what worked before (operational ontology)
3. **Reflects** on patterns across simulations
4. **Plans** the optimal action sequence

---

## Your 5-Layer Technical Architecture

### Layer 01: Data Foundation
**Tech**: Neo4j GraphRAG + Senzing (entity resolution)

```python
# Unified Entity Graph
class EntityGraph:
    """Every entity resolves to single canonical identity"""

    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI)
        self.senzing = G2Engine()

    def resolve_entity(self, source_system, record_id):
        """Cross-system identity resolution"""
        # Senzing fuzzy matches across all data sources
        return self.senzing.getEntityByRecordID(source_system, record_id)

    def get_entity_context(self, entity_id, depth=2):
        """Get full context graph for an entity"""
        query = """
        MATCH (e:Entity {id: $entity_id})-[r*1..$depth]-(connected)
        RETURN e, r, connected
        """
        return self.driver.execute_query(query, entity_id=entity_id, depth=depth)

    def time_travel(self, entity_id, timestamp):
        """Get entity state at any point in time"""
        query = """
        MATCH (e:Entity {id: $entity_id})-[:HAS_STATE]->(s:State)
        WHERE s.valid_from <= $timestamp AND s.valid_to > $timestamp
        RETURN s
        """
        return self.driver.execute_query(query, entity_id=entity_id, timestamp=timestamp)
```

### Layer 02: Operational Ontology
**Tech**: Process mining + LLM extraction

```python
class OperationalOntology:
    """How decisions actually happen here"""

    def __init__(self, anthropic_client):
        self.client = anthropic_client
        self.decision_rules = {}

    def extract_decision_physics(self, historical_decisions: List[Decision]):
        """Extract actual decision patterns from historical data"""

        prompt = f"""
        Analyze these historical decisions and extract:
        1. Authority boundaries - who can approve what
        2. Information dependencies - what data triggers decisions
        3. Trigger conditions - what thresholds matter
        4. Top-performer patterns - what the best decision-makers do differently

        Historical decisions:
        {json.dumps([d.to_dict() for d in historical_decisions])}

        Return as executable logic.
        """

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_rules(response.content[0].text)

    def codify_playbook(self, playbook_description: str):
        """Turn a playbook into executable decision rules"""
        # Convert natural language playbook to code
        pass
```

### Layer 03: Behavioral Models
**Tech**: Mesa + LLM hybrid (Stanford architecture)

```python
from mesa import Agent, Model
from anthropic import Anthropic
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Memory:
    timestamp: float
    description: str
    importance: float  # 1-10
    embedding: Optional[List[float]] = None

@dataclass
class Reflection:
    timestamp: float
    content: str
    source_memories: List[int]  # indices

class GenerativeDecisionAgent(Agent):
    """
    Stanford-style generative agent adapted for enterprise decisions.
    Memory stream + Reflection + Planning architecture.
    """

    def __init__(self, unique_id, model, persona: dict, llm_client: Anthropic):
        super().__init__(unique_id, model)
        self.persona = persona
        self.llm = llm_client

        # Stanford architecture components
        self.memory_stream: List[Memory] = []
        self.reflections: List[Reflection] = []
        self.current_plan: List[str] = []

        # Decision-specific attributes
        self.utility_function = persona.get("utility_function", {})
        self.belief_state = persona.get("initial_beliefs", {})
        self.constraints = persona.get("constraints", [])

        # Thresholds
        self.reflection_threshold = 100  # Accumulated importance before reflection
        self.accumulated_importance = 0

    def perceive(self, observation: str):
        """Add observation to memory stream"""
        importance = self._rate_importance(observation)

        memory = Memory(
            timestamp=self.model.current_time,
            description=observation,
            importance=importance
        )
        self.memory_stream.append(memory)
        self.accumulated_importance += importance

        # Trigger reflection if threshold exceeded
        if self.accumulated_importance >= self.reflection_threshold:
            self._reflect()
            self.accumulated_importance = 0

    def _rate_importance(self, observation: str) -> float:
        """LLM rates importance 1-10"""
        prompt = f"""
        On a scale of 1-10, rate the importance of this observation
        for a {self.persona['role']} making {self.persona['decision_domain']} decisions.

        1 = mundane, routine
        10 = critical, requires immediate attention

        Observation: {observation}

        Return only the number.
        """
        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": prompt}]
        )
        return float(response.content[0].text.strip())

    def _reflect(self):
        """Generate higher-level insights from recent memories"""
        recent_memories = self.memory_stream[-50:]  # Last 50 memories

        prompt = f"""
        Based on these recent observations, generate 3 high-level insights
        that a {self.persona['role']} would derive:

        Observations:
        {chr(10).join([m.description for m in recent_memories])}

        Format: One insight per line.
        """

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        for insight in response.content[0].text.strip().split('\n'):
            reflection = Reflection(
                timestamp=self.model.current_time,
                content=insight,
                source_memories=list(range(len(self.memory_stream)-50, len(self.memory_stream)))
            )
            self.reflections.append(reflection)

            # Reflections become memories too (recursive)
            self.perceive(f"[Reflection] {insight}")

    def retrieve_relevant_context(self, query: str, k: int = 20) -> List[Memory]:
        """Retrieve memories by recency + importance + relevance"""
        # In production: use embeddings for relevance
        # For MVP: recency * importance scoring

        scored = []
        for i, mem in enumerate(self.memory_stream):
            recency_score = 1.0 / (1 + (self.model.current_time - mem.timestamp))
            importance_score = mem.importance / 10.0
            # relevance_score would come from embedding similarity

            total_score = 0.5 * recency_score + 0.3 * importance_score + 0.2 * 1.0
            scored.append((total_score, mem))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [mem for _, mem in scored[:k]]

    def plan(self, goal: str) -> List[str]:
        """Generate action plan given current state and goal"""
        relevant_memories = self.retrieve_relevant_context(goal)
        recent_reflections = self.reflections[-10:]

        prompt = f"""
        You are a {self.persona['role']} at {self.persona['organization']}.

        Your goal: {goal}

        Your utility function (what you optimize for):
        {json.dumps(self.utility_function)}

        Your constraints:
        {json.dumps(self.constraints)}

        Relevant context from memory:
        {chr(10).join([m.description for m in relevant_memories])}

        Recent reflections:
        {chr(10).join([r.content for r in recent_reflections])}

        Generate a step-by-step action plan. Be specific about:
        - What to do
        - When to do it
        - What would trigger a plan change

        Format: Numbered steps.
        """

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        self.current_plan = response.content[0].text.strip().split('\n')
        return self.current_plan

    def decide(self, options: List[dict]) -> dict:
        """Make a decision given options"""
        relevant_memories = self.retrieve_relevant_context(str(options))

        prompt = f"""
        You are a {self.persona['role']} making a decision.

        Options:
        {json.dumps(options, indent=2)}

        Your utility function:
        {json.dumps(self.utility_function)}

        Your constraints:
        {json.dumps(self.constraints)}

        Your current beliefs:
        {json.dumps(self.belief_state)}

        Relevant past experience:
        {chr(10).join([m.description for m in relevant_memories])}

        Choose the option that maximizes your utility given constraints.
        Explain your reasoning, then state your choice.

        Format:
        REASONING: [your reasoning]
        CHOICE: [option index]
        CONFIDENCE: [0-1]
        """

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_decision(response.content[0].text, options)

    def update_beliefs(self, evidence: dict):
        """Bayesian update on beliefs given new evidence"""
        prompt = f"""
        Current beliefs: {json.dumps(self.belief_state)}
        New evidence: {json.dumps(evidence)}

        Update the beliefs based on this evidence.
        Return updated beliefs as JSON.
        """

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        self.belief_state = json.loads(response.content[0].text)

    def step(self):
        """Mesa step function"""
        # Execute current plan step
        if self.current_plan:
            current_action = self.current_plan.pop(0)
            self.perceive(f"Executed: {current_action}")
```

### Layer 04: Simulation Engine
**Tech**: Mesa with parallel Monte Carlo

```python
from mesa import Model
from mesa.time import RandomActivation
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import numpy as np

class DecisionSimulation(Model):
    """
    Monte Carlo simulation across branching futures.
    """

    def __init__(self, scenario: dict, strategy: dict, num_agents: int = 1000):
        super().__init__()
        self.scenario = scenario
        self.strategy = strategy
        self.schedule = RandomActivation(self)
        self.current_time = 0
        self.event_log = []

        # Create agents
        self._create_agents(num_agents)

    def _create_agents(self, num_agents: int):
        """Create population of decision agents"""
        llm = Anthropic()

        for i in range(num_agents):
            segment = self._sample_segment()
            persona = self._generate_persona(segment)
            agent = GenerativeDecisionAgent(i, self, persona, llm)
            self.schedule.add(agent)

    def inject_intervention(self, intervention: dict):
        """Inject an event into the simulation"""
        for agent in self.schedule.agents:
            agent.perceive(intervention['description'])
        self.event_log.append({
            'time': self.current_time,
            'intervention': intervention
        })

    def step(self):
        """Advance simulation by one time step"""
        self.current_time += 1
        self.schedule.step()

    def run(self, steps: int) -> dict:
        """Run simulation for n steps"""
        for _ in range(steps):
            self.step()
        return self._collect_results()

    def _collect_results(self) -> dict:
        """Aggregate results across all agents"""
        decisions = []
        for agent in self.schedule.agents:
            decisions.append({
                'agent_id': agent.unique_id,
                'final_beliefs': agent.belief_state,
                'decision_log': agent.memory_stream[-10:],  # Last 10 memories
                'reflections': agent.reflections
            })
        return {
            'scenario': self.scenario,
            'strategy': self.strategy,
            'agent_outcomes': decisions,
            'event_log': self.event_log
        }


def run_monte_carlo(scenario: dict, strategy: dict, num_branches: int = 1000) -> dict:
    """
    Run Monte Carlo simulation across multiple branches.
    Each branch has different random seeds → different emergent behavior.
    """

    def run_branch(seed: int) -> dict:
        np.random.seed(seed)
        model = DecisionSimulation(scenario, strategy, num_agents=100)
        return model.run(steps=90)  # 90 days

    # Parallel execution
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(run_branch, range(num_branches)))

    return aggregate_monte_carlo_results(results)


def aggregate_monte_carlo_results(branch_results: List[dict]) -> dict:
    """
    Aggregate across Monte Carlo branches into probability distributions.
    """
    # Extract outcomes from each branch
    outcomes = []
    for result in branch_results:
        # Calculate key metrics per branch
        outcome = calculate_branch_outcome(result)
        outcomes.append(outcome)

    # Build distributions
    return {
        'win_probability': np.mean([o['win'] for o in outcomes]),
        'outcome_distribution': np.histogram([o['revenue'] for o in outcomes], bins=50),
        'sensitivity_analysis': calculate_sensitivity(outcomes),
        'branch_details': outcomes
    }
```

### Layer 05: Prediction + Execution (THE DECISION LAYER)
**This is what makes you different from Aaru.**

```python
class DecisionLayer:
    """
    The layer that turns predictions into decisions.
    This is the RLTX differentiation.
    """

    def __init__(self,
                 data_foundation: EntityGraph,
                 ontology: OperationalOntology,
                 simulation_engine,
                 llm_client: Anthropic):
        self.data = data_foundation
        self.ontology = ontology
        self.sim = simulation_engine
        self.llm = llm_client

    def compute_optimal_decision(self,
                                  decision_context: dict,
                                  options: List[dict],
                                  constraints: dict) -> dict:
        """
        The core function: Given context and options, return the optimal decision
        with full explainability and execution plan.
        """

        # 1. Get current state from data foundation
        current_state = self.data.get_entity_context(
            decision_context['focal_entity'],
            depth=3
        )

        # 2. Get relevant decision rules from ontology
        decision_rules = self.ontology.get_rules_for_context(decision_context)

        # 3. Run Monte Carlo simulation for each option
        option_results = {}
        for option in options:
            results = run_monte_carlo(
                scenario=decision_context,
                strategy=option,
                num_branches=1000
            )
            option_results[option['id']] = results

        # 4. Rank options by expected utility
        rankings = self._rank_by_utility(option_results, constraints)

        # 5. Generate execution plan for top option
        optimal_option = rankings[0]
        execution_plan = self._generate_execution_plan(
            optimal_option,
            decision_rules,
            constraints
        )

        # 6. Identify contingencies (what-if triggers)
        contingencies = self._identify_contingencies(
            option_results,
            optimal_option
        )

        return {
            'recommended_decision': optimal_option,
            'confidence': rankings[0]['confidence'],
            'explanation': self._generate_explanation(rankings, option_results),
            'execution_plan': execution_plan,
            'contingencies': contingencies,
            'approval_gates': self._get_approval_gates(execution_plan, decision_rules),
            'audit_trail': self._build_audit_trail(decision_context, option_results)
        }

    def _generate_execution_plan(self, decision: dict, rules: dict, constraints: dict) -> List[dict]:
        """
        Turn a decision into specific, timed actions.
        This is what Aaru doesn't do.
        """
        prompt = f"""
        You are generating an execution plan for this decision:
        {json.dumps(decision)}

        Decision rules for this organization:
        {json.dumps(rules)}

        Constraints:
        {json.dumps(constraints)}

        Generate a specific, timed action plan with:
        1. Exact actions (not vague recommendations)
        2. Specific dates/times
        3. Responsible parties
        4. Approval gates
        5. Contingency triggers ("if X happens, do Y")

        Format as JSON array of actions.
        """

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(response.content[0].text)

    def _identify_contingencies(self, results: dict, chosen: dict) -> List[dict]:
        """
        Identify what would cause the decision to change.
        Critical for enterprise trust.
        """

        # Find scenarios where chosen option loses
        losing_scenarios = []
        for branch in results[chosen['id']]['branch_details']:
            if not branch['win']:
                losing_scenarios.append(branch)

        # Cluster losing scenarios by root cause
        prompt = f"""
        These are scenarios where the recommended strategy fails:
        {json.dumps(losing_scenarios[:20])}  # Sample

        Identify the 3-5 most common causes of failure.
        For each, specify:
        1. The trigger condition (what would we observe?)
        2. The alternative action (what should we do instead?)
        3. The detection method (how do we know it's happening?)

        Format as JSON.
        """

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(response.content[0].text)

    def _generate_explanation(self, rankings: List[dict], results: dict) -> str:
        """
        Generate board-ready, regulator-acceptable explanation.
        Not a black box.
        """

        prompt = f"""
        Generate an explanation for why this decision is optimal:

        Recommended: {rankings[0]['option']['name']}
        Alternatives considered: {[r['option']['name'] for r in rankings[1:]]}

        Key simulation results:
        - Win probability: {results[rankings[0]['option']['id']]['win_probability']:.1%}
        - Expected outcome range: {results[rankings[0]['option']['id']]['outcome_distribution']}

        Write an explanation that:
        1. A board member would trust
        2. A regulator would accept
        3. Shows the reasoning clearly
        4. Acknowledges uncertainty appropriately

        Keep it under 300 words.
        """

        response = self.llm.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def execute_and_learn(self, decision_id: str, actual_outcome: dict):
        """
        Closed-loop learning: Compare predicted vs actual, update models.
        This is how the system compounds.
        """

        # Get original prediction
        prediction = self.decision_store.get(decision_id)

        # Calculate prediction error
        error = self._calculate_error(prediction, actual_outcome)

        # Update behavioral models
        self._update_agent_parameters(error)

        # Update ontology rules
        self._update_decision_rules(prediction, actual_outcome)

        # Log for audit
        self.audit_log.append({
            'decision_id': decision_id,
            'predicted': prediction,
            'actual': actual_outcome,
            'error': error,
            'model_updates': self._get_model_diff()
        })
```

---

# PART 3: THE BUILD SEQUENCE

## What to Build First (MVP in 4 Weeks)

### Week 1: Foundation
- [ ] Set up project structure
- [ ] Implement basic `GenerativeDecisionAgent` with memory stream
- [ ] Simple Mesa model with 100 agents
- [ ] Test: Can agents remember, reflect, plan?

### Week 2: Simulation
- [ ] Monte Carlo branching
- [ ] Parallel execution
- [ ] Results aggregation
- [ ] Test: Can we get probability distributions?

### Week 3: Decision Layer
- [ ] Execution plan generation
- [ ] Contingency identification
- [ ] Explanation generation
- [ ] Test: Can we output actionable decisions?

### Week 4: Demo
- [ ] FastAPI endpoints
- [ ] Simple frontend (Streamlit or Reflex)
- [ ] Pre-built scenario
- [ ] Test: Can we show it to a customer?

---

# PART 4: HOW TO USE AGENTIC CODING (RALPH MODE)

## The "Socratic Mode" Approach

From the screenshot you shared — this is the key insight:

> "Instead of just telling the agent what to do, start with questions that force it to load the right files and understand the abstractions."

### For Letta / Claude Code:

**DON'T DO THIS:**
```
Build me a decision intelligence platform with behavioral agents
```

**DO THIS:**
```
Phase 1: Understanding
- What is the Stanford generative agents architecture? Read the paper.
- What are the three core components (memory, reflection, planning)?
- How does Mesa work for agent-based modeling?
- What makes Aaru's approach work (90% survey correlation)?

Phase 2: Architecture
- Given those components, how would you structure a Python project?
- What are the key classes and their relationships?
- Where does the LLM integration happen?
- How does Monte Carlo branching work?

Phase 3: Implementation
- Now build the GenerativeDecisionAgent class
- Add the memory stream
- Add reflection (triggered by accumulated importance)
- Add planning

Phase 4: Testing
- Run 100 agents for 10 time steps
- Do they exhibit emergent behavior?
- Do the reflections make sense?
```

### The Exact Prompts to Use

**Initial Context Load:**
```
I'm building a Decision Intelligence platform called RLTX. The goal is to go
one step beyond Aaru (which does prediction/simulation) to actually output
optimal decisions with execution plans.

The core architecture is:
1. Data Foundation (Neo4j knowledge graph)
2. Operational Ontology (how decisions happen here)
3. Behavioral Models (Stanford generative agents)
4. Simulation Engine (Mesa + Monte Carlo)
5. Decision Layer (execution plans, contingencies, explanations)

Before building anything, help me understand:
- How does Stanford's memory stream architecture work?
- What makes their reflection mechanism trigger?
- How do you scale this to 10,000 agents?
```

**After understanding:**
```
Now let's build the GenerativeDecisionAgent class.

Requirements:
- Must have memory stream (list of Memory objects)
- Must have reflection (triggered at importance threshold)
- Must have planning (multi-step action generation)
- Must integrate with Anthropic API for LLM reasoning
- Must be compatible with Mesa's Agent interface

Start with the class structure, then implement each method.
```

**For iteration:**
```
The agent works but reflection is triggering too often.
Looking at the Stanford paper, they use accumulated importance.
Let's adjust the threshold logic.

Also, the plans are too vague. The Stanford agents plan at
hour-level granularity. Let's add hierarchical planning.
```

---

# PART 5: THE DEMO SCENARIO

## Pre-Built Demo: PE Portfolio AI Rollout

**Scenario**: Vista Equity-style fund deciding how to deploy AI across 50 portfolio companies.

**Agents**:
- 500 CIOs (decision-makers at portcos)
- 50 AI vendors (competing for implementations)
- 10 Operating Partners (fund-level decision-makers)

**Decision being simulated**: "Should we mandate AI adoption top-down or let portcos self-select?"

**Output**:
```json
{
  "recommended_decision": "Hybrid approach with incentives",
  "confidence": 0.73,
  "execution_plan": [
    {
      "action": "Announce AI transformation initiative at Q1 portfolio meeting",
      "date": "2025-02-15",
      "responsible": "CTO Operating Partner",
      "approval_required": false
    },
    {
      "action": "Deploy Context Layer to top 5 performing portcos",
      "date": "2025-03-01 to 2025-04-15",
      "responsible": "AI Platform Team",
      "budget": "$250K per portco",
      "approval_required": true,
      "approval_gate": "$500K cumulative"
    },
    {
      "action": "Launch incentive program: EBITDA boost linked to AI adoption",
      "date": "2025-04-01",
      "responsible": "Value Creation Team",
      "contingency": "If <30% adoption by June, switch to mandate"
    }
  ],
  "contingencies": [
    {
      "trigger": "Competitor fund announces aggressive AI mandate",
      "detection": "Monitor Apollo, Thoma Bravo PR",
      "response": "Accelerate timeline by 6 weeks"
    },
    {
      "trigger": "Top portco CIO resigns citing AI concerns",
      "detection": "HR flagging",
      "response": "Pause deployment, conduct sentiment survey"
    }
  ],
  "explanation": "Simulation across 1,000 scenarios shows hybrid approach wins 73% of cases. Pure mandate risks talent attrition (23% of CIOs indicated resistance in agent interviews). Pure self-selection results in only 34% adoption by EOY. Incentive-linked hybrid achieves 67% adoption while maintaining CIO satisfaction above 0.7 threshold..."
}
```

---

# PART 6: FILE STRUCTURE

```
rltx/
├── README.md
├── requirements.txt
├── .env.example
│
├── core/
│   ├── __init__.py
│   ├── data_foundation.py      # Layer 01 - Neo4j + Senzing
│   ├── ontology.py             # Layer 02 - Decision rules
│   ├── agents.py               # Layer 03 - GenerativeDecisionAgent
│   ├── simulation.py           # Layer 04 - Mesa + Monte Carlo
│   └── decision_layer.py       # Layer 05 - The differentiator
│
├── api/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── routes/
│   │   ├── scenarios.py
│   │   ├── simulations.py
│   │   └── decisions.py
│   └── schemas/
│       └── models.py           # Pydantic models
│
├── frontend/
│   └── app.py                  # Reflex or Streamlit
│
├── demos/
│   ├── pe_portfolio_rollout.json
│   ├── product_launch.json
│   └── pricing_decision.json
│
└── tests/
    ├── test_agents.py
    ├── test_simulation.py
    └── test_decision_layer.py
```

---

# PART 7: THE PROMPT TO GIVE YOUR CODING AGENT

Copy this entire prompt and paste it into Claude Code / Letta / Cursor:

```
# MISSION

Build RLTX Decision Layer - a platform that goes beyond prediction intelligence
(what Aaru does) to decision intelligence (recommending and executing optimal
decisions).

# CONTEXT

I have uploaded a detailed architecture document. Read it first.

The core insight: Aaru tells you "Strategy A has 67% chance of success."
We tell you "Execute Strategy A. Do X by Tuesday. If competitor does Y, pivot to Z."

# ARCHITECTURE

5 layers:
1. Data Foundation - Neo4j knowledge graph with entity resolution
2. Operational Ontology - How decisions actually happen here
3. Behavioral Models - Stanford generative agents (memory + reflection + planning)
4. Simulation Engine - Mesa + Monte Carlo
5. Decision Layer - Execution plans, contingencies, explanations

# BUILD ORDER

1. FIRST: Understand Stanford generative agents architecture
   - Read about memory stream
   - Read about reflection mechanism
   - Read about planning

2. THEN: Build GenerativeDecisionAgent class
   - Mesa Agent subclass
   - Memory stream implementation
   - Reflection triggered by accumulated importance
   - Planning with hierarchical granularity

3. THEN: Build simulation engine
   - Monte Carlo branching
   - Parallel execution
   - Results aggregation

4. THEN: Build decision layer
   - Optimal decision computation
   - Execution plan generation
   - Contingency identification
   - Explanation generation

5. FINALLY: API and frontend
   - FastAPI endpoints
   - Simple Streamlit demo

# KEY TECHNOLOGIES

- Mesa (agent-based modeling)
- Anthropic Claude API (LLM reasoning)
- Neo4j (knowledge graph)
- FastAPI (API)
- Pydantic (schemas)

# SUCCESS CRITERIA

The demo should:
1. Show 1000 agents making decisions
2. Output probability distributions
3. Recommend an optimal decision
4. Generate a specific execution plan with dates
5. Identify contingencies
6. Explain the reasoning

Start by examining the architecture document, then build step by step.
Ask clarifying questions before implementing.
```

---

# SUMMARY

**The gap you're filling:**
- Aaru = "What will probably happen" → Layers 03-04
- RLTX = "What you should do, exactly" → Layers 01-05

**The technical edge:**
- Full Stanford architecture (memory + reflection + planning)
- Closed-loop learning (outcomes train the model)
- Execution plans, not just predictions
- Audit trails for regulators
- Defense-grade credibility

**The build path:**
- Use Socratic prompting with coding agents
- Force understanding before implementation
- Build incrementally with tests
- Demo in 4 weeks

**The demo:**
- PE portfolio AI rollout scenario
- 500+ agents, 1000 Monte Carlo branches
- Output: Decision + Execution Plan + Contingencies + Explanation

This is what makes you worth a billion dollars. Aaru does predictions.
You do decisions.
