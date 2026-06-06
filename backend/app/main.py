from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, suppliers, inventory, products, warehouses, simulations

app = FastAPI(
    title="Supply Chain Risk Simulation Platform",
    description="A decision-support system for analyzing supply chain resilience under uncertainty.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
