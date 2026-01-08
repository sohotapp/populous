"""
Project API routes.
"""

from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from datetime import datetime

from backend.models.project import (
    Project,
    ProjectStatus,
    CreateProjectRequest,
    UpdateProjectRequest,
)

router = APIRouter(prefix="/projects", tags=["projects"])

# In-memory storage (replace with database for production)
projects_db: dict[str, Project] = {}


def _create_mock_projects():
    """Create mock projects matching Figma designs"""
    mock_data = [
        {
            "name": "SparkZero Pricing Study",
            "description": "Consumer Test • Value Sat • Shipping",
            "status": ProjectStatus.RUNNING,
            "responses_collected": 3000,
            "responses_target": 5000,
            "tags": ["Consumer", "Pricing"],
        },
        {
            "name": "SparkZero Pricing Study",
            "description": "Consumer Test • Value Sat • Shipping",
            "status": ProjectStatus.COMPLETED,
            "responses_collected": 5000,
            "responses_target": 5000,
            "tags": ["Consumer", "Research"],
        },
        {
            "name": "EcoSpark Launch Test",
            "description": "Product Launch • Market Fit • Segments",
            "status": ProjectStatus.RUNNING,
            "responses_collected": 2400,
            "responses_target": 3000,
            "tags": ["Launch", "B2B"],
        },
        {
            "name": "EcoSpark Launch Test",
            "description": "Product Launch • Market Fit • Segments",
            "status": ProjectStatus.COMPLETED,
            "responses_collected": 3000,
            "responses_target": 3000,
            "tags": ["Launch"],
        },
    ]

    for data in mock_data:
        project_id = str(uuid.uuid4())
        projects_db[project_id] = Project(
            id=project_id,
            **data,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )


# Initialize mock data
_create_mock_projects()


@router.get("", response_model=List[Project])
def list_projects(status: str = None):
    """List all projects, optionally filtered by status"""
    projects = list(projects_db.values())

    if status:
        projects = [p for p in projects if p.status == status]

    return sorted(projects, key=lambda p: p.updated_at, reverse=True)


@router.get("/{project_id}", response_model=Project)
def get_project(project_id: str):
    """Get a specific project by ID"""
    if project_id not in projects_db:
        raise HTTPException(404, "Project not found")
    return projects_db[project_id]


@router.post("", response_model=Project)
def create_project(request: CreateProjectRequest):
    """Create a new project"""
    project_id = str(uuid.uuid4())
    project = Project(
        id=project_id,
        name=request.name,
        description=request.description,
        audience_id=request.audience_id,
        responses_target=request.responses_target,
        tags=request.tags,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    projects_db[project_id] = project
    return project


@router.put("/{project_id}", response_model=Project)
def update_project(project_id: str, request: UpdateProjectRequest):
    """Update an existing project"""
    if project_id not in projects_db:
        raise HTTPException(404, "Project not found")

    project = projects_db[project_id]

    if request.name is not None:
        project.name = request.name
    if request.description is not None:
        project.description = request.description
    if request.status is not None:
        project.status = request.status
    if request.audience_id is not None:
        project.audience_id = request.audience_id
    if request.responses_target is not None:
        project.responses_target = request.responses_target
    if request.tags is not None:
        project.tags = request.tags

    project.updated_at = datetime.now()
    projects_db[project_id] = project

    return project


@router.delete("/{project_id}")
def delete_project(project_id: str):
    """Delete a project"""
    if project_id not in projects_db:
        raise HTTPException(404, "Project not found")

    del projects_db[project_id]
    return {"message": "Project deleted"}
