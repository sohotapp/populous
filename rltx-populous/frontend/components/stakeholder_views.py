"""
Stakeholder Views
Tailored presentations for different executive audiences
CEO, CFO, CTO, Board, Team views with appropriate detail levels
"""

import reflex as rx
from typing import Dict, Any, List, Optional
from enum import Enum
from ..design_system import colors, borders, shadows, typography, spacing


# =============================================================================
# STAKEHOLDER TYPES
# =============================================================================

class StakeholderType(str, Enum):
    """Types of stakeholder views"""
    CEO = "ceo"           # High-level strategic view
    CFO = "cfo"           # Financial impact focus
    CTO = "cto"           # Technical and risk focus
    BOARD = "board"       # Executive summary
    TEAM = "team"         # Detailed implementation view


# View configurations
STAKEHOLDER_CONFIG = {
    StakeholderType.CEO: {
        "title": "Executive Strategic View",
        "focus": ["Strategic impact", "Market position", "Key risks"],
        "detail_level": "high",
        "metrics": ["market_share", "competitive_position", "revenue_impact"],
        "icon": "crown",
    },
    StakeholderType.CFO: {
        "title": "Financial Impact Analysis",
        "focus": ["Revenue impact", "Cost implications", "ROI"],
        "detail_level": "high",
        "metrics": ["revenue_impact", "cost_estimate", "roi", "payback_period"],
        "icon": "dollar-sign",
    },
    StakeholderType.CTO: {
        "title": "Technical Risk Assessment",
        "focus": ["Technical risks", "Implementation complexity", "Dependencies"],
        "detail_level": "detailed",
        "metrics": ["risk_exposure", "complexity_score", "integration_effort"],
        "icon": "cpu",
    },
    StakeholderType.BOARD: {
        "title": "Board Summary",
        "focus": ["Strategic recommendation", "Key numbers", "Risk/reward"],
        "detail_level": "summary",
        "metrics": ["headline_metric", "confidence", "recommendation"],
        "icon": "users",
    },
    StakeholderType.TEAM: {
        "title": "Implementation Details",
        "focus": ["Action items", "Timeline", "Resource needs"],
        "detail_level": "full",
        "metrics": ["all"],
        "icon": "layout-list",
    },
}


# =============================================================================
# STAKEHOLDER VIEW STATE
# =============================================================================

class StakeholderViewState(rx.State):
    """State for stakeholder views"""
    current_view: str = "ceo"
    presentation_mode: bool = False
    current_slide: int = 0
    total_slides: int = 5

    def set_view(self, view: str):
        self.current_view = view

    def toggle_presentation_mode(self):
        self.presentation_mode = not self.presentation_mode
        self.current_slide = 0

    def next_slide(self):
        if self.current_slide < self.total_slides - 1:
            self.current_slide += 1

    def prev_slide(self):
        if self.current_slide > 0:
            self.current_slide -= 1

    def go_to_slide(self, index: int):
        self.current_slide = index


# =============================================================================
# VIEW SELECTOR
# =============================================================================

def stakeholder_selector() -> rx.Component:
    """Selector for different stakeholder views"""
    return rx.hstack(
        rx.foreach(
            list(StakeholderType),
            lambda st: _stakeholder_tab(st),
        ),
        spacing="1",
        style={
            "padding": spacing["2"],
            "background": colors["bg_secondary"],
            "border_radius": borders["radius_lg"],
            "border": f"1px solid {colors['border_subtle']}",
        },
    )


def _stakeholder_tab(stakeholder_type: StakeholderType) -> rx.Component:
    """Individual stakeholder tab"""
    config = STAKEHOLDER_CONFIG.get(stakeholder_type, {})
    is_active = StakeholderViewState.current_view == stakeholder_type.value

    return rx.button(
        rx.hstack(
            rx.icon(config.get("icon", "user"), size=14),
            rx.text(
                stakeholder_type.value.upper(),
                style={
                    "font_size": typography["text_xs"],
                    "font_weight": typography["weight_medium"],
                },
            ),
            spacing="2",
        ),
        on_click=lambda: StakeholderViewState.set_view(stakeholder_type.value),
        style={
            "padding": f"{spacing['2']} {spacing['3']}",
            "background": colors["accent"] if is_active else "transparent",
            "border": "none",
            "border_radius": borders["radius_md"],
            "color": colors["text_primary"] if is_active else colors["text_secondary"],
            "cursor": "pointer",
            "_hover": {
                "background": colors["bg_hover"] if not is_active else colors["accent"],
            },
        },
    )


# =============================================================================
# CEO VIEW
# =============================================================================

def ceo_view(data: Dict[str, Any]) -> rx.Component:
    """CEO strategic view - high-level impact focus"""
    return rx.vstack(
        # Header
        rx.hstack(
            rx.vstack(
                rx.heading(
                    "Strategic Impact Summary",
                    style={
                        "font_size": typography["text_2xl"],
                        "font_weight": typography["weight_bold"],
                        "color": colors["text_primary"],
                    },
                ),
                rx.text(
                    data.get("decision_title", "Decision Analysis"),
                    style={
                        "font_size": typography["text_md"],
                        "color": colors["text_secondary"],
                    },
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            _recommendation_badge(data.get("recommendation", "proceed")),
            width="100%",
        ),

        # Key insight
        rx.box(
            rx.text(
                data.get("headline", "Analysis complete"),
                style={
                    "font_size": typography["text_lg"],
                    "color": colors["text_primary"],
                    "line_height": typography["leading_relaxed"],
                },
            ),
            style={
                "padding": spacing["4"],
                "background": f"linear-gradient(135deg, {colors['accent_muted']}, {colors['bg_tertiary']})",
                "border_radius": borders["radius_lg"],
                "border_left": f"4px solid {colors['accent']}",
            },
        ),

        # Key metrics
        rx.hstack(
            _metric_card(
                "Win Probability",
                f"{int(data.get('win_probability', 0) * 100)}%",
                data.get('win_probability', 0) > 0.5,
            ),
            _metric_card(
                "Market Position",
                data.get('market_position', 'Neutral'),
                data.get('market_position') == 'Improved',
            ),
            _metric_card(
                "Revenue Impact",
                f"{data.get('revenue_impact', 0):+.1f}%",
                data.get('revenue_impact', 0) > 0,
            ),
            spacing="4",
            width="100%",
        ),

        # Key risks
        rx.vstack(
            rx.text(
                "Key Risks to Monitor",
                style={
                    "font_size": typography["text_sm"],
                    "font_weight": typography["weight_semibold"],
                    "color": colors["text_primary"],
                },
            ),
            rx.hstack(
                rx.foreach(
                    data.get("key_risks", [])[:3],
                    lambda risk: _risk_pill(risk),
                ),
                spacing="2",
            ),
            spacing="2",
            align="start",
            width="100%",
        ),

        spacing="6",
        width="100%",
    )


# =============================================================================
# CFO VIEW
# =============================================================================

def cfo_view(data: Dict[str, Any]) -> rx.Component:
    """CFO financial impact view"""
    return rx.vstack(
        # Header
        rx.heading(
            "Financial Impact Analysis",
            style={
                "font_size": typography["text_2xl"],
                "font_weight": typography["weight_bold"],
                "color": colors["text_primary"],
            },
        ),

        # Financial metrics
        rx.grid(
            _financial_metric_card(
                "Revenue Impact",
                f"${data.get('revenue_impact_dollars', 0):,.0f}",
                data.get('revenue_impact_percent', 0),
            ),
            _financial_metric_card(
                "Implementation Cost",
                f"${data.get('implementation_cost', 0):,.0f}",
                None,
            ),
            _financial_metric_card(
                "Expected ROI",
                f"{data.get('roi', 0):.1f}x",
                data.get('roi', 0) - 1,
            ),
            _financial_metric_card(
                "Payback Period",
                f"{data.get('payback_months', 0)} months",
                None,
            ),
            columns="2",
            spacing="4",
            width="100%",
        ),

        # Scenario analysis
        rx.vstack(
            rx.text(
                "Scenario Analysis",
                style={
                    "font_size": typography["text_lg"],
                    "font_weight": typography["weight_semibold"],
                    "color": colors["text_primary"],
                },
            ),
            rx.hstack(
                _scenario_bar("Best Case", data.get("best_case_revenue", 0), colors["success"]),
                _scenario_bar("Expected", data.get("expected_revenue", 0), colors["accent"]),
                _scenario_bar("Worst Case", data.get("worst_case_revenue", 0), colors["error"]),
                spacing="4",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),

        spacing="6",
        width="100%",
    )


# =============================================================================
# CTO VIEW
# =============================================================================

def cto_view(data: Dict[str, Any]) -> rx.Component:
    """CTO technical risk view"""
    return rx.vstack(
        # Header
        rx.heading(
            "Technical Risk Assessment",
            style={
                "font_size": typography["text_2xl"],
                "font_weight": typography["weight_bold"],
                "color": colors["text_primary"],
            },
        ),

        # Risk matrix
        rx.hstack(
            _risk_card("Technical Risk", data.get("technical_risk", 0.3)),
            _risk_card("Integration Complexity", data.get("integration_complexity", 0.5)),
            _risk_card("Execution Risk", data.get("execution_risk", 0.4)),
            spacing="4",
            width="100%",
        ),

        # Dependencies
        rx.vstack(
            rx.text(
                "Critical Dependencies",
                style={
                    "font_size": typography["text_md"],
                    "font_weight": typography["weight_semibold"],
                    "color": colors["text_primary"],
                },
            ),
            rx.vstack(
                rx.foreach(
                    data.get("dependencies", []),
                    lambda dep: _dependency_item(dep),
                ),
                spacing="2",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),

        # Confidence breakdown
        rx.vstack(
            rx.text(
                "Uncertainty Sources",
                style={
                    "font_size": typography["text_md"],
                    "font_weight": typography["weight_semibold"],
                    "color": colors["text_primary"],
                },
            ),
            # Confidence visualization would go here
            spacing="3",
            width="100%",
        ),

        spacing="6",
        width="100%",
    )


# =============================================================================
# BOARD VIEW
# =============================================================================

def board_view(data: Dict[str, Any]) -> rx.Component:
    """Board summary view - executive digest"""
    return rx.vstack(
        # One-liner
        rx.box(
            rx.vstack(
                rx.text(
                    "RECOMMENDATION",
                    style={
                        "font_size": typography["text_xs"],
                        "font_weight": typography["weight_semibold"],
                        "color": colors["accent"],
                        "letter_spacing": "0.1em",
                    },
                ),
                rx.heading(
                    data.get("recommendation_headline", "Proceed with Strategy A"),
                    style={
                        "font_size": typography["text_3xl"],
                        "font_weight": typography["weight_bold"],
                        "color": colors["text_primary"],
                    },
                ),
                spacing="2",
                align="center",
            ),
            style={
                "padding": spacing["6"],
                "background": colors["bg_secondary"],
                "border_radius": borders["radius_xl"],
                "border": f"1px solid {colors['border_subtle']}",
                "text_align": "center",
            },
            width="100%",
        ),

        # Three key numbers
        rx.hstack(
            _board_metric(
                "Success Probability",
                f"{int(data.get('success_probability', 0) * 100)}%",
                "Target: >70%",
            ),
            _board_metric(
                "Expected Return",
                f"${data.get('expected_return', 0):,.0f}",
                f"Risk-adjusted",
            ),
            _board_metric(
                "Confidence Level",
                data.get("confidence_level", "High"),
                f"{int(data.get('confidence', 0) * 100)}% certainty",
            ),
            spacing="4",
            width="100%",
        ),

        # Risk/Reward summary
        rx.hstack(
            rx.vstack(
                rx.text(
                    "UPSIDE",
                    style={
                        "font_size": typography["text_xs"],
                        "color": colors["success"],
                        "font_weight": typography["weight_semibold"],
                    },
                ),
                rx.text(
                    data.get("upside_summary", "Market share gains"),
                    style={
                        "font_size": typography["text_sm"],
                        "color": colors["text_secondary"],
                    },
                ),
                spacing="1",
                align="start",
                style={
                    "padding": spacing["3"],
                    "background": colors["success_muted"],
                    "border_radius": borders["radius_md"],
                    "flex": "1",
                },
            ),
            rx.vstack(
                rx.text(
                    "DOWNSIDE",
                    style={
                        "font_size": typography["text_xs"],
                        "color": colors["error"],
                        "font_weight": typography["weight_semibold"],
                    },
                ),
                rx.text(
                    data.get("downside_summary", "Competitive response risk"),
                    style={
                        "font_size": typography["text_sm"],
                        "color": colors["text_secondary"],
                    },
                ),
                spacing="1",
                align="start",
                style={
                    "padding": spacing["3"],
                    "background": colors["error_muted"],
                    "border_radius": borders["radius_md"],
                    "flex": "1",
                },
            ),
            spacing="4",
            width="100%",
        ),

        spacing="6",
        width="100%",
    )


# =============================================================================
# TEAM VIEW
# =============================================================================

def team_view(data: Dict[str, Any]) -> rx.Component:
    """Team implementation view - detailed action items"""
    return rx.vstack(
        # Header
        rx.heading(
            "Implementation Plan",
            style={
                "font_size": typography["text_2xl"],
                "font_weight": typography["weight_bold"],
                "color": colors["text_primary"],
            },
        ),

        # Action items
        rx.vstack(
            rx.text(
                "Action Items",
                style={
                    "font_size": typography["text_md"],
                    "font_weight": typography["weight_semibold"],
                    "color": colors["text_primary"],
                },
            ),
            rx.vstack(
                rx.foreach(
                    data.get("action_items", []),
                    lambda item: _action_item(item),
                ),
                spacing="2",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),

        # Timeline
        rx.vstack(
            rx.text(
                "Key Milestones",
                style={
                    "font_size": typography["text_md"],
                    "font_weight": typography["weight_semibold"],
                    "color": colors["text_primary"],
                },
            ),
            rx.vstack(
                rx.foreach(
                    data.get("milestones", []),
                    lambda milestone: _milestone_item(milestone),
                ),
                spacing="0",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),

        spacing="6",
        width="100%",
    )


# =============================================================================
# PRESENTATION MODE
# =============================================================================

def presentation_mode_controls() -> rx.Component:
    """Controls for presentation mode"""
    return rx.cond(
        StakeholderViewState.presentation_mode,
        rx.hstack(
            rx.button(
                rx.icon("chevron-left", size=20),
                on_click=StakeholderViewState.prev_slide,
                style=_presentation_button_style(),
                disabled=StakeholderViewState.current_slide == 0,
            ),
            rx.text(
                f"{StakeholderViewState.current_slide + 1} / {StakeholderViewState.total_slides}",
                style={
                    "font_size": typography["text_md"],
                    "color": colors["text_secondary"],
                },
            ),
            rx.button(
                rx.icon("chevron-right", size=20),
                on_click=StakeholderViewState.next_slide,
                style=_presentation_button_style(),
                disabled=StakeholderViewState.current_slide == StakeholderViewState.total_slides - 1,
            ),
            rx.spacer(),
            rx.button(
                "Exit",
                on_click=StakeholderViewState.toggle_presentation_mode,
                style={
                    "padding": f"{spacing['2']} {spacing['4']}",
                    "background": colors["bg_tertiary"],
                    "border": f"1px solid {colors['border_default']}",
                    "border_radius": borders["radius_md"],
                    "color": colors["text_primary"],
                    "cursor": "pointer",
                },
            ),
            position="fixed",
            bottom="24px",
            left="50%",
            transform="translateX(-50%)",
            padding="3",
            background=colors["bg_secondary"],
            border=f"1px solid {colors['border_default']}",
            border_radius=borders["radius_lg"],
            box_shadow=shadows["lg"],
            z_index="1000",
            spacing="4",
            align="center",
        ),
        rx.fragment(),
    )


def _presentation_button_style() -> Dict[str, Any]:
    return {
        "padding": spacing["2"],
        "background": "transparent",
        "border": "none",
        "color": colors["text_secondary"],
        "cursor": "pointer",
        "_hover": {
            "color": colors["text_primary"],
        },
        "_disabled": {
            "opacity": "0.5",
            "cursor": "not-allowed",
        },
    }


def presentation_button() -> rx.Component:
    """Button to enter presentation mode"""
    return rx.button(
        rx.icon("presentation", size=16),
        "Present",
        on_click=StakeholderViewState.toggle_presentation_mode,
        style={
            "padding": f"{spacing['2']} {spacing['3']}",
            "background": colors["accent"],
            "border": "none",
            "border_radius": borders["radius_md"],
            "color": colors["text_primary"],
            "cursor": "pointer",
            "display": "flex",
            "align_items": "center",
            "gap": spacing["2"],
        },
    )


# =============================================================================
# HELPER COMPONENTS
# =============================================================================

def _metric_card(label: str, value: str, is_positive: bool) -> rx.Component:
    """Metric card for dashboard"""
    color = colors["success"] if is_positive else colors["error"]
    return rx.vstack(
        rx.text(
            label,
            style={
                "font_size": typography["text_xs"],
                "color": colors["text_tertiary"],
                "text_transform": "uppercase",
            },
        ),
        rx.text(
            value,
            style={
                "font_size": typography["text_2xl"],
                "font_weight": typography["weight_bold"],
                "color": color if is_positive is not None else colors["text_primary"],
            },
        ),
        spacing="1",
        style={
            "padding": spacing["4"],
            "background": colors["bg_secondary"],
            "border": f"1px solid {colors['border_subtle']}",
            "border_radius": borders["radius_lg"],
            "flex": "1",
        },
    )


def _recommendation_badge(recommendation: str) -> rx.Component:
    """Recommendation badge"""
    badge_colors = {
        "proceed": colors["success"],
        "caution": colors["warning"],
        "hold": colors["error"],
    }
    color = badge_colors.get(recommendation, colors["text_secondary"])

    return rx.box(
        rx.text(
            recommendation.upper(),
            style={
                "font_size": typography["text_xs"],
                "font_weight": typography["weight_semibold"],
                "color": color,
            },
        ),
        style={
            "padding": f"{spacing['1']} {spacing['3']}",
            "background": f"{color}20",
            "border": f"1px solid {color}40",
            "border_radius": borders["radius_full"],
        },
    )


def _risk_pill(risk: str) -> rx.Component:
    """Risk indicator pill"""
    return rx.box(
        rx.text(
            risk,
            style={
                "font_size": typography["text_xs"],
                "color": colors["warning"],
            },
        ),
        style={
            "padding": f"{spacing['1']} {spacing['2']}",
            "background": colors["warning_muted"],
            "border_radius": borders["radius_sm"],
        },
    )


def _financial_metric_card(
    label: str,
    value: str,
    change: Optional[float]
) -> rx.Component:
    """Financial metric card with optional change indicator"""
    return rx.vstack(
        rx.text(
            label,
            style={
                "font_size": typography["text_xs"],
                "color": colors["text_tertiary"],
            },
        ),
        rx.text(
            value,
            style={
                "font_size": typography["text_xl"],
                "font_weight": typography["weight_bold"],
                "color": colors["text_primary"],
            },
        ),
        rx.cond(
            change is not None,
            rx.text(
                f"{change:+.1f}%",
                style={
                    "font_size": typography["text_xs"],
                    "color": colors["success"] if change > 0 else colors["error"],
                },
            ),
            rx.fragment(),
        ),
        spacing="1",
        style={
            "padding": spacing["4"],
            "background": colors["bg_secondary"],
            "border": f"1px solid {colors['border_subtle']}",
            "border_radius": borders["radius_md"],
        },
    )


def _scenario_bar(label: str, value: float, color: str) -> rx.Component:
    """Scenario comparison bar"""
    return rx.vstack(
        rx.text(
            label,
            style={
                "font_size": typography["text_xs"],
                "color": colors["text_secondary"],
            },
        ),
        rx.box(
            rx.box(
                style={
                    "width": f"{min(value / 1000000 * 100, 100)}%",
                    "height": "100%",
                    "background": color,
                    "border_radius": borders["radius_sm"],
                },
            ),
            style={
                "width": "100%",
                "height": "8px",
                "background": colors["bg_tertiary"],
                "border_radius": borders["radius_sm"],
            },
        ),
        rx.text(
            f"${value:,.0f}",
            style={
                "font_size": typography["text_sm"],
                "font_weight": typography["weight_medium"],
                "color": colors["text_primary"],
            },
        ),
        spacing="1",
        flex="1",
    )


def _risk_card(label: str, value: float) -> rx.Component:
    """Risk indicator card"""
    risk_color = colors["success"] if value < 0.3 else colors["warning"] if value < 0.6 else colors["error"]
    risk_label = "Low" if value < 0.3 else "Medium" if value < 0.6 else "High"

    return rx.vstack(
        rx.text(
            label,
            style={
                "font_size": typography["text_xs"],
                "color": colors["text_secondary"],
            },
        ),
        rx.circular_progress(
            rx.circular_progress_label(
                risk_label,
                style={
                    "font_size": typography["text_xs"],
                    "color": risk_color,
                },
            ),
            value=int(value * 100),
            size="80px",
            thickness="8px",
        ),
        spacing="2",
        align="center",
        style={
            "padding": spacing["3"],
            "background": colors["bg_secondary"],
            "border": f"1px solid {colors['border_subtle']}",
            "border_radius": borders["radius_md"],
            "flex": "1",
        },
    )


def _dependency_item(dep: Dict[str, Any]) -> rx.Component:
    """Dependency item"""
    return rx.hstack(
        rx.icon(
            "check-circle" if dep.get("resolved") else "circle",
            size=14,
            color=colors["success"] if dep.get("resolved") else colors["text_tertiary"],
        ),
        rx.text(
            dep.get("name", ""),
            style={
                "font_size": typography["text_sm"],
                "color": colors["text_primary"],
            },
        ),
        spacing="2",
        style={
            "padding": spacing["2"],
            "background": colors["bg_tertiary"],
            "border_radius": borders["radius_sm"],
        },
        width="100%",
    )


def _board_metric(label: str, value: str, subtitle: str) -> rx.Component:
    """Board summary metric"""
    return rx.vstack(
        rx.text(
            label,
            style={
                "font_size": typography["text_xs"],
                "color": colors["text_tertiary"],
                "text_transform": "uppercase",
            },
        ),
        rx.text(
            value,
            style={
                "font_size": typography["text_3xl"],
                "font_weight": typography["weight_bold"],
                "color": colors["text_primary"],
            },
        ),
        rx.text(
            subtitle,
            style={
                "font_size": typography["text_xs"],
                "color": colors["text_tertiary"],
            },
        ),
        spacing="1",
        align="center",
        style={
            "padding": spacing["4"],
            "background": colors["bg_secondary"],
            "border": f"1px solid {colors['border_subtle']}",
            "border_radius": borders["radius_lg"],
            "flex": "1",
        },
    )


def _action_item(item: Dict[str, Any]) -> rx.Component:
    """Action item for team view"""
    return rx.hstack(
        rx.checkbox(
            checked=item.get("completed", False),
        ),
        rx.vstack(
            rx.text(
                item.get("task", ""),
                style={
                    "font_size": typography["text_sm"],
                    "color": colors["text_primary"],
                },
            ),
            rx.hstack(
                rx.text(
                    item.get("owner", ""),
                    style={
                        "font_size": typography["text_xs"],
                        "color": colors["text_secondary"],
                    },
                ),
                rx.text(
                    item.get("due", ""),
                    style={
                        "font_size": typography["text_xs"],
                        "color": colors["text_tertiary"],
                    },
                ),
                spacing="2",
            ),
            spacing="0",
            align="start",
        ),
        spacing="3",
        style={
            "padding": spacing["3"],
            "background": colors["bg_secondary"],
            "border": f"1px solid {colors['border_subtle']}",
            "border_radius": borders["radius_md"],
        },
        width="100%",
    )


def _milestone_item(milestone: Dict[str, Any]) -> rx.Component:
    """Milestone item for timeline"""
    return rx.hstack(
        rx.vstack(
            rx.box(
                style={
                    "width": "12px",
                    "height": "12px",
                    "background": colors["accent"] if milestone.get("completed") else colors["text_tertiary"],
                    "border_radius": borders["radius_full"],
                    "border": f"2px solid {colors['bg_secondary']}",
                },
            ),
            rx.box(
                style={
                    "width": "2px",
                    "height": "30px",
                    "background": colors["border_subtle"],
                },
            ),
            spacing="0",
        ),
        rx.vstack(
            rx.text(
                milestone.get("name", ""),
                style={
                    "font_size": typography["text_sm"],
                    "font_weight": typography["weight_medium"],
                    "color": colors["text_primary"],
                },
            ),
            rx.text(
                milestone.get("date", ""),
                style={
                    "font_size": typography["text_xs"],
                    "color": colors["text_tertiary"],
                },
            ),
            spacing="0",
            align="start",
        ),
        spacing="3",
        align="start",
    )
