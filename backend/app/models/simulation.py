from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class SimulationStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"

class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    num_iterations = Column(Integer, default=10000)
    status = Column(Enum(SimulationStatus), default=SimulationStatus.pending)

    # Results stored as JSON (flexible structure)
    results = Column(JSON, nullable=True)
    # Example results shape:
    # {
    #   "on_time_probability": 0.72,
    #   "shortage_probability": 0.18,
    #   "severe_disruption_probability": 0.10,
    #   "expected_shortage_cost": 45000,
    #   "service_level": 0.85
    # }

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    scenarios = relationship("Scenario", back_populates="simulation")

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False)
    name = Column(String, nullable=False)              # e.g. "Supplier A Failure"
    description = Column(String)

    # Scenario parameters as JSON — flexible for any type of disruption
    parameters = Column(JSON, nullable=False)
    # Example:
    # {"type": "supplier_failure", "supplier_id": 3, "duration_days": 30}
    # {"type": "demand_surge", "multiplier": 1.4}
    # {"type": "shipping_delay", "delay_multiplier": 1.5}

    results = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    simulation = relationship("Simulation", back_populates="scenarios")
