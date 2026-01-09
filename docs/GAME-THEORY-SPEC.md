# Populous: Game Theory Specification

## Overview

Populous implements game-theoretic competitor simulation to predict how competitors will respond to your strategic moves. This goes beyond simple customer simulation to model the full competitive landscape.

---

## Game-Theoretic Framework

### Game Structure

**Players:**
1. Your company (the decision maker)
2. Competitor agents (1-5 major competitors)
3. Customer agents (500+ synthetic customers)

**Game Type:**
- Sequential game (you move first, competitors respond)
- Repeated game (multi-round over simulation period)
- Imperfect information (uncertainty about competitor state)

### Payoff Functions

Each player optimizes a weighted combination of:

```python
class CompetitorPayoff:
    def calculate(self, market_state: Dict) -> float:
        return (
            self.weights["market_share"] * market_state["our_share"] +
            self.weights["revenue"] * market_state["our_revenue"] +
            self.weights["profit_margin"] * market_state["our_margin"] +
            self.weights["growth"] * market_state["our_growth"] -
            self.weights["risk_aversion"] * market_state["uncertainty"]
        )
```

**Weight Profiles by Strategy Type:**

| Strategy | Market Share | Revenue | Margin | Growth | Risk Aversion |
|----------|-------------|---------|--------|--------|---------------|
| Aggressive | 0.40 | 0.20 | 0.10 | 0.25 | 0.05 |
| Defensive | 0.30 | 0.25 | 0.20 | 0.10 | 0.15 |
| Opportunistic | 0.20 | 0.30 | 0.25 | 0.15 | 0.10 |
| Passive | 0.15 | 0.25 | 0.35 | 0.10 | 0.15 |

---

## Competitor Agent Architecture

### CompetitorAgent Class

```python
class CompetitorAgent:
    """
    A game-theoretic competitor that responds to market moves.
    """

    def __init__(
        self,
        company: Company,
        strategy_type: str,
        risk_tolerance: float,
        response_speed: str,
        resources: Dict[str, str]
    ):
        self.company = company
        self.strategy_type = strategy_type
        self.risk_tolerance = risk_tolerance
        self.response_speed = response_speed
        self.resources = resources

        # Derived from strategy type
        self.payoff_weights = self._get_payoff_weights()

        # State tracking
        self.beliefs = {}  # What they believe about the market
        self.history = []  # Past moves and outcomes

    def observe_move(self, move: Dict, market_state: Dict):
        """
        Observe a competitor move and update beliefs.
        """
        self.beliefs["last_move"] = move
        self.beliefs["market_state"] = market_state
        self.history.append({
            "timestamp": datetime.now(),
            "move": move,
            "market_state": market_state
        })

    def decide_response(self, your_move: Dict, market_state: Dict) -> Optional[Dict]:
        """
        Decide whether and how to respond to a move.
        Uses backward induction and Nash equilibrium concepts.
        """
        # Calculate all possible responses
        possible_responses = self._generate_possible_responses(your_move)

        # Calculate payoff for each response
        response_payoffs = []
        for response in possible_responses:
            future_state = self._simulate_future(response, market_state)
            payoff = self._calculate_payoff(future_state)
            response_payoffs.append((response, payoff))

        # Calculate payoff for no response
        no_response_state = self._simulate_future(None, market_state)
        no_response_payoff = self._calculate_payoff(no_response_state)

        # Choose best response if it beats no response by enough
        best_response, best_payoff = max(response_payoffs, key=lambda x: x[1])

        threshold = 0.05 * (1 - self.risk_tolerance)  # Higher risk tolerance = lower threshold
        if best_payoff > no_response_payoff + threshold:
            return self._add_timing(best_response)
        else:
            return None

    def _generate_possible_responses(self, your_move: Dict) -> List[Dict]:
        """
        Generate possible response moves based on your move type.
        """
        responses = []

        if your_move["type"] == "price_change":
            percent = your_move["percent"]

            # Match
            responses.append({
                "type": "price_change",
                "percent": percent,
                "rationale": "match_competitor"
            })

            # Undercut
            if percent > 0:  # You raised, they could stay or lower
                responses.append({
                    "type": "price_change",
                    "percent": 0,
                    "rationale": "hold_ground"
                })
                responses.append({
                    "type": "price_change",
                    "percent": -5,
                    "rationale": "undercut"
                })
            else:  # You lowered
                responses.append({
                    "type": "price_change",
                    "percent": percent - 5,
                    "rationale": "undercut_more"
                })

            # Differentiate (no price change, add value)
            responses.append({
                "type": "feature_announcement",
                "features": ["enhanced_support", "new_integration"],
                "rationale": "differentiate"
            })

            # Marketing response
            responses.append({
                "type": "marketing_campaign",
                "intensity": "high",
                "message": "value_proposition",
                "rationale": "defend_perception"
            })

        elif your_move["type"] == "feature_launch":
            responses.append({
                "type": "feature_announcement",
                "features": ["similar_feature"],
                "timeline": "soon",
                "rationale": "match_feature"
            })
            responses.append({
                "type": "price_reduction",
                "percent": -10,
                "rationale": "compete_on_price"
            })

        return responses

    def _simulate_future(self, response: Optional[Dict], market_state: Dict) -> Dict:
        """
        Simulate market state after response.
        Simple model of customer reactions.
        """
        future_state = market_state.copy()

        if response is None:
            # No response - you gain from your move
            if market_state.get("your_move_type") == "price_increase":
                future_state["our_share"] *= 1.02  # Small gain from your price increase
            return future_state

        if response["type"] == "price_change":
            if response["percent"] < 0:
                # We lowered price - attract price-sensitive customers
                future_state["our_share"] *= 1.05
                future_state["our_margin"] *= 0.95
            else:
                # We raised price - may lose some share
                future_state["our_margin"] *= 1.03
                future_state["our_share"] *= 0.98

        elif response["type"] == "marketing_campaign":
            future_state["our_share"] *= 1.02
            future_state["our_margin"] *= 0.99  # Campaign cost

        elif response["type"] == "feature_announcement":
            future_state["our_share"] *= 1.03

        return future_state

    def _calculate_payoff(self, future_state: Dict) -> float:
        """
        Calculate payoff for a future state.
        """
        return (
            self.payoff_weights["market_share"] * future_state.get("our_share", 0) +
            self.payoff_weights["revenue"] * future_state.get("our_revenue", 0) +
            self.payoff_weights["profit_margin"] * future_state.get("our_margin", 0) +
            self.payoff_weights["growth"] * future_state.get("our_growth", 0)
        )

    def _add_timing(self, response: Dict) -> Dict:
        """
        Add timing to response based on response_speed.
        """
        delays = {
            "immediate": 1,  # Next day
            "fast": 7,  # Within a week
            "normal": 14,  # Within two weeks
            "slow": 30  # Within a month
        }
        response["delay_days"] = delays.get(self.response_speed, 14)
        return response
```

---

## Nash Equilibrium Calculation

For strategic decisions, we calculate Nash equilibrium to find stable outcomes.

### Two-Player Matrix Game

When there are clear discrete choices, we model as a matrix game:

```python
def find_nash_equilibrium(payoff_matrix: np.ndarray) -> Tuple[int, int]:
    """
    Find pure strategy Nash equilibrium for 2-player game.
    payoff_matrix[i, j] = (your_payoff, their_payoff) for your strategy i, their strategy j
    """
    your_strategies, their_strategies = payoff_matrix.shape[:2]

    # Find best responses
    for i in range(your_strategies):
        for j in range(their_strategies):
            your_payoff, their_payoff = payoff_matrix[i, j]

            # Check if j is best response to i
            their_br = True
            for j2 in range(their_strategies):
                if payoff_matrix[i, j2][1] > their_payoff:
                    their_br = False
                    break

            # Check if i is best response to j
            your_br = True
            for i2 in range(your_strategies):
                if payoff_matrix[i2, j][0] > your_payoff:
                    your_br = False
                    break

            if your_br and their_br:
                return (i, j)

    # No pure strategy equilibrium - use mixed strategy
    return find_mixed_equilibrium(payoff_matrix)
```

### Example: Pricing Game

```
                    Competitor
                 Hold Price    Lower Price
You:
Raise Price     (80, 90)      (60, 100)
Hold Price      (85, 85)      (70, 95)
Lower Price     (95, 70)      (75, 75)

Reading: (Your payoff, Their payoff)
```

Analysis:
- If you raise, they should lower (100 > 90)
- If you hold, they should lower (95 > 85)
- If you lower, they should lower (75 > 70)

Their dominant strategy: Lower price
Your best response to their lower: Lower price too

Nash equilibrium: Both lower price (75, 75) - a "race to the bottom"

This is why game theory matters: naive analysis says "raise price for more margin" but game theory shows the equilibrium outcome.

---

## Multi-Round Games

Real competition is repeated, which changes dynamics:

### Reputation Effects

```python
class ReputationTracker:
    def __init__(self):
        self.history = []

    def record_move(self, player: str, move: Dict, context: Dict):
        self.history.append({
            "player": player,
            "move": move,
            "context": context,
            "timestamp": datetime.now()
        })

    def get_reputation(self, player: str) -> Dict:
        """
        Calculate reputation metrics from history.
        """
        player_moves = [h for h in self.history if h["player"] == player]

        return {
            "aggression": self._calculate_aggression(player_moves),
            "responsiveness": self._calculate_responsiveness(player_moves),
            "predictability": self._calculate_predictability(player_moves),
            "cooperation_tendency": self._calculate_cooperation(player_moves)
        }
```

### Tit-for-Tat Strategies

Some competitors use tit-for-tat: cooperate initially, then mirror your last move.

```python
def tit_for_tat_response(self, your_last_move: Dict) -> Dict:
    """
    Respond with equivalent move to your last move.
    """
    if your_last_move.get("cooperative", True):
        return {"type": "hold", "cooperative": True}
    else:
        # You were aggressive, we respond in kind
        return {"type": "match_aggression", "cooperative": False}
```

---

## Uncertainty Modeling

### Belief Updates (Bayesian)

Competitors don't know your true strategy. They update beliefs:

```python
def update_beliefs(self, observed_move: Dict):
    """
    Update probability distribution over your strategy types.
    """
    likelihoods = {}
    for strategy_type in ["aggressive", "defensive", "opportunistic", "passive"]:
        # P(observed_move | strategy_type)
        likelihoods[strategy_type] = self._move_likelihood(
            observed_move, strategy_type
        )

    # Bayes update: P(strategy | move) ∝ P(move | strategy) * P(strategy)
    total = sum(
        likelihoods[s] * self.beliefs["strategy_prior"][s]
        for s in likelihoods
    )

    for strategy_type in likelihoods:
        self.beliefs["strategy_posterior"][strategy_type] = (
            likelihoods[strategy_type] *
            self.beliefs["strategy_prior"][strategy_type] /
            total
        )
```

### Response Probability

We don't just predict the response, we estimate probability:

```python
def response_probability(self, your_move: Dict) -> Dict[str, float]:
    """
    Return probability distribution over possible responses.
    """
    responses = self._generate_possible_responses(your_move)
    responses.append(None)  # No response

    probabilities = {}
    for response in responses:
        future_state = self._simulate_future(response, self.market_state)
        payoff = self._calculate_payoff(future_state)

        # Softmax over payoffs
        probabilities[str(response)] = math.exp(payoff / self.temperature)

    # Normalize
    total = sum(probabilities.values())
    return {k: v/total for k, v in probabilities.items()}
```

---

## Integration with Simulation

### Simulation Loop with Competitors

```python
async def run_simulation_with_competitors(
    decision: Decision,
    customers: List[GenerativeAgent],
    competitors: List[CompetitorAgent],
    days: int = 90
) -> SimulationResult:

    # Day 0: Your move is announced
    your_move = decision.options[0].to_move()

    for day in range(1, days + 1):
        # Competitors observe and potentially respond
        for competitor in competitors:
            competitor.observe_move(your_move, market_state)

            if day >= competitor.response_delay:
                response = competitor.decide_response(your_move, market_state)
                if response:
                    # Competitor responds - this affects customers
                    apply_competitor_response(response, market_state)

                    # Customers perceive competitor response
                    for customer in customers:
                        customer.perceive(f"Competitor {competitor.name} announced: {response}")

        # Customers make decisions based on current market state
        for customer in customers:
            customer.perceive(f"Day {day}: {describe_market_state(market_state)}")

            if customer.should_reflect():
                customer.reflect()

            if customer.should_decide():
                customer.decide()

    return aggregate_results(customers, competitors)
```

---

## Scenario Branching with Competitors

Each competitor response creates a branch:

```
                        [Your Move: +10% Price]
                                  │
           ┌──────────────────────┼──────────────────────┐
           ▼                      ▼                      ▼
    [Comp A: Match]      [Comp A: Undercut]     [Comp A: No Response]
    P=0.30               P=0.45                 P=0.25
           │                      │                      │
      ┌────┴────┐            ┌────┴────┐            ┌────┴────┐
      ▼         ▼            ▼         ▼            ▼         ▼
  [Comp B:  [Comp B:    [Comp B:   [Comp B:    [Comp B:   [Comp B:
   Match]   Undercut]    Match]    Undercut]   Match]     None]
   P=0.40    P=0.60      P=0.30     P=0.70     P=0.20     P=0.80
```

Each branch runs its own customer simulation, leading to different outcomes.

---

## Output: Competitor Analysis

The game theory module outputs:

```python
class CompetitorAnalysis:
    competitor_id: str
    competitor_name: str

    # Predicted response
    most_likely_response: Dict
    response_probability: float

    # Alternative responses
    alternative_responses: List[Tuple[Dict, float]]

    # Timing
    expected_response_delay: int  # days

    # Impact
    impact_on_your_outcome: float  # How much their response hurts/helps you
    impact_on_customers: str  # Description

    # Counter-strategy
    recommended_counter: str
    counter_effectiveness: float
```

---

## Example: Pricing Decision

**Your Move:** Raise prices 15%

**Competitor A (Aggressive, market leader):**
- Most likely response: Match price increase (40%)
- Alternative: Hold and run "value" campaign (35%)
- Timing: Within 1 week
- Impact: If they match, your churn drops 8pp

**Competitor B (Defensive, challenger):**
- Most likely response: Undercut by 5% (60%)
- Alternative: No response (25%)
- Timing: Within 2 weeks
- Impact: If they undercut, your churn increases 12pp

**Combined Scenario Probabilities:**
- Both match: 16% → 82% retention
- A matches, B undercuts: 24% → 71% retention
- A holds, B undercuts: 21% → 68% retention
- Neither responds: 6% → 88% retention
- ...

**Recommendation:**
"Proceed with 15% increase. Prepare contingency: if Competitor B undercuts within 2 weeks, deploy retention offer to price-sensitive segment (pre-drafted)."
