import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SupplierData:
    id: int
    name: str
    reliability_score: float
    lead_time_days: int
    failure_probability: float

@dataclass
class InventoryData:
    product_id: int
    warehouse_id: int
    current_stock: int
    reorder_point: int
    safety_stock: int
    demand_forecast: float   # monthly units
    supplier_id: Optional[int]

@dataclass
class RouteData:
    id: int
    transit_time_days: int
    risk_score: float
    cost_per_unit: float

def run_monte_carlo(
    suppliers: List[SupplierData],
    inventory_items: List[InventoryData],
    routes: List[RouteData],
    num_iterations: int = 10000,
    simulation_days: int = 30,
    scenario_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Core Monte Carlo engine.

    For each iteration we:
      1. Apply scenario modifications (if any)
      2. Randomly determine which suppliers fail
      3. Sample demand from a normal distribution
      4. Sample transit delays based on route risk
      5. Compute whether demand can be fulfilled
      6. Classify outcome: on_time / shortage / severe

    Returns a dictionary of risk metrics.
    """
    rng = np.random.default_rng(seed=None)  # fresh seed each run

    # ── Apply scenario overrides ──────────────────────────────────────────
    scenario_params = scenario_params or {}
    scenario_type = scenario_params.get("type", "baseline")

    # Build mutable copies so we can override per scenario
    sup_failure_probs = np.array([s.failure_probability for s in suppliers])
    sup_lead_times    = np.array([s.lead_time_days for s in suppliers], dtype=float)
    demand_multiplier = 1.0
    route_delay_mult  = 1.0

    if scenario_type == "supplier_failure":
        target_id = scenario_params.get("supplier_id")
        for i, s in enumerate(suppliers):
            if s.id == target_id:
                sup_failure_probs[i] = 1.0   # guaranteed failure
                break

    elif scenario_type == "demand_surge":
        demand_multiplier = float(scenario_params.get("multiplier", 1.4))

    elif scenario_type == "shipping_delay":
        route_delay_mult = float(scenario_params.get("delay_multiplier", 1.5))

    elif scenario_type == "multi_disruption":
        # Combined: supplier pressure + demand surge
        demand_multiplier = float(scenario_params.get("demand_multiplier", 1.2))
        for i in range(len(sup_failure_probs)):
            sup_failure_probs[i] = min(1.0, sup_failure_probs[i] * 1.5)

    # ── Per-item simulation constants ─────────────────────────────────────
    # Daily demand (mean and std) per inventory item
    daily_demands_mean = np.array(
        [item.demand_forecast / 30.0 * demand_multiplier for item in inventory_items]
    )
    # Standard deviation = 30% of mean (realistic demand variability)
    daily_demands_std = daily_demands_mean * 0.30

    current_stocks = np.array([item.current_stock for item in inventory_items], dtype=float)
    safety_stocks  = np.array([item.safety_stock  for item in inventory_items], dtype=float)

    # Map each inventory item to a supplier index (-1 = no supplier)
    sup_id_to_idx = {s.id: i for i, s in enumerate(suppliers)}
    item_supplier_idx = np.array([
        sup_id_to_idx.get(item.supplier_id, -1) for item in inventory_items
    ])

    # Route risk → daily probability of a delay event
    route_delay_probs = np.array([r.risk_score * route_delay_mult for r in routes]) if routes else np.array([0.1])

    # ── Run iterations ────────────────────────────────────────────────────
    on_time_count   = 0
    shortage_count  = 0
    severe_count    = 0
    total_shortage_units = 0.0
    stockout_days_list   = []

    for _ in range(num_iterations):
        # 1. Which suppliers fail this period?
        supplier_failed = rng.random(len(suppliers)) < sup_failure_probs  # boolean array

        # 2. Sample total demand for each item over simulation_days
        daily_d = rng.normal(daily_demands_mean, daily_demands_std, size=(simulation_days, len(inventory_items)))
        daily_d = np.clip(daily_d, 0, None)   # demand can't be negative
        total_demand = daily_d.sum(axis=0)     # shape: (num_items,)

        # 3. Effective stock = current stock, reduced if supplier failed (can't reorder)
        effective_stock = current_stocks.copy()
        for item_idx, sup_idx in enumerate(item_supplier_idx):
            if sup_idx >= 0 and supplier_failed[sup_idx]:
                # Supplier failed → can only use existing stock, no replenishment
                # Reduce effective stock by a random fraction of the safety buffer
                loss_pct = rng.uniform(0.1, 0.5)
                effective_stock[item_idx] = max(
                    safety_stocks[item_idx],
                    effective_stock[item_idx] * (1 - loss_pct)
                )

        # 4. Apply route delays → increase effective lead time → stock arrives late
        if len(routes) > 0:
            any_delay = np.any(rng.random(len(routes)) < route_delay_probs)
            if any_delay:
                # Delayed stock: reduce available stock by ~15-35%
                delay_impact = rng.uniform(0.15, 0.35)
                effective_stock *= (1 - delay_impact)

        # 5. Compute shortage
        shortage = np.maximum(0, total_demand - effective_stock)   # units short per item
        total_shortage = shortage.sum()
        total_demand_sum = total_demand.sum()

        # 6. Classify outcome
        shortage_ratio = total_shortage / max(total_demand_sum, 1)
        stockout_days = (shortage > 0).sum()   # how many items ran out

        if shortage_ratio < 0.05:                # < 5% unmet → on time
            on_time_count += 1
        elif shortage_ratio < 0.25:              # 5–25% unmet → moderate shortage
            shortage_count += 1
        else:                                    # > 25% unmet → severe
            severe_count += 1

        total_shortage_units += total_shortage
        stockout_days_list.append(stockout_days)

    # ── Aggregate results ─────────────────────────────────────────────────
    n = num_iterations
    on_time_prob  = round(on_time_count  / n, 4)
    shortage_prob = round(shortage_count / n, 4)
    severe_prob   = round(severe_count   / n, 4)
    service_level = round(on_time_prob + shortage_prob * 0.5, 4)  # weighted

    avg_shortage_units = total_shortage_units / n

    # Estimate shortage cost (use mean unit cost if available, else $50 default)
    unit_cost_estimate = 50.0
    expected_shortage_cost = round(avg_shortage_units * unit_cost_estimate, 2)

    # Risk exposure score: 0 (safe) to 100 (critical)
    risk_exposure = round((shortage_prob * 40 + severe_prob * 60) * 100, 1)

    stockout_days_arr = np.array(stockout_days_list)

    return {
        "num_iterations": n,
        "simulation_days": simulation_days,
        "scenario_type": scenario_type,
        # Core probabilities
        "on_time_probability":              on_time_prob,
        "shortage_probability":             shortage_prob,
        "severe_disruption_probability":    severe_prob,
        # Service & cost
        "service_level":                    service_level,
        "expected_shortage_cost_usd":       expected_shortage_cost,
        "avg_shortage_units_per_run":       round(avg_shortage_units, 1),
        # Risk score
        "risk_exposure_score":              min(risk_exposure, 100.0),
        # Distribution stats
        "p50_stockout_items":  int(np.percentile(stockout_days_arr, 50)),
        "p90_stockout_items":  int(np.percentile(stockout_days_arr, 90)),
        "p99_stockout_items":  int(np.percentile(stockout_days_arr, 99)),
        # Supplier risk breakdown
        "supplier_risk_summary": [
            {
                "supplier_id":        s.id,
                "name":               s.name,
                "failure_probability": round(float(sup_failure_probs[i]), 3),
                "failed_in_pct_of_runs": round(float(sup_failure_probs[i]) * 100, 1),
            }
            for i, s in enumerate(suppliers)
        ],
    }
