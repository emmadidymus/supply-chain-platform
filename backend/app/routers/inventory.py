from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryResponse
from app.auth.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/inventory", tags=["Inventory"])

def compute_inventory_health(inv: Inventory, demand_forecast: float) -> dict:
    daily_demand = demand_forecast / 30.0
    days_of_stock = (inv.current_stock / daily_demand) if daily_demand > 0 else 999
    if inv.current_stock <= inv.safety_stock:
        risk = "critical"
    elif inv.current_stock <= inv.reorder_point:
        risk = "high"
    elif days_of_stock <= 14:
        risk = "medium"
    else:
        risk = "low"
    return {"days_of_stock": round(days_of_stock, 1), "stockout_risk": risk}

@router.get("/", response_model=List[InventoryResponse])
def list_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    items = db.query(Inventory).offset(skip).limit(limit).all()
    result = []
    for inv in items:
        product = db.query(Product).filter(Product.id == inv.product_id).first()
        demand = product.demand_forecast if product else 100.0
        inv_dict = {c.name: getattr(inv, c.name) for c in inv.__table__.columns}
        inv_dict.update(compute_inventory_health(inv, demand))
        result.append(inv_dict)
    return result

@router.post("/", response_model=InventoryResponse, status_code=201)
def create_inventory(data: InventoryCreate, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    inv = Inventory(**data.model_dump())
    db.add(inv)
    db.commit()
    db.refresh(inv)
    product = db.query(Product).filter(Product.id == inv.product_id).first()
    demand = product.demand_forecast if product else 100.0
    inv_dict = {c.name: getattr(inv, c.name) for c in inv.__table__.columns}
    inv_dict.update(compute_inventory_health(inv, demand))
    return inv_dict

@router.put("/{inventory_id}", response_model=InventoryResponse)
def update_inventory(inventory_id: int, data: InventoryUpdate, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    inv = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(inv, field, value)
    db.commit()
    db.refresh(inv)
    product = db.query(Product).filter(Product.id == inv.product_id).first()
    demand = product.demand_forecast if product else 100.0
    inv_dict = {c.name: getattr(inv, c.name) for c in inv.__table__.columns}
    inv_dict.update(compute_inventory_health(inv, demand))
    return inv_dict
