"""
Linear Design System for Populous
Verbatim implementation of Linear's design language
Dark mode, Inter font, subtle animations
"""

import reflex as rx
from typing import Dict, Any

# =============================================================================
# COLOR TOKENS - Linear's Color Palette
# =============================================================================

colors = {
    # Backgrounds (dark mode)
    "bg_primary": "#0D0D0F",          # Main background
    "bg_secondary": "#131316",         # Card/panel background
    "bg_tertiary": "#1A1A1E",          # Elevated elements
    "bg_hover": "#1F1F24",             # Hover states
    "bg_active": "#2A2A30",            # Active/selected states

    # Borders
    "border_subtle": "#1F1F24",        # Subtle borders
    "border_default": "#2A2A30",       # Default borders
    "border_strong": "#3A3A40",        # Prominent borders

    # Text
    "text_primary": "#FFFFFF",         # Primary text
    "text_secondary": "#8A8A8E",       # Secondary text
    "text_tertiary": "#5A5A60",        # Muted text
    "text_disabled": "#3A3A40",        # Disabled text

    # Accent (Linear purple)
    "accent": "#5E6AD2",               # Primary accent
    "accent_hover": "#6E7AE2",         # Accent hover
    "accent_muted": "#5E6AD220",       # Accent with alpha
    "accent_subtle": "#5E6AD210",      # Very subtle accent

    # Status colors
    "success": "#4ADE80",              # Green
    "success_muted": "#4ADE8020",
    "warning": "#FBBF24",              # Yellow
    "warning_muted": "#FBBF2420",
    "error": "#EF4444",                # Red
    "error_muted": "#EF444420",
    "info": "#38BDF8",                 # Blue
    "info_muted": "#38BDF820",

    # Special
    "gradient_start": "#5E6AD2",
    "gradient_end": "#7C3AED",
}

# =============================================================================
# TYPOGRAPHY - Inter Font
# =============================================================================

typography = {
    "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",

    # Font sizes
    "text_xs": "11px",
    "text_sm": "12px",
    "text_base": "13px",
    "text_md": "14px",
    "text_lg": "16px",
    "text_xl": "18px",
    "text_2xl": "20px",
    "text_3xl": "24px",
    "text_4xl": "32px",

    # Font weights
    "weight_normal": "400",
    "weight_medium": "500",
    "weight_semibold": "600",
    "weight_bold": "700",

    # Line heights
    "leading_tight": "1.2",
    "leading_normal": "1.5",
    "leading_relaxed": "1.6",

    # Letter spacing
    "tracking_tight": "-0.01em",
    "tracking_normal": "0",
    "tracking_wide": "0.02em",
}

# =============================================================================
# SPACING
# =============================================================================

spacing = {
    "0": "0",
    "1": "4px",
    "2": "8px",
    "3": "12px",
    "4": "16px",
    "5": "20px",
    "6": "24px",
    "8": "32px",
    "10": "40px",
    "12": "48px",
    "16": "64px",
}

# =============================================================================
# BORDERS & RADIUS
# =============================================================================

borders = {
    "radius_sm": "4px",
    "radius_md": "6px",
    "radius_lg": "8px",
    "radius_xl": "12px",
    "radius_full": "9999px",
}

# =============================================================================
# SHADOWS - Linear's subtle shadows
# =============================================================================

shadows = {
    "sm": "0 1px 2px rgba(0, 0, 0, 0.3)",
    "md": "0 4px 6px rgba(0, 0, 0, 0.3), 0 1px 3px rgba(0, 0, 0, 0.2)",
    "lg": "0 10px 15px rgba(0, 0, 0, 0.3), 0 4px 6px rgba(0, 0, 0, 0.2)",
    "xl": "0 20px 25px rgba(0, 0, 0, 0.35), 0 8px 10px rgba(0, 0, 0, 0.2)",
    "inner": "inset 0 2px 4px rgba(0, 0, 0, 0.2)",
    "glow": f"0 0 20px {colors['accent_muted']}",
}

# =============================================================================
# ANIMATIONS
# =============================================================================

animations = {
    "duration_fast": "100ms",
    "duration_normal": "200ms",
    "duration_slow": "300ms",
    "easing_default": "cubic-bezier(0.4, 0, 0.2, 1)",
    "easing_in": "cubic-bezier(0.4, 0, 1, 1)",
    "easing_out": "cubic-bezier(0, 0, 0.2, 1)",
}

# =============================================================================
# CSS VARIABLES (for use in stylesheets)
# =============================================================================

css_variables = f"""
:root {{
    /* Colors */
    --bg-primary: {colors['bg_primary']};
    --bg-secondary: {colors['bg_secondary']};
    --bg-tertiary: {colors['bg_tertiary']};
    --bg-hover: {colors['bg_hover']};
    --bg-active: {colors['bg_active']};

    --border-subtle: {colors['border_subtle']};
    --border-default: {colors['border_default']};
    --border-strong: {colors['border_strong']};

    --text-primary: {colors['text_primary']};
    --text-secondary: {colors['text_secondary']};
    --text-tertiary: {colors['text_tertiary']};

    --accent: {colors['accent']};
    --accent-hover: {colors['accent_hover']};
    --accent-muted: {colors['accent_muted']};

    --success: {colors['success']};
    --warning: {colors['warning']};
    --error: {colors['error']};
    --info: {colors['info']};

    /* Typography */
    --font-family: {typography['font_family']};
    --text-xs: {typography['text_xs']};
    --text-sm: {typography['text_sm']};
    --text-base: {typography['text_base']};
    --text-md: {typography['text_md']};
    --text-lg: {typography['text_lg']};

    /* Borders */
    --radius-sm: {borders['radius_sm']};
    --radius-md: {borders['radius_md']};
    --radius-lg: {borders['radius_lg']};

    /* Shadows */
    --shadow-sm: {shadows['sm']};
    --shadow-md: {shadows['md']};
    --shadow-lg: {shadows['lg']};

    /* Animation */
    --duration-fast: {animations['duration_fast']};
    --duration-normal: {animations['duration_normal']};
    --easing: {animations['easing_default']};
}}

/* Base styles */
body {{
    background: {colors['bg_primary']};
    color: {colors['text_primary']};
    font-family: {typography['font_family']};
    font-size: {typography['text_base']};
    line-height: {typography['leading_normal']};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

/* Selection */
::selection {{
    background: {colors['accent_muted']};
}}

/* Scrollbar */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: transparent;
}}

::-webkit-scrollbar-thumb {{
    background: {colors['border_default']};
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: {colors['border_strong']};
}}
"""

# =============================================================================
# COMPONENT STYLES
# =============================================================================

def linear_button(variant: str = "default") -> Dict[str, Any]:
    """Linear-style button styles"""
    base = {
        "font_family": typography["font_family"],
        "font_size": typography["text_sm"],
        "font_weight": typography["weight_medium"],
        "padding": f"{spacing['2']} {spacing['3']}",
        "border_radius": borders["radius_md"],
        "transition": f"all {animations['duration_normal']} {animations['easing_default']}",
        "cursor": "pointer",
        "display": "inline-flex",
        "align_items": "center",
        "gap": spacing["2"],
    }

    variants = {
        "default": {
            **base,
            "background": colors["bg_tertiary"],
            "border": f"1px solid {colors['border_default']}",
            "color": colors["text_primary"],
            "_hover": {
                "background": colors["bg_hover"],
                "border_color": colors["border_strong"],
            },
        },
        "primary": {
            **base,
            "background": colors["accent"],
            "border": f"1px solid {colors['accent']}",
            "color": "#FFFFFF",
            "_hover": {
                "background": colors["accent_hover"],
            },
        },
        "ghost": {
            **base,
            "background": "transparent",
            "border": "1px solid transparent",
            "color": colors["text_secondary"],
            "_hover": {
                "background": colors["bg_hover"],
                "color": colors["text_primary"],
            },
        },
        "danger": {
            **base,
            "background": colors["error_muted"],
            "border": f"1px solid {colors['error']}30",
            "color": colors["error"],
            "_hover": {
                "background": f"{colors['error']}30",
            },
        },
    }

    return variants.get(variant, variants["default"])


def linear_card() -> Dict[str, Any]:
    """Linear-style card styles"""
    return {
        "background": colors["bg_secondary"],
        "border": f"1px solid {colors['border_subtle']}",
        "border_radius": borders["radius_lg"],
        "padding": spacing["4"],
        "box_shadow": shadows["sm"],
    }


def linear_input() -> Dict[str, Any]:
    """Linear-style input styles"""
    return {
        "background": colors["bg_tertiary"],
        "border": f"1px solid {colors['border_default']}",
        "border_radius": borders["radius_md"],
        "padding": f"{spacing['2']} {spacing['3']}",
        "color": colors["text_primary"],
        "font_size": typography["text_sm"],
        "font_family": typography["font_family"],
        "transition": f"all {animations['duration_fast']} {animations['easing_default']}",
        "_focus": {
            "border_color": colors["accent"],
            "box_shadow": f"0 0 0 2px {colors['accent_muted']}",
            "outline": "none",
        },
        "_placeholder": {
            "color": colors["text_tertiary"],
        },
    }


def linear_badge(color: str = "default") -> Dict[str, Any]:
    """Linear-style badge styles"""
    base = {
        "font_size": typography["text_xs"],
        "font_weight": typography["weight_medium"],
        "padding": f"2px {spacing['2']}",
        "border_radius": borders["radius_sm"],
        "display": "inline-flex",
        "align_items": "center",
    }

    variants = {
        "default": {
            **base,
            "background": colors["bg_tertiary"],
            "color": colors["text_secondary"],
        },
        "accent": {
            **base,
            "background": colors["accent_muted"],
            "color": colors["accent"],
        },
        "success": {
            **base,
            "background": colors["success_muted"],
            "color": colors["success"],
        },
        "warning": {
            **base,
            "background": colors["warning_muted"],
            "color": colors["warning"],
        },
        "error": {
            **base,
            "background": colors["error_muted"],
            "color": colors["error"],
        },
    }

    return variants.get(color, variants["default"])


# =============================================================================
# REFLEX THEME CONFIGURATION
# =============================================================================

def get_reflex_theme():
    """Get Reflex theme configuration for Linear design system"""
    return rx.theme(
        appearance="dark",
        accent_color="iris",  # Closest to Linear's purple
        gray_color="slate",
        radius="small",
        scaling="100%",
    )


# =============================================================================
# GLOBAL STYLES
# =============================================================================

global_styles = {
    "body": {
        "background": colors["bg_primary"],
        "color": colors["text_primary"],
        "font_family": typography["font_family"],
    },
    ".radix-themes": {
        "--color-background": colors["bg_primary"],
    },
}
