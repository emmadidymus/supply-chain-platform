from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, suppliers, inventory, products, warehouses, simulations
import subprocess, os

app = FastAPI(
    title="Supply Chain Risk Simulation Platform",
    description="A decision-support system for analyzing supply chain resilience under uncertainty.",
    version="1.0.0",
)

@app.on_event("startup")
def run_migrations():
    """Auto-run Alembic migrations on startup."""
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("✅ Database migrations applied")
    except Exception as e:
        print(f"⚠️ Migration warning: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will restrict after we get frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(suppliers.router)
app.include_router(inventory.router)
app.include_router(products.router)
app.include_router(warehouses.router)
app.include_router(simulations.router)

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Supply Chain Risk API is running"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
