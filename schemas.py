"""
Database Schemas for CitySense

Each Pydantic model maps to a MongoDB collection (lowercased class name).
Use these across the backend for validation and persistence.
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class Idea(BaseModel):
    title: str = Field(..., description="Short headline for the idea")
    description: str = Field(..., description="Details of the proposal")
    category: str = Field(..., description="e.g., mobility, energy, waste, air")
    location: Optional[str] = Field(None, description="Location description or coordinates")
    tags: Optional[List[str]] = Field(default_factory=list)
    votes: int = Field(0, ge=0, description="Upvote counter")

class IssueReport(BaseModel):
    title: str = Field(...)
    category: str = Field(..., description="traffic | pollution | infrastructure | other")
    location: Optional[str] = None
    photo_url: Optional[str] = None
    details: Optional[str] = None

class SimulationScenario(BaseModel):
    name: str
    electric_vehicles_pct: float = Field(..., ge=0, le=100)
    green_parks: int = Field(..., ge=0)
    smart_waste_pct: float = Field(..., ge=0, le=100)
    solar_adoption_pct: float = Field(..., ge=0, le=100)
    carbon_reduction_kg: float
    energy_savings_kwh: float
    livability_score: float = Field(..., ge=0, le=100)

class Dataset(BaseModel):
    name: str
    description: str
    category: str
    last_updated: str
    download_csv: str
    download_json: str
    api_endpoint: str
