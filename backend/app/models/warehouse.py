from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    location = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)          # max units it can hold
    latitude = Column(Float)                            # for map visualization
    longitude = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # One warehouse holds many inventory items
    inventory = relationship("Inventory", back_populates="warehouse")

    # Routes originating or ending at this warehouse
    outbound_routes = relationship("ShipmentRoute", foreign_keys="ShipmentRoute.origin_warehouse_id", back_populates="origin")
    inbound_routes = relationship("ShipmentRoute", foreign_keys="ShipmentRoute.destination_warehouse_id", back_populates="destination")
