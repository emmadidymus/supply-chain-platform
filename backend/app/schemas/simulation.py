from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from app.models.simulation import SimulationStatus

class ScenarioCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any]
    # parameters examples:
    # {"type": "supplier_failure", "supplier_id": 3, "duration_days": 30}
    # {"type": "demand_surge", "multiplier": 1.4}
    # {"type": "shipping_delay", "delay_multiplier": 1.5}

class SimulationCreate(BaseModel):
    name: str
    num_iterations: int = Field(default=10000, ge=100, le=100000)
    scenarios: list[ScenarioCreate] = []

class SimulationResponse(BaseModel):
    id: int
    name: str
    num_iterations: int
    status: SimulationStatus
    results: Optional[Dict[str, Any]]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}

class ScenarioResponse(BaseModel):
    id: int
    simulation_id: int
    name: str
    description: Optional[str]
    parameters: Dict[str, Any]
    results: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = {"from_attributes": True}
