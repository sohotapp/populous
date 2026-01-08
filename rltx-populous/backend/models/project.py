"""
Project model for the Populous platform.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"


class Project(BaseModel):
    """A research project containing surveys and connected to audiences"""

    id: str
    name: str
    description: str
    status: ProjectStatus = ProjectStatus.DRAFT

    # Connections
    audience_id: Optional[str] = None
    survey_id: Optional[str] = None
    scenario_id: Optional[str] = None
    strategy_id: Optional[str] = None

    # Progress
    responses_collected: int = 0
    responses_target: int = 0

    # Tags
    tags: List[str] = []

    # Timestamps
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class CreateProjectRequest(BaseModel):
    """Request to create a new project"""
    name: str
    description: str = ""
    audience_id: Optional[str] = None
    responses_target: int = 100
    tags: List[str] = []


class UpdateProjectRequest(BaseModel):
    """Request to update a project"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    audience_id: Optional[str] = None
    responses_target: Optional[int] = None
    tags: Optional[List[str]] = None
