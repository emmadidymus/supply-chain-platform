from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# What's required to CREATE a supplier
class SupplierCreate(BaseModel):
    name: str
    location: str
    reliability_score: float = Field(default=0.8, ge=0.0, le=1.0)
    lead_time_days: int = Field(default=14, gt=0)
    failure_probability: float = Field(default=0.05, ge=0.0, le=1.0)
    contact_email: Optional[str] = None

# What's allowed to UPDATE (all fields optional)
class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    reliability_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    lead_time_days: Optional[int] = Field(default=None, gt=0)
    failure_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    contact_email: Optional[str] = None

# What the API RETURNS (includes id, created_at, and a computed risk_score)
class SupplierResponse(BaseModel):
    id: int
    name: str
    location: str
    reliability_score: float
    lead_time_days: int
    failure_probability: float
    contact_email: Optional[str]
    created_at: datetime
    risk_score: Optional[float] = None  # computed field added by router

    model_config = {"from_attributes": True}
