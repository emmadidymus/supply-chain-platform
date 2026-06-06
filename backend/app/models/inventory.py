from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys — link this row to specific product, warehouse, supplier
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)

    current_stock = Column(Integer, default=0)          # units on hand right now
    reorder_point = Column(Integer, default=50)         # trigger reorder when stock hits this
    safety_stock = Column(Integer, default=20)          # minimum buffer to keep
    max_stock = Column(Integer, default=500)            # storage limit for this item

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships (lets us do inventory.product.name, etc.)
    product = relationship("Product", back_populates="inventory")
    warehouse = relationship("Warehouse", back_populates="inventory")
    supplier = relationship("Supplier", back_populates="inventory")
