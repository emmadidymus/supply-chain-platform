from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from app.auth.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

def compute_risk_score(supplier: Supplier) -> float:
    reliability_risk = 1.0 - supplier.reliability_score
    lead_time_risk = min(supplier.lead_time_days / 90.0, 1.0)
    return round((supplier.failure_probability * 0.5 + reliability_risk * 0.3 + lead_time_risk * 0.2), 3)

@router.get("/", response_model=List[SupplierResponse])
def list_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    suppliers = db.query(Supplier).offset(skip).limit(limit).all()
    result = []
    for s in suppliers:
        s_dict = {c.name: getattr(s, c.name) for c in s.__table__.columns}
        s_dict["risk_score"] = compute_risk_score(s)
        result.append(s_dict)
    return result

@router.post("/", response_model=SupplierResponse, status_code=201)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    s_dict = {c.name: getattr(supplier, c.name) for c in supplier.__table__.columns}
    s_dict["risk_score"] = compute_risk_score(supplier)
    return s_dict

@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    s_dict = {c.name: getattr(supplier, c.name) for c in supplier.__table__.columns}
    s_dict["risk_score"] = compute_risk_score(supplier)
    return s_dict

@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(supplier_id: int, data: SupplierUpdate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(supplier, field, value)
    db.commit()
    db.refresh(supplier)
    s_dict = {c.name: getattr(supplier, c.name) for c in supplier.__table__.columns}
    s_dict["risk_score"] = compute_risk_score(supplier)
    return s_dict

@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    db.delete(supplier)
    db.commit()
