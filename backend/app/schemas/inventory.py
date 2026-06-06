from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InventoryCreate(BaseModel):
    product_id: int
    warehouse_id: int
    supplier_id: Optional[int] = None
    current_stock: int = Field(default=0, ge=0)
    reorder_point: int = Field(default=50, ge=0)
    safety_stock: int = Field(default=20, ge=0)
    max_stock: int = Field(default=500, gt=0)

class InventoryUpdate(BaseModel):
    current_stock: Optional[int] = Field(default=None, ge=0)
    reorder_point: Optional[int] = Field(default=None, ge=0)
    safety_stock: Optional[int] = Field(default=None, ge=0)
    max_stock: Optional[int] = Field(default=None, gt=0)
    supplier_id: Optional[int] = None

class InventoryResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    supplier_id: Optional[int]
    current_stock: int
    reorder_point: int
    safety_stock: int
    max_stock: int
    updated_at: datetime
    # Computed health fields added by the router
    days_of_stock: Optional[float] = None
    stockout_risk: Optional[str] = None   # "low", "medium", "high", "critical"

    model_config = {"from_attributes": True}
