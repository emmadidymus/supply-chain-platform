from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProductCreate(BaseModel):
    name: str
    sku: str
    unit_cost: float = Field(gt=0)
    demand_forecast: float = Field(default=100.0, gt=0)
    category: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    unit_cost: Optional[float] = Field(default=None, gt=0)
    demand_forecast: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    unit_cost: float
    demand_forecast: float
    category: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
