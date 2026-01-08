"""
RLTX Populous Frontend - Complete Reflex Application
Decision Intelligence Simulation Platform

This implements the full UI/UX flow:
1. Scenario Setup - Define market environment
2. Strategy Configuration - Set up GTM strategies to test
3. Simulation Runner - Watch futures fork in real-time
4. Results Dashboard - Probability distributions and insights
5. Agent Deep-Dive - Interview synthetic customers
"""

import reflex as rx
import httpx
from typing import List, Dict, Any
import asyncio


# =============================================================================
# STATE MANAGEMENT
# =============================================================================

class State(rx.State):
    """Global application state"""

    # ---------- API Connection ----------
    api_url: str = "http://localhost:8000"
    api_connected: bool = False
    error_message: str = ""

    # ---------- Data ----------
    scenarios: List[Dict[str, Any]] = []
    strategies: List[Dict[str, Any]] = []
    selected_scenario_id: str = ""
    selected_scenario: Dict[str, Any] = {}
    selected_strategy_ids: List[str] = []

    # ---------- Simulation State ----------
    is_simulating: bool = False
    simulation_progress: float = 0.0
    simulation_status: str = ""
    branches_computed: int = 0

    # ---------- Results ----------
    comparison_results: List[Dict[str, Any]] = []
    winner_id: str = ""
    insight: str = ""
    has_results: bool = False

    # Single simulation results (for detailed view)
    current_result: Dict[str, Any] = {}
    branch_timeline: List[Dict[str, Any]] = []

    # ---------- Agent Deep-Dive ----------
    available_agents: List[Dict[str, Any]] = []
    selected_agent: Dict[str, Any] = {}
    selected_agent_id: str = ""
    chat_messages: List[Dict[str, Any]] = []
    chat_input: str = ""
    is_chatting: bool = False

    # ---------- UI State ----------
    active_tab: str = "setup"
    show_scenario_details: bool = False
    show_advanced_settings: bool = False

    # Simulation parameters
    num_agents: int = 5000
    num_branches: int = 200

    # Computed properties
    @rx.var
    def selected_strategies_count(self) -> int:
        return len(self.selected_strategy_ids)

    @rx.var
    def has_selected_strategies(self) -> bool:
        return len(self.selected_strategy_ids) > 0

    @rx.var
    def can_run_simulation(self) -> bool:
        return len(self.selected_strategy_ids) > 0 and bool(self.selected_scenario_id)

    # ==========================================================================
    # INITIALIZATION & DATA LOADING
    # ==========================================================================

    async def on_mount(self):
        """Initialize the application on page load"""
        await self.check_api_connection()
        if self.api_connected:
            await self.load_scenarios()
            await self.load_strategies()

    async def check_api_connection(self):
        """Check if backend API is available"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.api_url}/health")
                if response.status_code == 200:
                    self.api_connected = True
                    self.error_message = ""
                else:
                    self.api_connected = False
                    self.error_message = "API returned error status"
        except Exception as e:
            self.api_connected = False
            self.error_message = f"Cannot connect to API at {self.api_url}. Start the backend with: python -m backend.run"

    async def load_scenarios(self):
        """Load available scenarios from API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}/scenarios")
                self.scenarios = response.json()
                if self.scenarios and not self.selected_scenario_id:
                    self.selected_scenario_id = self.scenarios[0]["id"]
                    self.selected_scenario = self.scenarios[0]
        except Exception as e:
            self.error_message = f"Failed to load scenarios: {str(e)}"

    async def load_strategies(self):
        """Load available strategies from API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}/strategies")
                self.strategies = response.json()
        except Exception as e:
            self.error_message = f"Failed to load strategies: {str(e)}"

    # ==========================================================================
    # SCENARIO SELECTION
    # ==========================================================================

    
    def select_scenario(self, scenario_id: str):
        """Select a scenario"""
        self.selected_scenario_id = scenario_id
        for s in self.scenarios:
            if s["id"] == scenario_id:
                self.selected_scenario = s
                break

    
    def toggle_scenario_details(self):
        """Toggle scenario details panel"""
        self.show_scenario_details = not self.show_scenario_details

    # ==========================================================================
    # STRATEGY SELECTION
    # ==========================================================================

    
    def toggle_strategy(self, strategy_id: str):
        """Toggle a strategy selection"""
        if strategy_id in self.selected_strategy_ids:
            self.selected_strategy_ids = [
                s for s in self.selected_strategy_ids if s != strategy_id
            ]
        else:
            self.selected_strategy_ids = self.selected_strategy_ids + [strategy_id]

    
    def select_all_strategies(self):
        """Select all strategies"""
        self.selected_strategy_ids = [s["id"] for s in self.strategies]

    
    def clear_strategies(self):
        """Clear all strategy selections"""
        self.selected_strategy_ids = []

    # ==========================================================================
    # SIMULATION SETTINGS
    # ==========================================================================

    
    def toggle_advanced_settings(self):
        """Toggle advanced settings panel"""
        self.show_advanced_settings = not self.show_advanced_settings

    
    def set_num_agents(self, value: str):
        """Set number of agents"""
        try:
            self.num_agents = int(value)
        except ValueError:
            pass

    
    def set_num_branches(self, value: str):
        """Set number of branches"""
        try:
            self.num_branches = int(value)
        except ValueError:
            pass

    # ==========================================================================
    # SIMULATION EXECUTION
    # ==========================================================================

    
    async def run_comparison(self):
        """Run strategy comparison simulation"""
        if not self.selected_strategy_ids:
            self.error_message = "Please select at least one strategy to test"
            return

        if not self.selected_scenario_id:
            self.error_message = "Please select a scenario"
            return

        self.is_simulating = True
        self.simulation_status = "Initializing simulation..."
        self.simulation_progress = 0.0
        self.error_message = ""
        self.comparison_results = []
        self.winner_id = ""
        self.insight = ""
        self.active_tab = "results"

        try:
            # Progress updates
            self.simulation_status = "Creating synthetic agents..."
            self.simulation_progress = 0.1

            async with httpx.AsyncClient(timeout=600) as client:
                self.simulation_status = f"Running {self.num_branches} Monte Carlo branches..."
                self.simulation_progress = 0.3

                response = await client.post(
                    f"{self.api_url}/compare",
                    json={
                        "scenario_id": self.selected_scenario_id,
                        "strategy_ids": self.selected_strategy_ids,
                        "num_agents": self.num_agents,
                        "num_branches": self.num_branches,
                    },
                )

                self.simulation_progress = 0.9
                self.simulation_status = "Generating AI insights..."

                if response.status_code == 200:
                    data = response.json()
                    self.comparison_results = data.get("comparisons", [])
                    self.winner_id = data.get("winner", "")
                    self.insight = data.get("insight", "")
                    self.has_results = True
                    self.simulation_progress = 1.0
                    self.simulation_status = "Complete"
                else:
                    self.error_message = f"Simulation failed: {response.text}"

        except httpx.TimeoutException:
            self.error_message = "Simulation timed out. Try reducing the number of branches."
        except Exception as e:
            self.error_message = f"Simulation error: {str(e)}"

        self.is_simulating = False

    # ==========================================================================
    # AGENT DEEP-DIVE
    # ==========================================================================

    
    async def load_agents(self, result_id: str = ""):
        """Load agents for exploration"""
        try:
            async with httpx.AsyncClient() as client:
                # For demo, we generate sample agents
                self.available_agents = [
                    {
                        "id": "smb_0",
                        "segment_id": "smb",
                        "persona_name": "Sarah Chen",
                        "persona_role": "Founder & CEO",
                        "company": "TechStart Labs",
                        "stage": "Evaluating",
                    },
                    {
                        "id": "smb_1",
                        "segment_id": "smb",
                        "persona_name": "Mike Rodriguez",
                        "persona_role": "Operations Manager",
                        "company": "Creative Co",
                        "stage": "Decided",
                    },
                    {
                        "id": "mid_market_0",
                        "segment_id": "mid_market",
                        "persona_name": "Jennifer Park",
                        "persona_role": "VP of Operations",
                        "company": "GrowthScale Inc",
                        "stage": "Evaluating",
                    },
                    {
                        "id": "mid_market_1",
                        "segment_id": "mid_market",
                        "persona_name": "David Thompson",
                        "persona_role": "Director of IT",
                        "company": "MidSize Solutions",
                        "stage": "Decided",
                    },
                    {
                        "id": "enterprise_0",
                        "segment_id": "enterprise",
                        "persona_name": "Robert Williams",
                        "persona_role": "CTO",
                        "company": "Enterprise Corp",
                        "stage": "Evaluating",
                    },
                ]
        except Exception as e:
            self.error_message = f"Failed to load agents: {str(e)}"

    
    def select_agent(self, agent: Dict[str, Any]):
        """Select an agent for deep-dive"""
        self.selected_agent = agent
        self.selected_agent_id = agent.get("id", "")
        self.chat_messages = []

    
    def set_chat_input(self, value: str):
        """Update chat input"""
        self.chat_input = value

    
    async def send_chat_message(self):
        """Send a message to the selected agent"""
        if not self.chat_input.strip() or not self.selected_agent:
            return

        message = self.chat_input
        self.chat_input = ""
        self.is_chatting = True

        # Add user message
        self.chat_messages = self.chat_messages + [
            {"role": "user", "content": message}
        ]

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.api_url}/agents/{self.selected_agent['id']}/chat",
                    json={"message": message},
                )

                if response.status_code == 200:
                    data = response.json()
                    self.chat_messages = self.chat_messages + [
                        {"role": "assistant", "content": data.get("response", "")}
                    ]
                else:
                    self.chat_messages = self.chat_messages + [
                        {"role": "assistant", "content": "Sorry, I couldn't process that request."}
                    ]
        except Exception as e:
            self.chat_messages = self.chat_messages + [
                {"role": "assistant", "content": f"Error: {str(e)}"}
            ]

        self.is_chatting = False

    
    def clear_chat(self):
        """Clear chat history"""
        self.chat_messages = []

    # ==========================================================================
    # NAVIGATION
    # ==========================================================================

    
    def set_tab(self, tab: str):
        """Set active tab"""
        self.active_tab = tab
        if tab == "agent" and not self.available_agents:
            # Load agents when navigating to agent tab
            return State.load_agents()

    
    def go_to_results(self):
        """Navigate to results tab"""
        self.active_tab = "results"

    
    def go_to_agent_chat(self):
        """Navigate to agent chat tab"""
        self.active_tab = "agent"


# =============================================================================
# COMPONENTS
# =============================================================================

def header() -> rx.Component:
    """Application header"""
    return rx.hstack(
        rx.hstack(
            rx.icon("brain-circuit", size=32, color="var(--accent-9)"),
            rx.vstack(
                rx.heading("RLTX Populous", size="6", weight="bold"),
                rx.text(
                    "Decision Intelligence Platform",
                    size="1",
                    color="gray",
                ),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
        ),
        rx.spacer(),
        rx.hstack(
            rx.cond(
                State.api_connected,
                rx.badge("API Connected", color_scheme="green", variant="soft"),
                rx.badge("API Disconnected", color_scheme="red", variant="soft"),
            ),
            rx.button(
                rx.icon("refresh-cw", size=16),
                variant="ghost",
                on_click=State.check_api_connection,
            ),
            spacing="2",
        ),
        width="100%",
        padding="4",
        border_bottom="1px solid var(--gray-5)",
        background="var(--gray-1)",
    )


def nav_tabs() -> rx.Component:
    """Navigation tabs"""
    return rx.hstack(
        rx.button(
            rx.icon("settings-2", size=16),
            "Setup",
            variant=rx.cond(State.active_tab == "setup", "solid", "ghost"),
            on_click=lambda: State.set_tab("setup"),
        ),
        rx.button(
            rx.icon("play", size=16),
            "Simulate",
            variant=rx.cond(State.active_tab == "simulate", "solid", "ghost"),
            on_click=lambda: State.set_tab("simulate"),
        ),
        rx.button(
            rx.icon("bar-chart-3", size=16),
            "Results",
            variant=rx.cond(State.active_tab == "results", "solid", "ghost"),
            on_click=lambda: State.set_tab("results"),
            disabled=~State.has_results,
        ),
        rx.button(
            rx.icon("message-circle", size=16),
            "Agent Deep-Dive",
            variant=rx.cond(State.active_tab == "agent", "solid", "ghost"),
            on_click=lambda: State.set_tab("agent"),
        ),
        spacing="2",
        padding="3",
        background="var(--gray-2)",
        border_radius="lg",
        margin="4",
    )


def error_alert() -> rx.Component:
    """Error message display"""
    return rx.cond(
        State.error_message != "",
        rx.callout(
            State.error_message,
            icon="circle-alert",
            color="red",
            margin="4",
        ),
        rx.fragment(),
    )


# =============================================================================
# SETUP TAB
# =============================================================================

def scenario_card(scenario: Dict[str, Any]) -> rx.Component:
    """Scenario selection card"""
    is_selected = scenario["id"] == State.selected_scenario_id
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("globe", size=20, color=rx.cond(is_selected, "var(--accent-9)", "var(--gray-9)")),
                rx.text(scenario["name"], weight="bold", size="3"),
                rx.spacer(),
                rx.cond(
                    is_selected,
                    rx.icon("circle-check-big", size=18, color="var(--accent-9)"),
                    rx.fragment(),
                ),
                width="100%",
            ),
            rx.text(
                scenario["description"],
                size="2",
                color="gray",
            ),
            rx.hstack(
                rx.badge(scenario["total_addressable_market"], variant="soft"),
                spacing="2",
                wrap="wrap",
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        padding="4",
        border_radius="lg",
        border=rx.cond(is_selected, "2px solid var(--accent-9)", "1px solid var(--gray-6)"),
        background=rx.cond(is_selected, "var(--accent-2)", "var(--gray-1)"),
        cursor="pointer",
        on_click=lambda: State.select_scenario(scenario["id"]),
        _hover={"border_color": "var(--accent-7)"},
    )


def strategy_card(strategy: Dict[str, Any]) -> rx.Component:
    """Strategy selection card"""
    is_selected = State.selected_strategy_ids.contains(strategy["id"])
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.checkbox(
                    checked=is_selected,
                    on_change=lambda _: State.toggle_strategy(strategy["id"]),
                ),
                rx.text(strategy["name"], weight="bold", size="3"),
                rx.spacer(),
                width="100%",
            ),
            rx.text(
                strategy["description"],
                size="2",
                color="gray",
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        padding="4",
        border_radius="lg",
        border=rx.cond(is_selected, "2px solid var(--accent-9)", "1px solid var(--gray-6)"),
        background=rx.cond(is_selected, "var(--accent-2)", "var(--gray-1)"),
        cursor="pointer",
        on_click=lambda: State.toggle_strategy(strategy["id"]),
        _hover={"border_color": "var(--accent-7)"},
    )


def segment_badge(segment: Dict[str, Any]) -> rx.Component:
    """Segment info badge"""
    return rx.tooltip(
        rx.badge(
            f'{segment["name"]}: {int(segment["size_pct"] * 100)}%',
            variant="soft",
        ),
        content=f'Avg cycle: {segment.get("decision_framework", {}).get("avg_cycle_days", "N/A")} days',
    )


def scenario_details() -> rx.Component:
    """Expandable scenario details"""
    return rx.cond(
        State.show_scenario_details,
        rx.box(
            rx.vstack(
                rx.heading("Scenario Details", size="4"),
                rx.text(
                    "View market segments, competitors, and product info in the simulation run",
                    size="2",
                    color="gray",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            padding="4",
            border="1px solid var(--gray-5)",
            border_radius="lg",
            background="var(--gray-1)",
            margin_top="3",
        ),
        rx.fragment(),
    )


def advanced_settings() -> rx.Component:
    """Advanced simulation settings"""
    return rx.cond(
        State.show_advanced_settings,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Number of Agents", size="2", weight="medium"),
                        rx.input(
                            value=State.num_agents,
                            on_change=State.set_num_agents,
                            type="number",
                            width="150px",
                        ),
                        rx.text("Synthetic buyers to simulate", size="1", color="gray"),
                        align="start",
                    ),
                    rx.vstack(
                        rx.text("Monte Carlo Branches", size="2", weight="medium"),
                        rx.input(
                            value=State.num_branches,
                            on_change=State.set_num_branches,
                            type="number",
                            width="150px",
                        ),
                        rx.text("Parallel futures to compute", size="1", color="gray"),
                        align="start",
                    ),
                    spacing="6",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            padding="4",
            border="1px solid var(--gray-5)",
            border_radius="lg",
            background="var(--gray-1)",
            margin_top="3",
        ),
        rx.fragment(),
    )


def setup_view() -> rx.Component:
    """Setup tab content"""
    return rx.vstack(
        # Scenario Section
        rx.vstack(
            rx.hstack(
                rx.heading("1. Select Market Scenario", size="5"),
                rx.button(
                    rx.cond(
                        State.show_scenario_details,
                        rx.icon("chevron-up", size=16),
                        rx.icon("chevron-down", size=16),
                    ),
                    "Details",
                    variant="ghost",
                    size="1",
                    on_click=State.toggle_scenario_details,
                ),
                width="100%",
                justify="between",
            ),
            rx.text(
                "Choose the market environment for your simulation",
                size="2",
                color="gray",
            ),
            rx.vstack(
                rx.foreach(State.scenarios, scenario_card),
                spacing="3",
                width="100%",
            ),
            scenario_details(),
            spacing="3",
            align="start",
            width="100%",
        ),
        rx.divider(margin_y="4"),
        # Strategy Section
        rx.vstack(
            rx.hstack(
                rx.heading("2. Select Strategies to Compare", size="5"),
                rx.hstack(
                    rx.button("Select All", variant="ghost", size="1", on_click=State.select_all_strategies),
                    rx.button("Clear", variant="ghost", size="1", on_click=State.clear_strategies),
                    spacing="2",
                ),
                width="100%",
                justify="between",
            ),
            rx.text(
                "Choose one or more go-to-market strategies to test",
                size="2",
                color="gray",
            ),
            rx.grid(
                rx.foreach(State.strategies, strategy_card),
                columns="2",
                spacing="3",
                width="100%",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        rx.divider(margin_y="4"),
        # Settings Section
        rx.vstack(
            rx.hstack(
                rx.heading("3. Simulation Settings", size="5"),
                rx.button(
                    rx.cond(
                        State.show_advanced_settings,
                        rx.icon("chevron-up", size=16),
                        rx.icon("chevron-down", size=16),
                    ),
                    "Advanced",
                    variant="ghost",
                    size="1",
                    on_click=State.toggle_advanced_settings,
                ),
                width="100%",
                justify="between",
            ),
            rx.hstack(
                rx.icon("users", size=16, color="gray"),
                rx.text(f"{State.num_agents:,} agents", size="2"),
                rx.text("|", color="gray"),
                rx.icon("git-branch", size=16, color="gray"),
                rx.text(f"{State.num_branches} branches", size="2"),
                spacing="2",
            ),
            advanced_settings(),
            spacing="3",
            align="start",
            width="100%",
        ),
        rx.divider(margin_y="4"),
        # Run Button
        rx.button(
            rx.cond(
                State.is_simulating,
                rx.hstack(
                    rx.spinner(size="1"),
                    rx.text("Running Simulation..."),
                    spacing="2",
                ),
                rx.hstack(
                    rx.icon("play", size=18),
                    rx.text("Run Simulation"),
                    spacing="2",
                ),
            ),
            size="4",
            width="100%",
            on_click=State.run_comparison,
            disabled=State.is_simulating,
        ),
        spacing="4",
        padding="4",
        width="100%",
    )


# =============================================================================
# SIMULATE TAB (Running Simulation View)
# =============================================================================

def simulate_view() -> rx.Component:
    """Simulation in progress view"""
    return rx.center(
        rx.vstack(
            rx.cond(
                State.is_simulating,
                rx.vstack(
                    rx.icon("brain-circuit", size=64, color="var(--accent-9)"),
                    rx.heading("Computing Futures", size="6"),
                    rx.text(State.simulation_status, size="3", color="gray"),
                    rx.progress(value=50, width="300px"),
                    rx.text(
                        State.simulation_status,
                        size="2",
                        color="gray",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.text("What's happening:", weight="medium", size="2"),
                            rx.text(
                                f"Simulating {State.num_agents:,} synthetic buyers making decisions across {State.num_branches} parallel timelines",
                                size="2",
                                color="gray",
                            ),
                            spacing="2",
                        ),
                        margin_top="4",
                    ),
                    spacing="4",
                    align="center",
                ),
                rx.vstack(
                    rx.icon("circle-play", size=64, color="var(--gray-9)"),
                    rx.heading("Ready to Simulate", size="6"),
                    rx.text(
                        "Configure your scenario and strategies, then run the simulation",
                        size="3",
                        color="gray",
                    ),
                    rx.button(
                        "Go to Setup",
                        on_click=lambda: State.set_tab("setup"),
                    ),
                    spacing="4",
                    align="center",
                ),
            ),
            spacing="4",
            align="center",
            padding="8",
        ),
        width="100%",
        min_height="400px",
    )


# =============================================================================
# RESULTS TAB
# =============================================================================

def result_card(result: Dict[str, Any]) -> rx.Component:
    """Individual result card"""
    is_winner = result["strategy_id"] == State.winner_id

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.text(result["strategy_name"], weight="bold", size="4"),
                        rx.cond(
                            is_winner,
                            rx.badge("WINNER", color_scheme="green", variant="solid"),
                            rx.fragment(),
                        ),
                        spacing="2",
                    ),
                    rx.hstack(
                        rx.text(result["mean_conversion"], size="7", weight="bold", color=rx.cond(is_winner, "var(--green-11)", "var(--gray-12)")),
                        rx.text("conversion", size="2", color="gray"),
                        align="end",
                        spacing="2",
                    ),
                    align="start",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.text("90% Confidence Interval", size="1", color="gray"),
                    rx.text(result["p5"], size="3", weight="medium"),
                    align="end",
                ),
                width="100%",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        padding="5",
        border_radius="lg",
        border=rx.cond(is_winner, "2px solid var(--green-9)", "1px solid var(--gray-6)"),
        background=rx.cond(is_winner, "var(--green-2)", "var(--gray-1)"),
    )


def insight_panel() -> rx.Component:
    """AI-generated insight panel"""
    return rx.cond(
        State.insight != "",
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("sparkles", size=20, color="var(--accent-9)"),
                    rx.text("AI Insight", weight="bold", size="3"),
                    spacing="2",
                ),
                rx.text(State.insight, size="3", line_height="1.6"),
                spacing="3",
                align="start",
            ),
            background="linear-gradient(135deg, var(--accent-2), var(--accent-3))",
        ),
        rx.fragment(),
    )


def results_view() -> rx.Component:
    """Results tab content"""
    return rx.cond(
        State.has_results,
        rx.vstack(
            rx.hstack(
                rx.heading("Simulation Results", size="5"),
                rx.spacer(),
                rx.button(
                    rx.icon("refresh-cw", size=16),
                    "Run Again",
                    variant="outline",
                    on_click=lambda: State.set_tab("setup"),
                ),
                width="100%",
            ),
            rx.text(
                "Strategy comparison results",
                size="2",
                color="gray",
            ),
            # Results cards
            rx.vstack(
                rx.foreach(State.comparison_results, result_card),
                spacing="4",
                width="100%",
            ),
            # AI Insight
            insight_panel(),
            # Call to action
            rx.card(
                rx.hstack(
                    rx.vstack(
                        rx.text("Want to understand why?", weight="bold"),
                        rx.text(
                            "Interview synthetic buyers to learn their reasoning",
                            size="2",
                            color="gray",
                        ),
                        align="start",
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("message-circle", size=16),
                        "Talk to Agents",
                        on_click=State.go_to_agent_chat,
                    ),
                    width="100%",
                    align="center",
                ),
            ),
            spacing="4",
            padding="4",
            width="100%",
        ),
        rx.center(
            rx.vstack(
                rx.icon("bar-chart-3", size=64, color="var(--gray-6)"),
                rx.heading("No Results Yet", size="5", color="gray"),
                rx.text("Run a simulation to see results", size="3", color="gray"),
                rx.button(
                    "Go to Setup",
                    on_click=lambda: State.set_tab("setup"),
                ),
                spacing="4",
                align="center",
            ),
            padding="8",
        ),
    )


# =============================================================================
# AGENT DEEP-DIVE TAB
# =============================================================================

def agent_list_item(agent: Dict[str, Any]) -> rx.Component:
    """Agent list item"""
    return rx.box(
        rx.hstack(
            rx.box(
                rx.text(agent["persona_name"], size="1"),
                width="32px",
                height="32px",
                background="var(--accent-3)",
                border_radius="full",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.vstack(
                rx.text(agent["persona_name"], weight="medium", size="2"),
                rx.text(agent["persona_role"], size="1", color="gray"),
                spacing="0",
                align="start",
            ),
            rx.spacer(),
            rx.badge(agent["segment_id"], variant="soft", size="1"),
            width="100%",
            padding="2",
        ),
        border_radius="md",
        background=rx.cond(
            State.selected_agent_id == agent["id"],
            "var(--accent-3)",
            "transparent"
        ),
        cursor="pointer",
        on_click=lambda: State.select_agent(agent),
        _hover={"background": "var(--gray-3)"},
    )


def chat_bubble(message: Dict[str, Any]) -> rx.Component:
    """Chat message bubble"""
    is_user = message["role"] == "user"
    return rx.box(
        rx.text(message["content"], size="2"),
        padding="3",
        border_radius="lg",
        background=rx.cond(is_user, "var(--accent-9)", "var(--gray-3)"),
        color=rx.cond(is_user, "white", "var(--gray-12)"),
        max_width="80%",
        align_self=rx.cond(is_user, "flex-end", "flex-start"),
    )


def agent_profile() -> rx.Component:
    """Selected agent profile panel"""
    return rx.cond(
        State.selected_agent_id != "",
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.text("A", size="3"),
                        width="48px",
                        height="48px",
                        background="var(--accent-3)",
                        border_radius="full",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    rx.vstack(
                        rx.text(State.selected_agent["persona_name"], weight="bold", size="4"),
                        rx.text(State.selected_agent["persona_role"], size="2", color="gray"),
                        rx.text(State.selected_agent["company"], size="2", color="gray"),
                        spacing="0",
                        align="start",
                    ),
                    spacing="3",
                ),
                rx.divider(),
                rx.hstack(
                    rx.badge(State.selected_agent["segment_id"], variant="outline"),
                    rx.badge(State.selected_agent["stage"], variant="outline"),
                    spacing="2",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
        ),
        rx.fragment(),
    )


def chat_interface() -> rx.Component:
    """Chat interface with agent"""
    return rx.vstack(
        # Chat messages area
        rx.scroll_area(
            rx.vstack(
                rx.cond(
                    State.chat_messages.length() == 0,
                    rx.center(
                        rx.vstack(
                            rx.icon("message-circle", size=32, color="var(--gray-6)"),
                            rx.text("Start a conversation", size="2", color="gray"),
                            rx.text(
                                'Try asking: "Why did you choose this product?" or "What were your main concerns?"',
                                size="1",
                                color="gray",
                                text_align="center",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        padding="8",
                    ),
                    rx.vstack(
                        rx.foreach(State.chat_messages, chat_bubble),
                        spacing="2",
                        width="100%",
                        align="stretch",
                        padding="3",
                    ),
                ),
                width="100%",
            ),
            height="300px",
            width="100%",
            border="1px solid var(--gray-5)",
            border_radius="lg",
            background="var(--gray-1)",
        ),
        # Input area
        rx.hstack(
            rx.input(
                placeholder="Ask about their decision...",
                value=State.chat_input,
                on_change=State.set_chat_input,
                width="100%",
                disabled=State.is_chatting,
            ),
            rx.button(
                rx.cond(
                    State.is_chatting,
                    rx.spinner(size="1"),
                    rx.icon("send", size=16),
                ),
                on_click=State.send_chat_message,
                disabled=State.is_chatting,
            ),
            width="100%",
            spacing="2",
        ),
        spacing="3",
        width="100%",
    )


def agent_view() -> rx.Component:
    """Agent deep-dive tab content"""
    return rx.hstack(
        # Agent list sidebar
        rx.vstack(
            rx.heading("Synthetic Buyers", size="4"),
            rx.text("Select an agent to interview", size="2", color="gray"),
            rx.divider(),
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(State.available_agents, agent_list_item),
                    spacing="1",
                    width="100%",
                ),
                height="400px",
            ),
            spacing="3",
            width="250px",
            padding="3",
            border_right="1px solid var(--gray-5)",
            background="var(--gray-1)",
        ),
        # Main content area
        rx.vstack(
            rx.cond(
                State.selected_agent_id != "",
                rx.vstack(
                    agent_profile(),
                    rx.heading("Interview This Buyer", size="4"),
                    rx.text(
                        "Ask questions to understand their decision-making process",
                        size="2",
                        color="gray",
                    ),
                    chat_interface(),
                    rx.hstack(
                        rx.button(
                            "Clear Chat",
                            variant="ghost",
                            size="1",
                            on_click=State.clear_chat,
                        ),
                        rx.spacer(),
                        rx.text(
                            "Powered by Claude AI",
                            size="1",
                            color="gray",
                        ),
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                rx.center(
                    rx.vstack(
                        rx.icon("user", size=64, color="var(--gray-6)"),
                        rx.heading("Select an Agent", size="5", color="gray"),
                        rx.text(
                            "Choose a synthetic buyer from the list to start interviewing",
                            size="3",
                            color="gray",
                            text_align="center",
                        ),
                        spacing="4",
                        align="center",
                    ),
                    padding="8",
                ),
            ),
            padding="4",
            flex="1",
        ),
        width="100%",
        min_height="500px",
        align="stretch",
    )


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main_content() -> rx.Component:
    """Main content area with tab switching"""
    return rx.match(
        State.active_tab,
        ("setup", setup_view()),
        ("simulate", simulate_view()),
        ("results", results_view()),
        ("agent", agent_view()),
        setup_view(),  # Default
    )


def index() -> rx.Component:
    """Main page"""
    return rx.box(
        rx.vstack(
            header(),
            error_alert(),
            nav_tabs(),
            rx.box(
                main_content(),
                width="100%",
                max_width="1200px",
                margin="auto",
            ),
            spacing="0",
            width="100%",
            min_height="100vh",
        ),
        on_mount=State.on_mount,
        background="var(--gray-1)",
    )


# =============================================================================
# APP CONFIGURATION
# =============================================================================

app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="blue",
        radius="medium",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
)
app.add_page(index, title="RLTX Populous | Decision Intelligence Platform")
