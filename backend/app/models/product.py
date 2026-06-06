from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    sku = Column(String, unique=True, nullable=False)   # stock keeping unit code
    unit_cost = Column(Float, nullable=False)            # cost per unit in USD
    demand_forecast = Column(Float, default=100.0)       # expected units/month
    category = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # One product can exist in many warehouses
    inventory = relationship("Inventory", back_populates="product")
