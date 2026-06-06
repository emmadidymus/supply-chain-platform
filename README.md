# Supply Chain Risk Simulation Platform

A full-stack decision-support system that models supply chain resilience under uncertainty using Monte Carlo simulation.

![Dashboard](https://img.shields.io/badge/status-live-brightgreen) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688) ![React](https://img.shields.io/badge/React-18-61DAFB) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791)

## Live Demo
- **Frontend:** (add after deploy)
- **API Docs:** (add after deploy)

## Features

- **Monte Carlo Engine** — runs 10,000+ probabilistic iterations modeling supplier failures, demand surges, and shipping delays
- **Risk Dashboard** — real-time KPIs: service level probability, risk exposure score, expected shortage cost
- **Supplier Management** — computed risk scores combining failure probability, reliability, and lead time
- **Inventory Health** — stockout risk classification (critical / high / medium / low) with days-of-stock tracking
- **Scenario Analysis** — compare baseline vs. disruption scenarios side by side
- **JWT Authentication** — role-based access (admin, manager, analyst)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, SQLAlchemy, Alembic |
| Simulation | NumPy, SciPy |
| Database | PostgreSQL |
| Frontend | React, Vite, Recharts, React Router |
| Auth | JWT (python-jose, bcrypt) |
| Dev | Docker Compose |

## Architecture
supply-chain-platform/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── database.py          # DB connection
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API endpoints
│   │   ├── simulation/          # Monte Carlo engine
│   │   └── auth/                # JWT logic
│   └── alembic/                 # DB migrations
└── frontend/
└── src/
├── pages/               # Dashboard, Suppliers, Inventory, Simulations
├── components/          # Layout, shared UI
└── api/                 # Axios client + endpoints

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker Desktop

### Setup

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/supply-chain-platform.git
cd supply-chain-platform

# Start database
docker compose up db -d

# Backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### Seed sample data

```bash
cd backend
source venv/bin/activate
pip install requests
python seed_data.py
```

## API Documentation

Interactive docs available at `http://localhost:8000/docs` when running locally.

Key endpoints:
- `POST /auth/register` — create account
- `POST /auth/login` — get JWT token
- `GET /suppliers/` — list suppliers with computed risk scores
- `GET /inventory/` — inventory with stockout risk classification
- `POST /simulations/run` — launch Monte Carlo simulation (async)
- `GET /simulations/{id}` — poll simulation status and results

## Simulation Engine

The Monte Carlo engine (`backend/app/simulation/engine.py`) runs N iterations where each iteration:

1. Randomly determines supplier failures based on `failure_probability`
2. Samples demand from a normal distribution (±30% variance)
3. Applies route delays based on `risk_score`
4. Computes whether demand can be fulfilled
5. Classifies outcome: on-time / shortage / severe disruption

Output metrics include `on_time_probability`, `service_level`, `risk_exposure_score`, and `expected_shortage_cost_usd`.

## Author

Emmanuel Didymus — [GitHub](https://github.com/emmadidymus) | [LinkedIn](https://linkedin.com/in/YOUR_PROFILE)
