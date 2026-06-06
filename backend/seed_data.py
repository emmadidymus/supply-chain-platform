"""
Seed script — populates the Supply Chain Risk Platform with realistic sample data.
Run with: python seed_data.py
"""
import requests
import json

BASE = "http://localhost:8000"

# ── 1. Login ──────────────────────────────────────────────────────────────────
print("🔐 Logging in...")
res = requests.post(f"{BASE}/auth/login",
    data={"username": "admin@supplychain.com", "password": "admin123"})
token = res.json()["access_token"]
H = {"Authorization": f"Bearer {token}"}
print("   ✅ Logged in")

# ── 2. Suppliers ──────────────────────────────────────────────────────────────
print("\n🏭 Creating suppliers...")
suppliers_data = [
    {"name": "Shanghai Precision Mfg",  "location": "Shanghai, China",       "reliability_score": 0.92, "lead_time_days": 21, "failure_probability": 0.04, "contact_email": "ops@spm.cn"},
    {"name": "Taiwan Tech Components",  "location": "Taipei, Taiwan",         "reliability_score": 0.88, "lead_time_days": 18, "failure_probability": 0.06, "contact_email": "supply@ttc.tw"},
    {"name": "German Precision Parts",  "location": "Munich, Germany",        "reliability_score": 0.96, "lead_time_days": 14, "failure_probability": 0.02, "contact_email": "orders@gpp.de"},
    {"name": "Vietnam Assembly Co.",    "location": "Ho Chi Minh, Vietnam",   "reliability_score": 0.78, "lead_time_days": 28, "failure_probability": 0.11, "contact_email": "info@vac.vn"},
    {"name": "Mexico FastTrack Mfg",    "location": "Monterrey, Mexico",      "reliability_score": 0.85, "lead_time_days": 10, "failure_probability": 0.07, "contact_email": "sales@mftm.mx"},
    {"name": "India Circuit Systems",   "location": "Bangalore, India",       "reliability_score": 0.81, "lead_time_days": 24, "failure_probability": 0.09, "contact_email": "supply@ics.in"},
    {"name": "US Domestic Parts Co.",   "location": "Detroit, Michigan, USA", "reliability_score": 0.94, "lead_time_days": 5,  "failure_probability": 0.03, "contact_email": "orders@usparts.com"},
    {"name": "Brazil Raw Materials",    "location": "São Paulo, Brazil",      "reliability_score": 0.73, "lead_time_days": 35, "failure_probability": 0.14, "contact_email": "export@brm.br"},
]

supplier_ids = []
for s in suppliers_data:
    res = requests.post(f"{BASE}/suppliers/", json=s, headers=H)
    if res.status_code == 201:
        supplier_ids.append(res.json()["id"])
        print(f"   ✅ {s['name']} (risk: {res.json()['risk_score']})")
    else:
        print(f"   ⚠️  {s['name']}: {res.text}")

# ── 3. Warehouses ─────────────────────────────────────────────────────────────
print("\n🏢 Creating warehouses...")
warehouses_data = [
    {"name": "Los Angeles Hub",       "location": "Los Angeles, CA, USA",    "capacity": 50000, "latitude": 34.0522,  "longitude": -118.2437},
    {"name": "Chicago Distribution",  "location": "Chicago, IL, USA",        "capacity": 35000, "latitude": 41.8781,  "longitude": -87.6298},
    {"name": "Rotterdam Port",        "location": "Rotterdam, Netherlands",  "capacity": 80000, "latitude": 51.9244,  "longitude": 4.4777},
    {"name": "Singapore Gateway",     "location": "Singapore",               "capacity": 60000, "latitude": 1.3521,   "longitude": 103.8198},
    {"name": "Mexico City Depot",     "location": "Mexico City, Mexico",     "capacity": 25000, "latitude": 19.4326,  "longitude": -99.1332},
]

warehouse_ids = []
for w in warehouses_data:
    res = requests.post(f"{BASE}/warehouses/", json=w, headers=H)
    if res.status_code == 201:
        warehouse_ids.append(res.json()["id"])
        print(f"   ✅ {w['name']}")
    else:
        print(f"   ⚠️  {w['name']}: {res.text}")

# ── 4. Products ───────────────────────────────────────────────────────────────
print("\n📦 Creating products...")
products_data = [
    {"name": "Microcontroller Unit MCU-X1",  "sku": "MCU-X1-001",  "unit_cost": 12.50,  "demand_forecast": 2400, "category": "Electronics"},
    {"name": "OLED Display Panel 6-inch",    "sku": "DISP-6IN-02", "unit_cost": 34.00,  "demand_forecast": 1800, "category": "Electronics"},
    {"name": "Lithium Battery Pack 5000mAh", "sku": "BATT-5K-003", "unit_cost": 18.75,  "demand_forecast": 3200, "category": "Power"},
    {"name": "Aluminium Casing Type-B",      "sku": "CASE-ALB-04", "unit_cost": 8.20,   "demand_forecast": 1500, "category": "Hardware"},
    {"name": "USB-C Charging Module",        "sku": "USB-C-MOD-05","unit_cost": 5.40,   "demand_forecast": 4000, "category": "Electronics"},
    {"name": "Thermal Paste Premium",        "sku": "THRM-PRE-06", "unit_cost": 3.80,   "demand_forecast": 800,  "category": "Materials"},
    {"name": "PCB Main Board v3",            "sku": "PCB-MB3-007", "unit_cost": 47.00,  "demand_forecast": 1200, "category": "Electronics"},
    {"name": "Cooling Fan 80mm",             "sku": "FAN-80MM-08", "unit_cost": 6.90,   "demand_forecast": 2000, "category": "Hardware"},
    {"name": "Power Supply Unit 650W",       "sku": "PSU-650W-09", "unit_cost": 62.00,  "demand_forecast": 900,  "category": "Power"},
    {"name": "Copper Wire Bundle 100m",      "sku": "COPP-100-10", "unit_cost": 22.00,  "demand_forecast": 600,  "category": "Materials"},
]

product_ids = []
for p in products_data:
    res = requests.post(f"{BASE}/products/", json=p, headers=H)
    if res.status_code == 201:
        product_ids.append(res.json()["id"])
        print(f"   ✅ {p['name']}")
    else:
        print(f"   ⚠️  {p['name']}: {res.text}")

# ── 5. Inventory ──────────────────────────────────────────────────────────────
print("\n📊 Creating inventory records...")

# Realistic stock scenarios including some critical/high risk items
inventory_data = [
    # LA Hub — primary US distribution
    {"product_id": product_ids[0], "warehouse_id": warehouse_ids[0], "supplier_id": supplier_ids[0], "current_stock": 1200, "reorder_point": 400,  "safety_stock": 200, "max_stock": 5000},
    {"product_id": product_ids[1], "warehouse_id": warehouse_ids[0], "supplier_id": supplier_ids[1], "current_stock": 85,   "reorder_point": 300,  "safety_stock": 150, "max_stock": 3000},  # HIGH RISK
    {"product_id": product_ids[2], "warehouse_id": warehouse_ids[0], "supplier_id": supplier_ids[4], "current_stock": 2800, "reorder_point": 600,  "safety_stock": 300, "max_stock": 8000},
    {"product_id": product_ids[4], "warehouse_id": warehouse_ids[0], "supplier_id": supplier_ids[6], "current_stock": 3500, "reorder_point": 800,  "safety_stock": 400, "max_stock": 10000},
    {"product_id": product_ids[6], "warehouse_id": warehouse_ids[0], "supplier_id": supplier_ids[2], "current_stock": 15,   "reorder_point": 200,  "safety_stock": 100, "max_stock": 2000},  # CRITICAL

    # Chicago — midwest hub
    {"product_id": product_ids[0], "warehouse_id": warehouse_ids[1], "supplier_id": supplier_ids[0], "current_stock": 800,  "reorder_point": 300,  "safety_stock": 150, "max_stock": 3000},
    {"product_id": product_ids[3], "warehouse_id": warehouse_ids[1], "supplier_id": supplier_ids[2], "current_stock": 420,  "reorder_point": 200,  "safety_stock": 100, "max_stock": 2500},
    {"product_id": product_ids[7], "warehouse_id": warehouse_ids[1], "supplier_id": supplier_ids[4], "current_stock": 60,   "reorder_point": 300,  "safety_stock": 150, "max_stock": 4000},  # HIGH RISK
    {"product_id": product_ids[8], "warehouse_id": warehouse_ids[1], "supplier_id": supplier_ids[6], "current_stock": 340,  "reorder_point": 150,  "safety_stock": 75,  "max_stock": 1500},

    # Rotterdam — European hub
    {"product_id": product_ids[1], "warehouse_id": warehouse_ids[2], "supplier_id": supplier_ids[2], "current_stock": 1600, "reorder_point": 400,  "safety_stock": 200, "max_stock": 6000},
    {"product_id": product_ids[5], "warehouse_id": warehouse_ids[2], "supplier_id": supplier_ids[3], "current_stock": 450,  "reorder_point": 150,  "safety_stock": 75,  "max_stock": 2000},
    {"product_id": product_ids[9], "warehouse_id": warehouse_ids[2], "supplier_id": supplier_ids[7], "current_stock": 200,  "reorder_point": 100,  "safety_stock": 50,  "max_stock": 1000},

    # Singapore — APAC hub
    {"product_id": product_ids[0], "warehouse_id": warehouse_ids[3], "supplier_id": supplier_ids[0], "current_stock": 2200, "reorder_point": 500,  "safety_stock": 250, "max_stock": 7000},
    {"product_id": product_ids[2], "warehouse_id": warehouse_ids[3], "supplier_id": supplier_ids[5], "current_stock": 40,   "reorder_point": 500,  "safety_stock": 250, "max_stock": 6000},  # CRITICAL
    {"product_id": product_ids[6], "warehouse_id": warehouse_ids[3], "supplier_id": supplier_ids[1], "current_stock": 580,  "reorder_point": 250,  "safety_stock": 125, "max_stock": 3000},

    # Mexico City — nearshore
    {"product_id": product_ids[3], "warehouse_id": warehouse_ids[4], "supplier_id": supplier_ids[4], "current_stock": 310,  "reorder_point": 200,  "safety_stock": 100, "max_stock": 2000},
    {"product_id": product_ids[4], "warehouse_id": warehouse_ids[4], "supplier_id": supplier_ids[4], "current_stock": 750,  "reorder_point": 300,  "safety_stock": 150, "max_stock": 3500},
]

for inv in inventory_data:
    res = requests.post(f"{BASE}/inventory/", json=inv, headers=H)
    if res.status_code == 201:
        data = res.json()
        risk = data.get("stockout_risk", "?")
        days = data.get("days_of_stock", "?")
        emoji = "🔴" if risk == "critical" else "🟠" if risk == "high" else "🟡" if risk == "medium" else "🟢"
        print(f"   {emoji} Product {inv['product_id']} @ Warehouse {inv['warehouse_id']} — {risk} ({days} days)")
    else:
        print(f"   ⚠️  {res.text}")

# ── 6. Run a simulation ───────────────────────────────────────────────────────
print("\n🎲 Running baseline Monte Carlo simulation...")
sim_payload = {
    "name": "Baseline Risk Analysis — Seeded Data",
    "num_iterations": 10000,
    "scenarios": [
        {"name": "Supplier Failure: Shanghai",   "description": "Shanghai Precision Mfg goes offline 30 days",
         "parameters": {"type": "supplier_failure", "supplier_id": supplier_ids[0], "duration_days": 30}},
        {"name": "40% Holiday Demand Surge",     "description": "Peak season demand spike",
         "parameters": {"type": "demand_surge", "multiplier": 1.4}},
        {"name": "Port Congestion +50% Delays",  "description": "Global shipping disruption",
         "parameters": {"type": "shipping_delay", "delay_multiplier": 1.5}},
    ]
}

res = requests.post(f"{BASE}/simulations/run", json=sim_payload, headers=H)
if res.status_code == 202:
    sim_id = res.json()["id"]
    print(f"   ✅ Simulation #{sim_id} started (running in background...)")
    print(f"   ⏳ Visit http://localhost:5173/simulations to watch results appear")
else:
    print(f"   ⚠️  {res.text}")

print("\n" + "="*60)
print("🎉  SEED DATA COMPLETE!")
print("="*60)
print(f"""
Summary:
  • {len(supplier_ids)} suppliers created
  • {len(warehouse_ids)} warehouses created
  • {len(product_ids)} products created
  • {len(inventory_data)} inventory records created
  • 1 simulation launched (10,000 iterations)

Open your browser:
  → Dashboard:    http://localhost:5173/
  → Suppliers:    http://localhost:5173/suppliers
  → Inventory:    http://localhost:5173/inventory
  → Simulations:  http://localhost:5173/simulations
""")
