"""
Visualization Components
Scenario trees, agent networks, timelines, and causal traces
"""

import reflex as rx
from typing import Dict, Any, List, Optional
from ..design_system import colors, borders, shadows, typography, spacing


# =============================================================================
# SCENARIO TREE VISUALIZATION
# =============================================================================

class ScenarioTreeState(rx.State):
    """State for scenario tree visualization"""
    tree_data: Dict[str, Any] = {}
    expanded_nodes: List[str] = []
    selected_path_id: Optional[str] = None
    hover_node_id: Optional[str] = None

    def toggle_node(self, node_id: str):
        if node_id in self.expanded_nodes:
            self.expanded_nodes = [n for n in self.expanded_nodes if n != node_id]
        else:
            self.expanded_nodes = self.expanded_nodes + [node_id]

    def select_path(self, path_id: str):
        self.selected_path_id = path_id

    def set_hover(self, node_id: Optional[str]):
        self.hover_node_id = node_id


def scenario_tree_node(
    node: Dict[str, Any],
    depth: int = 0,
    is_expanded: bool = True,
) -> rx.Component:
    """Individual node in scenario tree"""
    outcome_colors = {
        "favorable": colors["success"],
        "unfavorable": colors["error"],
        "neutral": colors["text_secondary"],
        "escalation": colors["warning"],
    }
    node_color = outcome_colors.get(node.get("outcome", ""), colors["accent"])

    return rx.box(
        rx.hstack(
            # Expand/collapse button (if has children)
            rx.cond(
                len(node.get("children", [])) > 0,
                rx.button(
                    rx.icon(
                        "chevron-down" if is_expanded else "chevron-right",
                        size=12,
                        color=colors["text_secondary"],
                    ),
                    on_click=lambda: ScenarioTreeState.toggle_node(node["id"]),
                    style={
                        "padding": "2px",
                        "background": "transparent",
                        "border": "none",
                        "cursor": "pointer",
                    },
                ),
                rx.box(width="16px"),  # Spacer
            ),

            # Node indicator
            rx.box(
                style={
                    "width": "8px",
                    "height": "8px",
                    "background": node_color,
                    "border_radius": borders["radius_full"],
                },
            ),

            # Node content
            rx.vstack(
                rx.hstack(
                    rx.text(
                        node.get("description", "")[:50],
                        style={
                            "font_size": typography["text_sm"],
                            "color": colors["text_primary"],
                        },
                    ),
                    rx.text(
                        f"{int(node.get('probability', 0) * 100)}%",
                        style={
                            "font_size": typography["text_xs"],
                            "color": colors["text_secondary"],
                            "background": colors["bg_tertiary"],
                            "padding": "2px 6px",
                            "border_radius": borders["radius_sm"],
                        },
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.cond(
                    node.get("actor", "") != "",
                    rx.text(
                        node.get("actor", ""),
                        style={
                            "font_size": typography["text_xs"],
                            "color": colors["text_tertiary"],
                        },
                    ),
                    rx.fragment(),
                ),
                spacing="0",
                align="start",
            ),
            spacing="2",
            align="center",
            width="100%",
        ),
        style={
            "padding": spacing["2"],
            "margin_left": f"{depth * 24}px",
            "border_left": f"2px solid {colors['border_subtle']}",
            "cursor": "pointer",
            "_hover": {
                "background": colors["bg_hover"],
            },
        },
        on_click=lambda: ScenarioTreeState.select_path(node.get("id", "")),
    )


def scenario_tree_view(tree_data: Dict[str, Any]) -> rx.Component:
    """Complete scenario tree visualization"""
    return rx.vstack(
        # Header
        rx.hstack(
            rx.heading(
                "Scenario Tree",
                style={
                    "font_size": typography["text_lg"],
                    "font_weight": typography["weight_semibold"],
                    "color": colors["text_primary"],
                },
            ),
            rx.spacer(),
            rx.hstack(
                rx.button(
                    "Expand All",
                    style={
                        "font_size": typography["text_xs"],
                        "padding": f"{spacing['1']} {spacing['2']}",
                        "background": colors["bg_tertiary"],
                        "border": "none",
                        "border_radius": borders["radius_sm"],
                        "color": colors["text_secondary"],
                        "cursor": "pointer",
                    },
                ),
                rx.button(
                    "Collapse All",
                    style={
                        "font_size": typography["text_xs"],
                        "padding": f"{spacing['1']} {spacing['2']}",
                        "background": colors["bg_tertiary"],
                        "border": "none",
                        "border_radius": borders["radius_sm"],
                        "color": colors["text_secondary"],
                        "cursor": "pointer",
                    },
                ),
                spacing="2",
            ),
            width="100%",
        ),

        # Outcome summary
        rx.hstack(
            _outcome_pill("Favorable", tree_data.get("favorable_prob", 0), colors["success"]),
            _outcome_pill("Neutral", tree_data.get("neutral_prob", 0), colors["text_secondary"]),
            _outcome_pill("Unfavorable", tree_data.get("unfavorable_prob", 0), colors["error"]),
            spacing="2",
        ),

        # Tree content
        rx.scroll_area(
            rx.vstack(
                # Render tree nodes here
                rx.text(
                    "Tree visualization",
                    style={"color": colors["text_tertiary"]},
                ),
                spacing="0",
                width="100%",
            ),
            height="400px",
            style={
                "background": colors["bg_secondary"],
                "border": f"1px solid {colors['border_subtle']}",
                "border_radius": borders["radius_lg"],
                "padding": spacing["3"],
            },
        ),

        spacing="3",
        width="100%",
    )


def _outcome_pill(label: str, probability: float, color: str) -> rx.Component:
    """Outcome probability pill"""
    return rx.hstack(
        rx.box(
            style={
                "width": "8px",
                "height": "8px",
                "background": color,
                "border_radius": borders["radius_full"],
            },
        ),
        rx.text(
            f"{label}: {int(probability * 100)}%",
            style={
                "font_size": typography["text_xs"],
                "color": colors["text_secondary"],
            },
        ),
        style={
            "padding": f"{spacing['1']} {spacing['2']}",
            "background": colors["bg_tertiary"],
            "border_radius": borders["radius_sm"],
        },
        spacing="2",
    )


# =============================================================================
# AGENT NETWORK VISUALIZATION
# =============================================================================

class AgentNetworkState(rx.State):
    """State for agent network visualization"""
    agents: List[Dict[str, Any]] = []
    connections: List[Dict[str, Any]] = []
    selected_agent_id: Optional[str] = None
    filter_state: str = "all"  # all, converted, churned, evaluating
    show_influence_lines: bool = True

    def select_agent(self, agent_id: str):
        self.selected_agent_id = agent_id

    def set_filter(self, filter_val: str):
        self.filter_state = filter_val

    def toggle_influence_lines(self):
        self.show_influence_lines = not self.show_influence_lines


def agent_network_view(
    agents: List[Dict[str, Any]],
    show_influence: bool = True,
) -> rx.Component:
    """Force-directed agent network visualization"""
    return rx.vstack(
        # Header with filters
        rx.hstack(
            rx.heading(
                "Agent Network",
                style={
                    "font_size": typography["text_lg"],
                    "font_weight": typography["weight_semibold"],
                    "color": colors["text_primary"],
                },
            ),
            rx.spacer(),
            rx.hstack(
                _filter_button("All", "all"),
                _filter_button("Converted", "converted"),
                _filter_button("Churned", "churned"),
                _filter_button("Evaluating", "evaluating"),
                spacing="1",
            ),
            width="100%",
        ),

        # Stats bar
        rx.hstack(
            _stat_box("Total", len(agents), colors["text_secondary"]),
            _stat_box("Converted", sum(1 for a in agents if a.get("state") == "converted"), colors["success"]),
            _stat_box("Churned", sum(1 for a in agents if a.get("state") == "churned"), colors["error"]),
            spacing="3",
        ),

        # Network canvas
        rx.box(
            # D3 force-directed graph would be rendered here
            rx.center(
                rx.vstack(
                    rx.icon("network", size=48, color=colors["text_tertiary"]),
                    rx.text(
                        "Agent network visualization",
                        style={"color": colors["text_tertiary"]},
                    ),
                    spacing="3",
                    align="center",
                ),
                width="100%",
                height="100%",
            ),
            style={
                "width": "100%",
                "height": "400px",
                "background": colors["bg_secondary"],
                "border": f"1px solid {colors['border_subtle']}",
                "border_radius": borders["radius_lg"],
            },
        ),

        # Legend
        rx.hstack(
            rx.hstack(
                rx.box(
                    style={
                        "width": "10px",
                        "height": "10px",
                        "background": colors["success"],
                        "border_radius": borders["radius_full"],
                    }
                ),
                rx.text("Converted", style={"font_size": typography["text_xs"], "color": colors["text_secondary"]}),
                spacing="1",
            ),
            rx.hstack(
                rx.box(
                    style={
                        "width": "10px",
                        "height": "10px",
                        "background": colors["error"],
                        "border_radius": borders["radius_full"],
                    }
                ),
                rx.text("Churned", style={"font_size": typography["text_xs"], "color": colors["text_secondary"]}),
                spacing="1",
            ),
            rx.hstack(
                rx.box(
                    style={
                        "width": "10px",
                        "height": "10px",
                        "background": colors["warning"],
                        "border_radius": borders["radius_full"],
                    }
                ),
                rx.text("Evaluating", style={"font_size": typography["text_xs"], "color": colors["text_secondary"]}),
                spacing="1",
            ),
            spacing="4",
        ),

        spacing="3",
        width="100%",
    )


def _filter_button(label: str, value: str) -> rx.Component:
    """Filter button for agent network"""
    is_active = AgentNetworkState.filter_state == value
    return rx.button(
        label,
        on_click=lambda: AgentNetworkState.set_filter(value),
        style={
            "font_size": typography["text_xs"],
            "padding": f"{spacing['1']} {spacing['2']}",
            "background": colors["accent_muted"] if is_active else "transparent",
            "border": f"1px solid {colors['accent'] if is_active else colors['border_default']}",
            "border_radius": borders["radius_sm"],
            "color": colors["accent"] if is_active else colors["text_secondary"],
            "cursor": "pointer",
        },
    )


def _stat_box(label: str, value: int, color: str) -> rx.Component:
    """Stats box for network view"""
    return rx.vstack(
        rx.text(
            str(value),
            style={
                "font_size": typography["text_2xl"],
                "font_weight": typography["weight_bold"],
                "color": color,
            },
        ),
        rx.text(
            label,
            style={
                "font_size": typography["text_xs"],
                "color": colors["text_tertiary"],
            },
        ),
        spacing="0",
        style={
            "padding": spacing["3"],
            "background": colors["bg_secondary"],
            "border": f"1px solid {colors['border_subtle']}",
            "border_radius": borders["radius_md"],
            "min_width": "80px",
        },
    )


# =============================================================================
# TIMELINE VISUALIZATION
# =============================================================================

def timeline_view(events: List[Dict[str, Any]]) -> rx.Component:
    """Timeline visualization for decision events"""
    return rx.vstack(
        rx.heading(
            "Timeline",
            style={
                "font_size": typography["text_lg"],
                "font_weight": typography["weight_semibold"],
                "color": colors["text_primary"],
            },
        ),

        rx.vstack(
            rx.foreach(
                events,
                lambda event: _timeline_event(event),
            ),
            spacing="0",
            width="100%",
        ),

        spacing="3",
        width="100%",
    )


def _timeline_event(event: Dict[str, Any]) -> rx.Component:
    """Individual timeline event"""
    event_colors = {
        "decision": colors["accent"],
        "simulation": colors["warning"],
        "outcome": colors["success"],
        "competitor": colors["error"],
    }
    color = event_colors.get(event.get("type", ""), colors["text_secondary"])

    return rx.hstack(
        # Timeline line and dot
        rx.vstack(
            rx.box(
                style={
                    "width": "12px",
                    "height": "12px",
                    "background": color,
                    "border_radius": borders["radius_full"],
                    "border": f"2px solid {colors['bg_primary']}",
                },
            ),
            rx.box(
                style={
                    "width": "2px",
                    "height": "40px",
                    "background": colors["border_subtle"],
                },
            ),
            spacing="0",
        ),

        # Event content
        rx.vstack(
            rx.hstack(
                rx.text(
                    event.get("title", ""),
                    style={
                        "font_size": typography["text_sm"],
                        "font_weight": typography["weight_medium"],
                        "color": colors["text_primary"],
                    },
                ),
                rx.text(
                    event.get("time", ""),
                    style={
                        "font_size": typography["text_xs"],
                        "color": colors["text_tertiary"],
                    },
                ),
                spacing="2",
            ),
            rx.text(
                event.get("description", ""),
                style={
                    "font_size": typography["text_xs"],
                    "color": colors["text_secondary"],
                },
            ),
            spacing="1",
            align="start",
        ),

        spacing="3",
        align="start",
        padding=spacing["2"],
    )


# =============================================================================
# CONFIDENCE VISUALIZATION
# =============================================================================

def confidence_breakdown_view(decomposition: Dict[str, Any]) -> rx.Component:
    """Confidence decomposition visualization"""
    components = decomposition.get("components", [])
    overall = decomposition.get("overall_confidence", 0)

    return rx.vstack(
        # Header
        rx.hstack(
            rx.vstack(
                rx.text(
                    "Confidence Analysis",
                    style={
                        "font_size": typography["text_lg"],
                        "font_weight": typography["weight_semibold"],
                        "color": colors["text_primary"],
                    },
                ),
                rx.text(
                    decomposition.get("plain_english", ""),
                    style={
                        "font_size": typography["text_sm"],
                        "color": colors["text_secondary"],
                    },
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            # Overall confidence gauge
            rx.vstack(
                rx.text(
                    f"{int(overall * 100)}%",
                    style={
                        "font_size": typography["text_3xl"],
                        "font_weight": typography["weight_bold"],
                        "color": colors["success"] if overall > 0.7 else colors["warning"] if overall > 0.5 else colors["error"],
                    },
                ),
                rx.text(
                    "Overall Confidence",
                    style={
                        "font_size": typography["text_xs"],
                        "color": colors["text_tertiary"],
                    },
                ),
                spacing="0",
                align="center",
            ),
            width="100%",
        ),

        # Breakdown bars
        rx.vstack(
            rx.foreach(
                components,
                lambda c: _confidence_bar(c),
            ),
            spacing="2",
            width="100%",
        ),

        # Improvement actions
        rx.cond(
            len(decomposition.get("improvement_actions", [])) > 0,
            rx.vstack(
                rx.text(
                    "To Increase Confidence",
                    style={
                        "font_size": typography["text_sm"],
                        "font_weight": typography["weight_medium"],
                        "color": colors["text_primary"],
                    },
                ),
                rx.vstack(
                    rx.foreach(
                        decomposition.get("improvement_actions", []),
                        lambda action: rx.hstack(
                            rx.icon("arrow-right", size=12, color=colors["accent"]),
                            rx.text(
                                action,
                                style={
                                    "font_size": typography["text_xs"],
                                    "color": colors["text_secondary"],
                                },
                            ),
                            spacing="2",
                        ),
                    ),
                    spacing="1",
                ),
                spacing="2",
                style={
                    "padding": spacing["3"],
                    "background": colors["bg_tertiary"],
                    "border_radius": borders["radius_md"],
                },
            ),
            rx.fragment(),
        ),

        spacing="4",
        style={
            "padding": spacing["4"],
            "background": colors["bg_secondary"],
            "border": f"1px solid {colors['border_subtle']}",
            "border_radius": borders["radius_lg"],
        },
        width="100%",
    )


def _confidence_bar(component: Dict[str, Any]) -> rx.Component:
    """Individual confidence component bar"""
    contribution = component.get("contribution", 0)
    reducible = component.get("reducible", False)

    return rx.hstack(
        rx.text(
            component.get("name", ""),
            style={
                "font_size": typography["text_xs"],
                "color": colors["text_secondary"],
                "min_width": "120px",
            },
        ),
        rx.box(
            rx.box(
                style={
                    "width": f"{contribution * 100}%",
                    "height": "100%",
                    "background": colors["accent"] if reducible else colors["text_tertiary"],
                    "border_radius": borders["radius_sm"],
                },
            ),
            style={
                "flex": "1",
                "height": "8px",
                "background": colors["bg_tertiary"],
                "border_radius": borders["radius_sm"],
            },
        ),
        rx.text(
            f"{int(contribution * 100)}%",
            style={
                "font_size": typography["text_xs"],
                "color": colors["text_tertiary"],
                "min_width": "35px",
                "text_align": "right",
            },
        ),
        rx.cond(
            reducible,
            rx.icon("settings-2", size=10, color=colors["accent"]),
            rx.icon("lock", size=10, color=colors["text_tertiary"]),
        ),
        spacing="2",
        width="100%",
    )


# =============================================================================
# CAUSAL TRACE VISUALIZATION
# =============================================================================

def causal_trace_view(trace_data: Dict[str, Any]) -> rx.Component:
    """DAG visualization for causal relationships"""
    return rx.vstack(
        rx.heading(
            "Causal Trace",
            style={
                "font_size": typography["text_lg"],
                "font_weight": typography["weight_semibold"],
                "color": colors["text_primary"],
            },
        ),

        rx.text(
            "How this outcome came to be",
            style={
                "font_size": typography["text_sm"],
                "color": colors["text_secondary"],
            },
        ),

        # DAG visualization
        rx.box(
            rx.center(
                rx.vstack(
                    rx.icon("git-commit-vertical", size=48, color=colors["text_tertiary"]),
                    rx.text(
                        "Causal DAG visualization",
                        style={"color": colors["text_tertiary"]},
                    ),
                    spacing="3",
                    align="center",
                ),
                width="100%",
                height="100%",
            ),
            style={
                "width": "100%",
                "height": "300px",
                "background": colors["bg_secondary"],
                "border": f"1px solid {colors['border_subtle']}",
                "border_radius": borders["radius_lg"],
            },
        ),

        spacing="3",
        width="100%",
    )
