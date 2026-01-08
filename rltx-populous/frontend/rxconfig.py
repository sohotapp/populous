"""Reflex configuration for RLTX Populous Frontend"""

import reflex as rx


config = rx.Config(
    app_name="app",
    title="RLTX Populous",
    description="Decision Intelligence Simulation Platform",
    frontend_port=3000,
    backend_port=8001,  # Different from API port 8000
)
