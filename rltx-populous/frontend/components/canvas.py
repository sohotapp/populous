"""
D3 Canvas System
Force-directed graph canvas for node-based visualization
"""

import reflex as rx
from typing import List, Dict, Any, Optional
from ..design_system import colors, borders, shadows, typography, spacing


# =============================================================================
# CANVAS COMPONENT
# =============================================================================

class CanvasState(rx.State):
    """State for the canvas component"""

    # Canvas settings
    canvas_width: int = 1200
    canvas_height: int = 800
    zoom_level: float = 1.0
    pan_x: float = 0.0
    pan_y: float = 0.0

    # Nodes and edges
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    # Selection
    selected_node_id: Optional[str] = None
    selected_nodes: List[str] = []
    hovered_node_id: Optional[str] = None

    # Interaction mode
    interaction_mode: str = "select"  # select, pan, connect

    # Minimap
    show_minimap: bool = True

    # Grid
    show_grid: bool = True
    snap_to_grid: bool = False
    grid_size: int = 20

    def set_zoom(self, level: float):
        self.zoom_level = max(0.25, min(2.0, level))

    def zoom_in(self):
        self.set_zoom(self.zoom_level + 0.1)

    def zoom_out(self):
        self.set_zoom(self.zoom_level - 0.1)

    def reset_view(self):
        self.zoom_level = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0

    def select_node(self, node_id: str):
        self.selected_node_id = node_id
        if node_id not in self.selected_nodes:
            self.selected_nodes = [node_id]

    def toggle_node_selection(self, node_id: str):
        if node_id in self.selected_nodes:
            self.selected_nodes = [n for n in self.selected_nodes if n != node_id]
            if self.selected_node_id == node_id:
                self.selected_node_id = self.selected_nodes[0] if self.selected_nodes else None
        else:
            self.selected_nodes = self.selected_nodes + [node_id]
            self.selected_node_id = node_id

    def clear_selection(self):
        self.selected_node_id = None
        self.selected_nodes = []

    def set_hover(self, node_id: Optional[str]):
        self.hovered_node_id = node_id

    def toggle_minimap(self):
        self.show_minimap = not self.show_minimap

    def toggle_grid(self):
        self.show_grid = not self.show_grid

    def set_mode(self, mode: str):
        self.interaction_mode = mode


def canvas_toolbar() -> rx.Component:
    """Toolbar for canvas controls"""
    return rx.hstack(
        # Zoom controls
        rx.hstack(
            rx.button(
                rx.icon("minus", size=14),
                on_click=CanvasState.zoom_out,
                style=_tool_button_style(),
            ),
            rx.text(
                rx.cond(
                    CanvasState.zoom_level,
                    f"{int(CanvasState.zoom_level * 100)}%",
                    "100%"
                ),
                style={
                    "font_size": typography["text_xs"],
                    "color": colors["text_secondary"],
                    "min_width": "40px",
                    "text_align": "center",
                },
            ),
            rx.button(
                rx.icon("plus", size=14),
                on_click=CanvasState.zoom_in,
                style=_tool_button_style(),
            ),
            spacing="1",
        ),

        rx.divider(orientation="vertical", height="20px"),

        # View mode
        rx.hstack(
            rx.tooltip(
                rx.button(
                    rx.icon("mouse-pointer", size=14),
                    on_click=lambda: CanvasState.set_mode("select"),
                    style=_tool_button_style(CanvasState.interaction_mode == "select"),
                ),
                content="Select (V)",
            ),
            rx.tooltip(
                rx.button(
                    rx.icon("hand", size=14),
                    on_click=lambda: CanvasState.set_mode("pan"),
                    style=_tool_button_style(CanvasState.interaction_mode == "pan"),
                ),
                content="Pan (H)",
            ),
            spacing="1",
        ),

        rx.divider(orientation="vertical", height="20px"),

        # View options
        rx.hstack(
            rx.tooltip(
                rx.button(
                    rx.icon("grid-3x3", size=14),
                    on_click=CanvasState.toggle_grid,
                    style=_tool_button_style(CanvasState.show_grid),
                ),
                content="Toggle Grid",
            ),
            rx.tooltip(
                rx.button(
                    rx.icon("map", size=14),
                    on_click=CanvasState.toggle_minimap,
                    style=_tool_button_style(CanvasState.show_minimap),
                ),
                content="Toggle Minimap",
            ),
            spacing="1",
        ),

        rx.spacer(),

        # Reset view
        rx.button(
            rx.icon("maximize", size=14),
            "Fit View",
            on_click=CanvasState.reset_view,
            style=_tool_button_style(),
        ),

        padding="2",
        background=colors["bg_secondary"],
        border=f"1px solid {colors['border_subtle']}",
        border_radius=borders["radius_md"],
        width="100%",
    )


def _tool_button_style(active: bool = False) -> Dict[str, Any]:
    """Style for toolbar buttons"""
    return {
        "padding": spacing["2"],
        "background": colors["bg_active"] if active else "transparent",
        "border": "none",
        "border_radius": borders["radius_sm"],
        "color": colors["text_primary"] if active else colors["text_secondary"],
        "cursor": "pointer",
        "_hover": {
            "background": colors["bg_hover"],
        },
    }


def canvas_grid() -> rx.Component:
    """Grid background for canvas"""
    return rx.cond(
        CanvasState.show_grid,
        rx.html(
            f"""
            <svg width="100%" height="100%" style="position: absolute; top: 0; left: 0; pointer-events: none;">
                <defs>
                    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                        <path d="M 20 0 L 0 0 0 20" fill="none" stroke="{colors['border_subtle']}" stroke-width="0.5"/>
                    </pattern>
                    <pattern id="grid-large" width="100" height="100" patternUnits="userSpaceOnUse">
                        <rect width="100" height="100" fill="url(#grid)"/>
                        <path d="M 100 0 L 0 0 0 100" fill="none" stroke="{colors['border_default']}" stroke-width="0.5"/>
                    </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#grid-large)"/>
            </svg>
            """
        ),
        rx.fragment(),
    )


def canvas_minimap() -> rx.Component:
    """Minimap for canvas navigation"""
    return rx.cond(
        CanvasState.show_minimap,
        rx.box(
            rx.box(
                style={
                    "width": "100%",
                    "height": "100%",
                    "background": colors["bg_tertiary"],
                    "border_radius": borders["radius_sm"],
                    "position": "relative",
                }
            ),
            # Viewport indicator
            rx.box(
                style={
                    "position": "absolute",
                    "border": f"1px solid {colors['accent']}",
                    "background": colors["accent_muted"],
                    "border_radius": "2px",
                    # Dynamic position based on pan/zoom would go here
                    "width": "30%",
                    "height": "30%",
                    "top": "35%",
                    "left": "35%",
                }
            ),
            position="absolute",
            bottom="16px",
            right="16px",
            width="150px",
            height="100px",
            background=colors["bg_secondary"],
            border=f"1px solid {colors['border_default']}",
            border_radius=borders["radius_md"],
            padding="2",
            box_shadow=shadows["md"],
            overflow="hidden",
        ),
        rx.fragment(),
    )


def canvas_container(children: rx.Component) -> rx.Component:
    """Main canvas container"""
    return rx.box(
        # Grid background
        canvas_grid(),

        # Main content area
        rx.box(
            children,
            style={
                "transform": f"scale({CanvasState.zoom_level}) translate({CanvasState.pan_x}px, {CanvasState.pan_y}px)",
                "transform_origin": "center center",
                "transition": "transform 0.1s ease-out",
            },
        ),

        # Minimap
        canvas_minimap(),

        position="relative",
        width="100%",
        height="100%",
        min_height="600px",
        background=colors["bg_primary"],
        border=f"1px solid {colors['border_subtle']}",
        border_radius=borders["radius_lg"],
        overflow="hidden",
        cursor=rx.cond(
            CanvasState.interaction_mode == "pan",
            "grab",
            "default"
        ),
    )


def canvas_view() -> rx.Component:
    """Complete canvas view with toolbar"""
    return rx.vstack(
        canvas_toolbar(),
        canvas_container(
            # Nodes will be rendered here
            rx.fragment()
        ),
        spacing="2",
        width="100%",
        height="100%",
    )


# =============================================================================
# D3 FORCE GRAPH COMPONENT (Custom React Component)
# =============================================================================

# This would be a custom component wrapping D3.js
# For now, we'll create a placeholder that can be replaced with actual D3

class ForceGraphState(rx.State):
    """State for force-directed graph"""
    graph_data: Dict[str, Any] = {
        "nodes": [],
        "links": []
    }
    simulation_running: bool = False

    def set_graph_data(self, data: Dict[str, Any]):
        self.graph_data = data

    def start_simulation(self):
        self.simulation_running = True

    def stop_simulation(self):
        self.simulation_running = False


def force_graph_canvas(
    nodes: List[Dict[str, Any]],
    links: List[Dict[str, Any]],
    width: int = 800,
    height: int = 600
) -> rx.Component:
    """
    Force-directed graph visualization.
    Uses D3.js via custom React component.
    """
    # For Reflex, we'd create a custom component wrapping D3
    # This is a simplified placeholder
    return rx.box(
        rx.html(
            f"""
            <div id="force-graph" style="width: {width}px; height: {height}px;">
                <svg width="100%" height="100%">
                    <g class="links"></g>
                    <g class="nodes"></g>
                </svg>
            </div>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <script>
                // D3 force simulation would be initialized here
                // This is a placeholder for the actual implementation
                console.log('Force graph initialized');
            </script>
            """
        ),
        style={
            "background": colors["bg_primary"],
            "border_radius": borders["radius_lg"],
            "border": f"1px solid {colors['border_subtle']}",
        },
    )
