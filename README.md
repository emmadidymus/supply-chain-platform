# Supply Chain Risk Simulation Platform

A full-stack decision-support system that helps organizations evaluate supply chain resilience under uncertain conditions using Monte Carlo simulation.

![Platform](https://img.shields.io/badge/FastAPI-0.111-green) ![React](https://img.shields.io/badge/React-18-blue) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue) ![Python](https://img.shields.io/badge/Python-3.11-yellow)

---

## What It Does

- **Supplier Risk Assessment** — scores each supplier based on reliability, lead time, and failure probability
- **Inventory Health Monitoring** — tracks days of stock remaining and stockout risk levels
- **Monte Carlo Simulation** — runs 10,000+ iterations to model supplier failures, demand surges, and shipping delays
- **Scenario Analysis** — compares outcomes across disruption scenarios (supplier failure, demand spike, port congestion)
- **Risk Dashboard** — visualizes fulfillment probabilities, risk exposure scores, and expected shortage costs

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Python, FastAPI, JWT Auth |
| Database | PostgreSQL, SQLAlchemy, Alembic |
| Simulation Engine | NumPy, Monte Carlo |
| Frontend | React, Vite, Recharts |
| Infrastructure | Docker, Docker Compose |

---

## Running Locally

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop (for PostgreSQL)

### 1. Clone the repository

```bash
git clone https://github.com/emmanueldidymus/supply-chain-platform.git
cd supply-chain-platform
```

### 2. Start the database

```bash
docker compose up db -d
```

### 3. Set up the backend

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
pip install bcrypt==4.0.1       # Pin for passlib compatibility
```

Create a `.env` file in the `backend/` folder:

```env
DATABASE_URL=postgresql://scuser:scpassword@localhost:5432/supplychain
SECRET_KEY=supersecretkey123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Run database migrations:

```bash
alembic upgrade head
```

Start the API server:

```bash
uvicorn app.main:app --reload --port 8000
```

API docs available at: **http://localhost:8000/docs**

### 4. Set up the frontend

Open a new terminal tab:

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: **http://localhost:5173**

### 5. Create an account and seed sample data

First register an admin user at **http://localhost:8000/docs** → `POST /auth/register`:

```json
{
  "email": "admin@supplychain.com",
  "full_name": "Admin User",
  "password": "admin123",
  "role": "admin"
}
```

Then seed the database with realistic sample data:

```bash
cd backend
pip install requests
python seed_data.py
```

This creates:
- 8 global suppliers with risk scores
- 5 warehouses across 4 continents
- 10 products
- 17 inventory records (including critical/high risk items)
- 1 Monte Carlo simulation with 3 scenarios

---

## Project Structure
supply-chain-platform/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── routers/         # FastAPI route handlers
│   │   ├── simulation/      # Monte Carlo engine
│   │   ├── auth/            # JWT authentication
│   │   ├── database.py      # DB connection
│   │   └── main.py          # FastAPI entry point
│   ├── alembic/             # Database migrations
│   ├── seed_data.py         # Sample data script
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/           # Dashboard, Suppliers, Inventory, Simulations
│       ├── components/      # Layout, shared components
│       └── api/             # Axios API client
└── docker-compose.yml

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create user account |
| POST | `/auth/login` | Get JWT token |
| GET/POST | `/suppliers/` | List / create suppliers |
| GET/POST | `/inventory/` | List / create inventory |
| GET/POST | `/products/` | List / create products |
| GET/POST | `/warehouses/` | List / create warehouses |
| POST | `/simulations/run` | Run Monte Carlo simulation |
| GET | `/simulations/{id}` | Get simulation results |

---

## Key Features

### Monte Carlo Simulation Engine

Runs thousands of probabilistic iterations modelling:
- Random supplier shutdowns based on failure probability
- Demand variability (normal distribution, ±30%)
- Shipping delays based on route risk scores
- Multi-disruption combined scenarios

**Sample output from 10,000 iterations:**
On-time fulfillment:      72%
Moderate shortage:        18%
Severe disruption:        10%
Service level:            81%
Risk exposure score:      13.2/100
Expected shortage cost:   $4,250

### Supplier Risk Scoring

Each supplier is scored 0–1 based on:
risk = (failure_probability × 0.5) + (1 - reliability × 0.3) + (lead_time / 90 × 0.2)

---

## Screenshots

> Login → Dashboard → Suppliers → Inventory → Simulations

The platform includes a dark sidebar navigation, risk heatmaps, pie charts for fulfillment probability distribution, horizontal bar charts for supplier risk ranking, and inventory health cards with color-coded risk levels.

---

## Built By Emmanuel Didymus Sebastian
