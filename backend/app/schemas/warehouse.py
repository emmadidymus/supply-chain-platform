from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WarehouseCreate(BaseModel):
    name: str
    location: str
    capacity: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class WarehouseResponse(BaseModel):
    id: int
    name: str
    location: str
    capacity: int
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}
