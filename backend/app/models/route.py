from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class ShipmentRoute(Base):
    __tablename__ = "shipment_routes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)                               # e.g. "Shanghai → LA"

    origin_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    destination_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)

    transit_time_days = Column(Integer, nullable=False) # normal transit days
    risk_score = Column(Float, default=0.1)             # 0.0 (safe) to 1.0 (very risky)
    cost_per_unit = Column(Float, default=5.0)          # shipping cost per unit
    carrier = Column(String)                            # e.g. "Maersk", "FedEx"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    origin = relationship("Warehouse", foreign_keys=[origin_warehouse_id], back_populates="outbound_routes")
    destination = relationship("Warehouse", foreign_keys=[destination_warehouse_id], back_populates="inbound_routes")
