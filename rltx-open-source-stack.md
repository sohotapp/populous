# RLTX Open Source Stack Reference

## Quick Picks by Layer

| Layer | Tool | Why | Install |
|-------|------|-----|---------|
| **Data Foundation** | Neo4j Aura (free) | Best graph DB, good Python SDK | Cloud hosted |
| **Entity Resolution** | Senzing | Open source ER, proven at scale | `pip install senzing` |
| **Behavioral Models** | Mesa 3.4 | ABM standard, 11 years mature | `pip install mesa[rec]` |
| **LLM Reasoning** | Claude API | Best reasoning, your stack | `pip install anthropic` |
| **Simulation Viz** | Plotly/Altair | Interactive, works with Reflex | `pip install plotly altair` |
| **Frontend** | Reflex | Pure Python, ships fast | `pip install reflex` |
| **API** | FastAPI | Industry standard, async | `pip install fastapi uvicorn` |

---

## Key Open Source Projects

### Mesa 3.4 (Agent-Based Modeling)
**GitHub:** github.com/mesa/mesa
**Docs:** mesa.readthedocs.io

What it gives you:
- Agent lifecycle management
- Network/grid/continuous spaces
- Batch running for Monte Carlo
- Data collection
- Built-in visualization (browser-based)

```python
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector

class BuyerAgent(Agent):
    def __init__(self, unique_id, model, segment):
        super().__init__(unique_id, model)
        self.segment = segment
        self.stage = "unaware"
    
    def step(self):
        # Your decision logic here
        pass

class MarketModel(Model):
    def __init__(self, num_agents, strategy):
        self.schedule = RandomActivation(self)
        self.strategy = strategy
        
        for i in range(num_agents):
            agent = BuyerAgent(i, self, "enterprise")
            self.schedule.add(agent)
        
        self.datacollector = DataCollector(
            model_reporters={"Conversions": compute_conversions},
            agent_reporters={"Stage": "stage"}
        )
    
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
```

### Senzing (Entity Resolution)
**GitHub:** github.com/Senzing
**Tutorial:** github.com/DerwenAI/ERKG

What it gives you:
- Fuzzy matching across data sources
- Entity deduplication
- Relationship discovery
- Works with Neo4j

```python
from senzing import G2Engine, G2Exception

# Initialize
engine = G2Engine()
engine.init("RLTX", config_json)

# Add records
engine.addRecord("CRM", "customer_123", json.dumps(customer_data))

# Resolve
response = engine.getEntityByRecordID("CRM", "customer_123")
```

### Neo4j GraphRAG (Knowledge Graphs)
**GitHub:** github.com/neo4j/neo4j-graphrag-python
**Docs:** neo4j.com/docs/graphrag

What it gives you:
- Knowledge graph construction from unstructured data
- Entity extraction with LLMs
- Vector similarity search
- Graph-based retrieval

```python
from neo4j_graphrag.experimental.pipeline import Pipeline
from neo4j_graphrag.embeddings import OpenAIEmbeddings

# Build knowledge graph from documents
pipeline = Pipeline.from_schema(schema, llm, embeddings)
pipeline.run(documents)

# Query with RAG
result = graph.query("""
    MATCH (c:Customer)-[:PURCHASED]->(p:Product)
    WHERE c.segment = $segment
    RETURN c, p
""", {"segment": "enterprise"})
```

### AgentSociety (Large-Scale LLM Agents)
**Paper:** arxiv.org/abs/2502.08691
**Framework:** 10K+ agents with LLM reasoning

What it gives you:
- Architecture for scaling LLM-driven agents
- Social interaction models
- Memory and belief systems

### Generative Agents (Stanford)
**Paper:** Park et al. 2023
**GitHub:** github.com/joonspk-research/generative_agents

What it gives you:
- Memory stream architecture
- Reflection and planning
- Natural language state tracking

---

## Architecture Patterns Worth Studying

### 1. Hybrid LLM-Mathematical Agents
Use LLMs to generate agent parameters, run fast math simulation, LLM explains on demand.

```python
# Generate persona once
persona = llm.generate_persona(segment_profile)

# Extract parameters
params = llm.extract_decision_params(persona)

# Fast simulation (no LLM calls)
for day in range(90):
    for agent in agents:
        agent.decide(params, market_signals)

# Explain on demand (LLM call)
explanation = llm.explain_decision(agent, decision_event)
```

### 2. Branching Futures
Fork state at decision points for scenario trees.

```python
def branch(state, num_branches):
    """Create parallel branches from a state"""
    branches = []
    for i in range(num_branches):
        branch_state = deepcopy(state)
        branch_state.seed = i
        branches.append(branch_state)
    return branches

# Run branches in parallel
with ProcessPoolExecutor() as executor:
    results = list(executor.map(simulate_branch, branches))
```

### 3. Network Influence
Social network effects on decision propagation.

```python
def propagate_influence(agents, decided_agents):
    """Word of mouth from decided agents"""
    for agent in decided_agents:
        if agent.decision.chose_product:
            for connection_id in agent.connections:
                connected = agents[connection_id]
                # Boost awareness based on influence
                boost = agent.influence_score * 0.1
                connected.awareness[agent.decision.product_id] += boost
```

---

## Performance Benchmarks

| Configuration | Agents | Branches | Time | Hardware |
|--------------|--------|----------|------|----------|
| Mesa, no LLM | 10K | 1K | ~2 min | M1 Mac |
| Mesa, no LLM | 50K | 1K | ~8 min | M1 Mac |
| Mesa + LLM personas | 10K | 100 | ~15 min | M1 Mac + API |
| Mesa + full LLM decisions | 1K | 10 | ~30 min | API limited |

**Recommendation:** Generate LLM personas for 100 agents per segment, use mathematical simulation for the rest. LLM explains decisions on-demand only.

---

## Quick Start Commands

```bash
# Create project
mkdir rltx-demo && cd rltx-demo
python -m venv venv
source venv/bin/activate

# Install core
pip install mesa[rec] pydantic numpy scipy

# Install API/UI
pip install fastapi uvicorn reflex

# Install LLM
pip install anthropic

# Install viz
pip install plotly altair

# Start building
reflex init
```

---

## Resources

- Mesa docs: mesa.readthedocs.io
- Mesa examples: github.com/mesa/mesa-examples
- Senzing + Neo4j tutorial: github.com/DerwenAI/ERKG
- AgentSociety paper: arxiv.org/abs/2502.08691
- LLM Agent-Based Modeling survey: github.com/tsinghua-fib-lab/LLM-Agent-Based-Modeling-and-Simulation
- Foundation Capital on Context Graphs: foundationcapital.com/context-graphs
