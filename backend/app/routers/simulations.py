from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app.database import get_db
from app.models.simulation import Simulation, Scenario, SimulationStatus
from app.models.supplier import Supplier
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.route import ShipmentRoute
from app.schemas.simulation import SimulationCreate, SimulationResponse, ScenarioResponse
from app.auth.auth import get_current_user
from app.models.user import User
from app.simulation.engine import (
    run_monte_carlo, SupplierData, InventoryData, RouteData
)

router = APIRouter(prefix="/simulations", tags=["Simulations"])

# ── Helper: load DB data into engine dataclasses ──────────────────────────
def _load_simulation_data(db: Session):
    suppliers = [
        SupplierData(
            id=s.id, name=s.name,
            reliability_score=s.reliability_score,
            lead_time_days=s.lead_time_days,
            failure_probability=s.failure_probability,
        )
        for s in db.query(Supplier).all()
    ]
    inventory_items = []
    for inv in db.query(Inventory).all():
        product = db.query(Product).filter(Product.id == inv.product_id).first()
        inventory_items.append(InventoryData(
            product_id=inv.product_id,
            warehouse_id=inv.warehouse_id,
            current_stock=inv.current_stock,
            reorder_point=inv.reorder_point,
            safety_stock=inv.safety_stock,
            demand_forecast=product.demand_forecast if product else 100.0,
            supplier_id=inv.supplier_id,
        ))
    routes = [
        RouteData(
            id=r.id,
            transit_time_days=r.transit_time_days,
            risk_score=r.risk_score,
            cost_per_unit=r.cost_per_unit,
        )
        for r in db.query(ShipmentRoute).all()
    ]
    return suppliers, inventory_items, routes

# ── Background task: actually run the simulation ──────────────────────────
def _execute_simulation(simulation_id: int, db_factory):
    db = db_factory()
    try:
        sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if not sim:
            return
        sim.status = SimulationStatus.running
        db.commit()

        suppliers, inventory_items, routes = _load_simulation_data(db)

        # Run baseline simulation
        if not suppliers and not inventory_items:
            # No data yet — run with demo data so you can still see results
            from app.simulation.engine import SupplierData, InventoryData
            suppliers = [
                SupplierData(1, "Demo Supplier A", 0.85, 14, 0.05),
                SupplierData(2, "Demo Supplier B", 0.70, 21, 0.12),
            ]
            inventory_items = [
                InventoryData(1, 1, 200, 50, 20, 150.0, 1),
                InventoryData(2, 1, 80,  50, 20, 100.0, 2),
            ]

        baseline_results = run_monte_carlo(
            suppliers=suppliers,
            inventory_items=inventory_items,
            routes=routes,
            num_iterations=sim.num_iterations,
        )

        # Run each scenario and save individual results
        scenario_results = {}
        for scenario in sim.scenarios:
            sc_results = run_monte_carlo(
                suppliers=suppliers,
                inventory_items=inventory_items,
                routes=routes,
                num_iterations=min(sim.num_iterations, 5000),  # faster for scenarios
                scenario_params=scenario.parameters,
            )
            scenario.results = sc_results
            scenario_results[scenario.name] = sc_results

        # Compile final results
        sim.results = {
            "baseline": baseline_results,
            "scenarios": scenario_results,
            "summary": {
                "total_suppliers_analyzed": len(suppliers),
                "total_inventory_items":    len(inventory_items),
                "total_routes_analyzed":    len(routes),
                "iterations_run":           sim.num_iterations,
            }
        }
        sim.status = SimulationStatus.completed
        sim.completed_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as e:
        sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if sim:
            sim.status = SimulationStatus.failed
            db.commit()
        raise e
    finally:
        db.close()

# ── API Endpoints ─────────────────────────────────────────────────────────
@router.post("/run", response_model=SimulationResponse, status_code=202)
def run_simulation(
    data: SimulationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start a Monte Carlo simulation. Runs asynchronously in the background.
    Poll GET /simulations/{id} to check status and retrieve results.
    """
    sim = Simulation(
        name=data.name,
        num_iterations=data.num_iterations,
        status=SimulationStatus.pending,
        created_by=current_user.id,
    )
    db.add(sim)
    db.commit()
    db.refresh(sim)

    # Attach scenarios
    for sc_data in data.scenarios:
        scenario = Scenario(
            simulation_id=sim.id,
            name=sc_data.name,
            description=sc_data.description,
            parameters=sc_data.parameters,
        )
        db.add(scenario)
    db.commit()
    db.refresh(sim)

    # Run simulation in background (non-blocking)
    from app.database import SessionLocal
    background_tasks.add_task(_execute_simulation, sim.id, SessionLocal)

    return sim

@router.get("/", response_model=List[SimulationResponse])
def list_simulations(
    skip: int = 0, limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Simulation).order_by(Simulation.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{simulation_id}", response_model=SimulationResponse)
def get_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim

@router.get("/{simulation_id}/scenarios", response_model=List[ScenarioResponse])
def get_simulation_scenarios(
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim.scenarios

@router.delete("/{simulation_id}", status_code=204)
def delete_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    db.delete(sim)
    db.commit()
