"""
Node Components for Canvas
Workflow nodes and entity nodes for the hybrid UI
"""

import reflex as rx
from typing import Dict, Any, List, Optional
from enum import Enum
from ..design_system import colors, borders, shadows, typography, spacing


# =============================================================================
# NODE TYPES
# =============================================================================

class NodeType(str, Enum):
    """Types of nodes in the canvas"""
    # Workflow nodes (process steps)
    RESEARCH = "research"
    DECISION = "decision"
    SIMULATION = "simulation"
    ANALYSIS = "analysis"
    RECOMMENDATION = "recommendation"

    # Entity nodes (data objects)
    COMPANY = "company"
    COMPETITOR = "competitor"
    AGENT = "agent"
    SCENARIO = "scenario"
    OUTCOME = "outcome"


class ConnectionType(str, Enum):
    """Types of connections between nodes"""
    DATA_FLOW = "data_flow"        # Data passes between nodes
    DEPENDENCY = "dependency"       # One node depends on another
    INFLUENCE = "influence"         # One entity influences another
    TEMPORAL = "temporal"           # Time-based relationship


# =============================================================================
# NODE STYLES
# =============================================================================

NODE_ICONS = {
    NodeType.RESEARCH: "search",
    NodeType.DECISION: "git-branch",
    NodeType.SIMULATION: "play",
    NodeType.ANALYSIS: "bar-chart-3",
    NodeType.RECOMMENDATION: "lightbulb",
    NodeType.COMPANY: "building-2",
    NodeType.COMPETITOR: "swords",
    NodeType.AGENT: "user",
    NodeType.SCENARIO: "git-fork",
    NodeType.OUTCOME: "target",
}

NODE_COLORS = {
    # Workflow nodes - accent colors
    NodeType.RESEARCH: colors["info"],
    NodeType.DECISION: colors["accent"],
    NodeType.SIMULATION: colors["warning"],
    NodeType.ANALYSIS: colors["success"],
    NodeType.RECOMMENDATION: "#A855F7",  # Purple

    # Entity nodes - neutral colors
    NodeType.COMPANY: colors["text_secondary"],
    NodeType.COMPETITOR: colors["error"],
    NodeType.AGENT: colors["accent"],
    NodeType.SCENARIO: colors["info"],
    NodeType.OUTCOME: colors["success"],
}


def get_node_style(node_type: NodeType, selected: bool = False, hover: bool = False) -> Dict[str, Any]:
    """Get styles for a node based on type and state"""
    color = NODE_COLORS.get(node_type, colors["accent"])

    base_style = {
        "background": colors["bg_secondary"],
        "border": f"1px solid {colors['border_default']}",
        "border_radius": borders["radius_lg"],
        "padding": spacing["3"],
        "cursor": "pointer",
        "transition": "all 0.15s ease-out",
        "position": "relative",
    }

    if selected:
        base_style.update({
            "border": f"2px solid {color}",
            "box_shadow": f"0 0 0 3px {color}20",
        })
    elif hover:
        base_style.update({
            "border": f"1px solid {color}40",
            "box_shadow": shadows["md"],
        })

    return base_style


# =============================================================================
# BASE NODE COMPONENT
# =============================================================================

def base_node(
    node_id: str,
    node_type: NodeType,
    title: str,
    subtitle: str = "",
    status: str = "",
    selected: bool = False,
    on_click: Optional[callable] = None,
    on_double_click: Optional[callable] = None,
) -> rx.Component:
    """Base node component"""
    color = NODE_COLORS.get(node_type, colors["accent"])
    icon = NODE_ICONS.get(node_type, "circle")

    return rx.box(
        # Status indicator dot
        rx.cond(
            status != "",
            rx.box(
                style={
                    "position": "absolute",
                    "top": "8px",
                    "right": "8px",
                    "width": "8px",
                    "height": "8px",
                    "border_radius": borders["radius_full"],
                    "background": colors["success"] if status == "complete" else colors["warning"],
                }
            ),
            rx.fragment(),
        ),

        rx.hstack(
            # Icon
            rx.box(
                rx.icon(icon, size=16, color=color),
                style={
                    "padding": spacing["2"],
                    "background": f"{color}15",
                    "border_radius": borders["radius_md"],
                },
            ),

            # Content
            rx.vstack(
                rx.text(
                    title,
                    style={
                        "font_size": typography["text_sm"],
                        "font_weight": typography["weight_medium"],
                        "color": colors["text_primary"],
                        "line_height": typography["leading_tight"],
                    },
                ),
                rx.cond(
                    subtitle != "",
                    rx.text(
                        subtitle,
                        style={
                            "font_size": typography["text_xs"],
                            "color": colors["text_secondary"],
                        },
                    ),
                    rx.fragment(),
                ),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
        ),

        # Connection handles
        _connection_handles(node_type),

        style=get_node_style(node_type, selected),
        on_click=on_click,
        on_double_click=on_double_click,
        data_node_id=node_id,
        data_node_type=node_type.value,
    )


def _connection_handles(node_type: NodeType) -> rx.Component:
    """Connection handles for node edges"""
    handle_style = {
        "width": "10px",
        "height": "10px",
        "background": colors["bg_tertiary"],
        "border": f"2px solid {colors['border_strong']}",
        "border_radius": borders["radius_full"],
        "position": "absolute",
        "cursor": "crosshair",
        "_hover": {
            "background": colors["accent"],
            "border_color": colors["accent"],
        },
    }

    return rx.fragment(
        # Left handle (input)
        rx.box(
            style={
                **handle_style,
                "left": "-5px",
                "top": "50%",
                "transform": "translateY(-50%)",
            },
        ),
        # Right handle (output)
        rx.box(
            style={
                **handle_style,
                "right": "-5px",
                "top": "50%",
                "transform": "translateY(-50%)",
            },
        ),
    )


# =============================================================================
# WORKFLOW NODES
# =============================================================================

def research_node(
    node_id: str,
    company_name: str = "",
    status: str = "pending",
    progress: float = 0,
    selected: bool = False,
    on_click: Optional[callable] = None,
) -> rx.Component:
    """Research workflow node"""
    return rx.box(
        base_node(
            node_id=node_id,
            node_type=NodeType.RESEARCH,
            title="Company Research",
            subtitle=company_name or "Enter company name",
            status=status,
            selected=selected,
            on_click=on_click,
        ),

        # Progress bar
        rx.cond(
            progress > 0,
            rx.box(
                rx.box(
                    style={
                        "width": f"{progress * 100}%",
                        "height": "100%",
                        "background": colors["info"],
                        "border_radius": borders["radius_full"],
                    },
                ),
                style={
                    "width": "100%",
                    "height": "3px",
                    "background": colors["bg_tertiary"],
                    "border_radius": borders["radius_full"],
                    "margin_top": spacing["2"],
                },
            ),
            rx.fragment(),
        ),
    )


def decision_node(
    node_id: str,
    decision_title: str = "",
    options_count: int = 0,
    status: str = "pending",
    selected: bool = False,
    on_click: Optional[callable] = None,
) -> rx.Component:
    """Decision workflow node"""
    return rx.box(
        base_node(
            node_id=node_id,
            node_type=NodeType.DECISION,
            title="Decision Point",
            subtitle=decision_title or "Define your decision",
            status=status,
            selected=selected,
            on_click=on_click,
        ),

        # Options indicator
        rx.cond(
            options_count > 0,
            rx.hstack(
                rx.icon("list", size=12, color=colors["text_tertiary"]),
                rx.text(
                    f"{options_count} options",
                    style={
                        "font_size": typography["text_xs"],
                        "color": colors["text_tertiary"],
                    },
                ),
                spacing="1",
                margin_top=spacing["2"],
            ),
            rx.fragment(),
        ),
    )


def simulation_node(
    node_id: str,
    simulation_name: str = "",
    agents_count: int = 0,
    branches_count: int = 0,
    status: str = "pending",
    selected: bool = False,
    on_click: Optional[callable] = None,
) -> rx.Component:
    """Simulation workflow node"""
    return rx.box(
        base_node(
            node_id=node_id,
            node_type=NodeType.SIMULATION,
            title="Run Simulation",
            subtitle=simulation_name or "Configure simulation",
            status=status,
            selected=selected,
            on_click=on_click,
        ),

        # Simulation stats
        rx.cond(
            agents_count > 0,
            rx.hstack(
                rx.hstack(
                    rx.icon("users", size=10, color=colors["text_tertiary"]),
                    rx.text(
                        f"{agents_count:,}",
                        style={
                            "font_size": typography["text_xs"],
                            "color": colors["text_tertiary"],
                        },
                    ),
                    spacing="1",
                ),
                rx.hstack(
                    rx.icon("git-branch", size=10, color=colors["text_tertiary"]),
                    rx.text(
                        f"{branches_count}",
                        style={
                            "font_size": typography["text_xs"],
                            "color": colors["text_tertiary"],
                        },
                    ),
                    spacing="1",
                ),
                spacing="3",
                margin_top=spacing["2"],
            ),
            rx.fragment(),
        ),
    )


def analysis_node(
    node_id: str,
    analysis_type: str = "",
    confidence: float = 0,
    status: str = "pending",
    selected: bool = False,
    on_click: Optional[callable] = None,
) -> rx.Component:
    """Analysis workflow node"""
    return rx.box(
        base_node(
            node_id=node_id,
            node_type=NodeType.ANALYSIS,
            title="Analyze Results",
            subtitle=analysis_type or "View analysis",
            status=status,
            selected=selected,
            on_click=on_click,
        ),

        # Confidence indicator
        rx.cond(
            confidence > 0,
            rx.hstack(
                rx.text(
                    f"{int(confidence * 100)}% confidence",
                    style={
                        "font_size": typography["text_xs"],
                        "color": colors["success"] if confidence > 0.7 else colors["warning"],
                    },
                ),
                margin_top=spacing["2"],
            ),
            rx.fragment(),
        ),
    )


def recommendation_node(
    node_id: str,
    recommendation: str = "",
    status: str = "pending",
    selected: bool = False,
    on_click: Optional[callable] = None,
) -> rx.Component:
    """Recommendation workflow node"""
    return base_node(
        node_id=node_id,
        node_type=NodeType.RECOMMENDATION,
        title="Recommendation",
        subtitle=recommendation or "View recommendation",
        status=status,
        selected=selected,
        on_click=on_click,
    )


# =============================================================================
# ENTITY NODES
# =============================================================================

def company_node(
    node_id: str,
    company_name: str,
    industry: str = "",
    is_target: bool = False,
    selected: bool = False,
    on_click: Optional[callable] = None,
) -> rx.Component:
    """Company entity node"""
    color = colors["accent"] if is_target else colors["text_secondary"]

    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon("building-2", size=16, color=color),
                style={
                    "padding": spacing["2"],
                    "background": f"{color}15",
                    "border_radius": borders["radius_md"],
                },
            ),
            rx.vstack(
                rx.text(
                    company_name,
                    style={
                        "font_size": typography["text_sm"],
                        "font_weight": typography["weight_medium"],
                        "color": colors["text_primary"],
                    },
                ),
                rx.cond(
                    industry != "",
                    rx.text(
                        industry,
                        style={
                            "font_size": typography["text_xs"],
                            "color": colors["text_secondary"],
                        },
                    ),
                    rx.fragment(),
                ),
                spacing="0",
                align="start",
            ),
            rx.cond(
                is_target,
                rx.box(
                    rx.text(
                        "Target",
                        style={
                            "font_size": "9px",
                            "color": colors["accent"],
                            "text_transform": "uppercase",
                            "letter_spacing": "0.05em",
                        },
                    ),
                    style={
                        "padding": "2px 6px",
                        "background": colors["accent_muted"],
                        "border_radius": borders["radius_sm"],
                    },
                ),
                rx.fragment(),
            ),
            spacing="3",
            align="center",
        ),
        style=get_node_style(NodeType.COMPANY, selected),
        on_click=on_click,
    )


def competitor_node(
    node_id: str,
    competitor_name: str,
    strategy_type: str = "",
    threat_level: str = "medium",
    selected: bool = False,
    on_click: Optional[callable] = None,
) -> rx.Component:
    """Competitor entity node"""
    threat_colors = {
        "high": colors["error"],
        "medium": colors["warning"],
        "low": colors["success"],
    }
    threat_color = threat_colors.get(threat_level, colors["warning"])

    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon("swords", size=16, color=threat_color),
                style={
                    "padding": spacing["2"],
                    "background": f"{threat_color}15",
                    "border_radius": borders["radius_md"],
                },
            ),
            rx.vstack(
                rx.text(
                    competitor_name,
                    style={
                        "font_size": typography["text_sm"],
                        "font_weight": typography["weight_medium"],
                        "color": colors["text_primary"],
                    },
                ),
                rx.cond(
                    strategy_type != "",
                    rx.text(
                        strategy_type,
                        style={
                            "font_size": typography["text_xs"],
                            "color": colors["text_secondary"],
                        },
                    ),
                    rx.fragment(),
                ),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
        ),

        # Threat indicator
        rx.box(
            style={
                "position": "absolute",
                "top": "-3px",
                "right": "-3px",
                "width": "8px",
                "height": "8px",
                "background": threat_color,
                "border_radius": borders["radius_full"],
                "border": f"2px solid {colors['bg_secondary']}",
            },
        ),

        style={
            **get_node_style(NodeType.COMPETITOR, selected),
            "position": "relative",
        },
        on_click=on_click,
    )


def agent_node(
    node_id: str,
    agent_name: str,
    role: str = "",
    state: str = "",
    selected: bool = False,
    on_click: Optional[callable] = None,
) -> rx.Component:
    """Agent entity node (smaller, for network view)"""
    state_colors = {
        "converted": colors["success"],
        "churned": colors["error"],
        "evaluating": colors["warning"],
        "unaware": colors["text_tertiary"],
    }
    state_color = state_colors.get(state, colors["text_secondary"])

    return rx.box(
        rx.vstack(
            rx.box(
                rx.text(
                    agent_name[0] if agent_name else "?",
                    style={
                        "font_size": typography["text_xs"],
                        "font_weight": typography["weight_semibold"],
                        "color": colors["text_primary"],
                    },
                ),
                style={
                    "width": "24px",
                    "height": "24px",
                    "background": f"{state_color}20",
                    "border": f"2px solid {state_color}",
                    "border_radius": borders["radius_full"],
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                },
            ),
            rx.text(
                agent_name,
                style={
                    "font_size": "9px",
                    "color": colors["text_secondary"],
                    "max_width": "60px",
                    "overflow": "hidden",
                    "text_overflow": "ellipsis",
                    "white_space": "nowrap",
                },
            ),
            spacing="1",
            align="center",
        ),
        style={
            "padding": spacing["1"],
            "cursor": "pointer",
            "_hover": {
                "background": colors["bg_hover"],
            },
            "border_radius": borders["radius_md"],
        },
        on_click=on_click,
    )


def scenario_node(
    node_id: str,
    scenario_name: str,
    probability: float = 0,
    outcome: str = "",
    selected: bool = False,
    on_click: Optional[callable] = None,
) -> rx.Component:
    """Scenario entity node"""
    outcome_colors = {
        "favorable": colors["success"],
        "unfavorable": colors["error"],
        "neutral": colors["text_secondary"],
    }
    outcome_color = outcome_colors.get(outcome, colors["info"])

    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon("git-fork", size=16, color=outcome_color),
                style={
                    "padding": spacing["2"],
                    "background": f"{outcome_color}15",
                    "border_radius": borders["radius_md"],
                },
            ),
            rx.vstack(
                rx.text(
                    scenario_name,
                    style={
                        "font_size": typography["text_sm"],
                        "font_weight": typography["weight_medium"],
                        "color": colors["text_primary"],
                    },
                ),
                rx.cond(
                    probability > 0,
                    rx.text(
                        f"{int(probability * 100)}% probability",
                        style={
                            "font_size": typography["text_xs"],
                            "color": colors["text_secondary"],
                        },
                    ),
                    rx.fragment(),
                ),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
        ),
        style=get_node_style(NodeType.SCENARIO, selected),
        on_click=on_click,
    )


# =============================================================================
# EDGE COMPONENT
# =============================================================================

def edge_line(
    from_x: float,
    from_y: float,
    to_x: float,
    to_y: float,
    connection_type: ConnectionType = ConnectionType.DATA_FLOW,
    label: str = "",
    animated: bool = False,
) -> rx.Component:
    """Edge/connection line between nodes"""
    type_colors = {
        ConnectionType.DATA_FLOW: colors["accent"],
        ConnectionType.DEPENDENCY: colors["text_tertiary"],
        ConnectionType.INFLUENCE: colors["warning"],
        ConnectionType.TEMPORAL: colors["info"],
    }
    color = type_colors.get(connection_type, colors["border_default"])

    # Calculate control points for bezier curve
    mid_x = (from_x + to_x) / 2
    ctrl_offset = abs(to_x - from_x) * 0.5

    path = f"M {from_x} {from_y} C {from_x + ctrl_offset} {from_y}, {to_x - ctrl_offset} {to_y}, {to_x} {to_y}"

    return rx.html(
        f"""
        <svg style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; overflow: visible;">
            <defs>
                <marker id="arrowhead-{connection_type.value}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="{color}" />
                </marker>
            </defs>
            <path
                d="{path}"
                stroke="{color}"
                stroke-width="2"
                fill="none"
                marker-end="url(#arrowhead-{connection_type.value})"
                {"stroke-dasharray='5,5'" if connection_type == ConnectionType.DEPENDENCY else ""}
            />
            {"<text x='" + str(mid_x) + "' y='" + str((from_y + to_y) / 2 - 8) + "' fill='" + colors['text_tertiary'] + "' font-size='10' text-anchor='middle'>" + label + "</text>" if label else ""}
        </svg>
        """
    )
