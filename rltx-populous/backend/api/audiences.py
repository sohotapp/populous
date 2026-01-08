"""
Audience API routes.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import uuid
import random
from datetime import datetime

from backend.models.audience import (
    Audience,
    AudienceProfile,
    AudiencePurpose,
    IncomeLevel,
    GenderRatio,
    CreateAudienceRequest,
)

router = APIRouter(prefix="/audiences", tags=["audiences"])

# In-memory storage
audiences_db: dict[str, Audience] = {}

# Sample names for profile generation
FIRST_NAMES_MALE = ["Ryan", "Mark", "Chris", "Alex", "Jordan", "Sam", "Taylor", "David", "Michael", "James"]
FIRST_NAMES_FEMALE = ["Kendall", "Taylor", "Jordan", "Sam", "Alex", "Emily", "Sarah", "Jessica", "Amanda", "Nicole"]
LAST_INITIALS = ["S", "H", "J", "M", "K", "P", "R", "W", "T", "B"]

EDUCATIONS = [
    "High School Diploma",
    "Some College",
    "Undergraduate Student",
    "Bachelor's Degree",
    "Master's Degree",
    "Professional Degree",
]

OCCUPATIONS = [
    "College Student",
    "Bartender",
    "Marketing Assistant",
    "Retail Associate",
    "Social Media Manager",
    "UX Designer",
    "Server",
    "Sales Rep",
    "Software Engineer",
    "Teacher",
    "Nurse",
    "Accountant",
]

LOCATIONS = [
    "Austin, TX",
    "Miami, FL",
    "Los Angeles, CA",
    "Chicago, IL",
    "New York, NY",
    "San Francisco, CA",
    "Denver, CO",
    "Seattle, WA",
    "Boston, MA",
    "Portland, OR",
]


def _generate_profile(audience: Audience, index: int) -> AudienceProfile:
    """Generate a single synthetic profile based on audience parameters"""

    # Gender based on ratio
    is_male = random.random() < (audience.gender_ratio.male / 100)
    gender = "male" if is_male else "female"

    # Name
    first_names = FIRST_NAMES_MALE if is_male else FIRST_NAMES_FEMALE
    first_name = random.choice(first_names)
    last_initial = random.choice(LAST_INITIALS)
    name = f"{first_name} {last_initial}."

    # Age within range
    age = random.randint(audience.age_range[0], audience.age_range[1])

    # Income based on level
    income_ranges = {
        IncomeLevel.LOW: (20000, 40000),
        IncomeLevel.MIDDLE: (40000, 80000),
        IncomeLevel.UPPER_MIDDLE: (80000, 150000),
        IncomeLevel.HIGH: (150000, 300000),
    }
    income_min, income_max = income_ranges[audience.income_level]
    income = random.randint(income_min, income_max)
    income_str = f"${income:,}"

    return AudienceProfile(
        id=f"{audience.id}_p{index}",
        name=name,
        age=age,
        gender=gender,
        education=random.choice(EDUCATIONS),
        occupation=random.choice(OCCUPATIONS),
        income=income_str,
        location=random.choice(LOCATIONS),
        risk_tolerance=random.random(),
        price_sensitivity=random.random(),
        decision_speed=random.random(),
    )


def _create_mock_audiences():
    """Create mock audiences matching Figma designs"""

    # Urban Gen Z Shoppers
    audience1_id = str(uuid.uuid4())
    audience1 = Audience(
        id=audience1_id,
        name="Urban Gen Z Shoppers (US)",
        description="Young urban consumers aged 18-32 in the United States with moderate income levels, urban sustainability and active environmentalist values.",
        purpose=AudiencePurpose.PRICING_ANALYSIS,
        age_range=(18, 32),
        gender_ratio=GenderRatio(male=30, female=70),
        income_level=IncomeLevel.MIDDLE,
        decision_factors=["Price", "Quality", "Sustainability"],
        profile_count=150,
        profiles=[],
        created_at=datetime.now(),
    )

    # Generate profiles
    audience1.profiles = [_generate_profile(audience1, i) for i in range(8)]

    audiences_db[audience1_id] = audience1

    # Add more mock audiences
    mock_data = [
        {
            "name": "Millennial Pet Owners",
            "description": "Pet owners aged 25-40 with disposable income for premium pet products.",
            "purpose": AudiencePurpose.PRODUCT_LAUNCH,
            "age_range": (25, 40),
            "gender_ratio": GenderRatio(male=45, female=55),
            "income_level": IncomeLevel.UPPER_MIDDLE,
            "profile_count": 200,
        },
        {
            "name": "Tech Enthusiasts",
            "description": "Early adopters interested in new technology products.",
            "purpose": AudiencePurpose.CONCEPT_TESTING,
            "age_range": (22, 45),
            "gender_ratio": GenderRatio(male=65, female=35),
            "income_level": IncomeLevel.HIGH,
            "profile_count": 175,
        },
        {
            "name": "Budget Conscious Millennials",
            "description": "Price-sensitive consumers looking for value.",
            "purpose": AudiencePurpose.PRICING_ANALYSIS,
            "age_range": (28, 40),
            "gender_ratio": GenderRatio(male=50, female=50),
            "income_level": IncomeLevel.LOW,
            "profile_count": 300,
        },
    ]

    for data in mock_data:
        audience_id = str(uuid.uuid4())
        audiences_db[audience_id] = Audience(
            id=audience_id,
            **data,
            decision_factors=[],
            profiles=[],
            created_at=datetime.now(),
        )


# Initialize mock data
_create_mock_audiences()


@router.get("", response_model=List[Audience])
def list_audiences():
    """List all audiences"""
    return list(audiences_db.values())


@router.get("/{audience_id}", response_model=Audience)
def get_audience(audience_id: str):
    """Get a specific audience with profiles"""
    if audience_id not in audiences_db:
        raise HTTPException(404, "Audience not found")
    return audiences_db[audience_id]


@router.post("", response_model=Audience)
def create_audience(request: CreateAudienceRequest):
    """Create a new audience (without generating profiles)"""
    audience_id = str(uuid.uuid4())
    audience = Audience(
        id=audience_id,
        name=request.name,
        description=request.description,
        purpose=request.purpose,
        age_range=(request.age_min, request.age_max),
        gender_ratio=GenderRatio(male=request.gender_ratio_male, female=request.gender_ratio_female),
        income_level=request.income_level,
        decision_factors=request.decision_factors,
        precision=request.precision,
        profile_count=0,
        profiles=[],
        created_at=datetime.now(),
    )
    audiences_db[audience_id] = audience
    return audience


@router.post("/generate", response_model=Audience)
async def generate_audience(request: CreateAudienceRequest, background_tasks: BackgroundTasks):
    """Create audience and generate synthetic profiles"""
    audience_id = str(uuid.uuid4())
    audience = Audience(
        id=audience_id,
        name=request.name,
        description=request.description,
        purpose=request.purpose,
        age_range=(request.age_min, request.age_max),
        gender_ratio=GenderRatio(male=request.gender_ratio_male, female=request.gender_ratio_female),
        income_level=request.income_level,
        decision_factors=request.decision_factors,
        precision=request.precision,
        profile_count=request.profile_count,
        profiles=[],
        created_at=datetime.now(),
    )

    # Generate profiles (in production, this could be a background task)
    audience.profiles = [_generate_profile(audience, i) for i in range(min(request.profile_count, 100))]

    audiences_db[audience_id] = audience
    return audience


@router.delete("/{audience_id}")
def delete_audience(audience_id: str):
    """Delete an audience"""
    if audience_id not in audiences_db:
        raise HTTPException(404, "Audience not found")

    del audiences_db[audience_id]
    return {"message": "Audience deleted"}
