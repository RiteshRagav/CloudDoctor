# CloudDoctor — AI Cloud Diagnostics

AI-powered cloud infrastructure diagnostics platform that monitors services, detects anomalies, analyzes logs, and provides root cause analysis using GPT-4o.

![CloudDoctor Dashboard](https://img.shields.io/badge/status-production--ready-brightgreen)

## Features

- **Dashboard** — Real-time health monitoring with 4 service pills (BetterStack, MongoDB, LLM, Sample App)
- **Failure Simulation** — Trigger infrastructure failure scenarios (db-crash, memory-leak, high-latency, crash)
- **Log Analyzer** — Real-time log streaming with severity filtering (FATAL/ERROR/WARN/INFO/DEBUG)
- **AI Diagnosis** — GPT-4o powered root cause analysis with confidence scores, MTTR, and recommended fixes
- **Incident Reports** — Full incident lifecycle management (open → diagnosed → resolved)
- **BetterStack Integration** — Dual-write logs to local buffer + BetterStack Logtail for long-term storage

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Tailwind CSS, shadcn/ui, Framer Motion |
| Backend | FastAPI, Python 3.10+ |
| Database | MongoDB |
| AI/LLM | OpenAI GPT-4o (via Emergent key) |
| Logs | BetterStack Logtail |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB running locally
- API keys (see `.env.example` files)

### Backend

```bash
cd backend
cp .env.example .env
# Fill in your API keys in .env

pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

### Frontend

```bash
cd frontend
cp .env.example .env
# Set REACT_APP_BACKEND_URL to your backend URL

npm install
npm run build   # production build
npm start       # development server
```

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|----------|-------------|
| `MONGO_URL` | MongoDB connection string |
| `DB_NAME` | Database name (default: `clouddoctor`) |
| `EMERGENT_LLM_KEY` | Emergent universal key for OpenAI GPT-4o |
| `BETTERSTACK_SOURCE_TOKEN` | BetterStack source token (log ingestion) |
| `BETTERSTACK_QUERY_TOKEN` | BetterStack API token (source health check) |

### Frontend (`frontend/.env`)

| Variable | Description |
|----------|-------------|
| `REACT_APP_BACKEND_URL` | Backend API URL (e.g., `http://localhost:8000`) |

## Deployment

### Frontend (Vercel)

- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `build`
- Framework preset: Create React App

### Backend (Render / Railway)

- Root directory: `backend`
- Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`

## Failure Scenarios

| Scenario | Description |
|----------|-------------|
| `db-crash` | Database connection pool exhaustion |
| `memory-leak` | OOMKilled pod (memory overflow) |
| `high-latency` | SLA breach (latency > 3000ms) |
| `crash` | NullPointerException + pod restart |
| `stop` | Reset all scenarios to healthy |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Service health status |
| GET | `/api/scenarios` | List failure scenarios |
| POST | `/api/incidents/trigger` | Trigger a failure scenario |
| GET | `/api/incidents` | List all incidents |
| POST | `/api/incidents/{id}/diagnose` | Run AI diagnosis |
| POST | `/api/incidents/{id}/resolve` | Resolve an incident |
| GET | `/api/logs` | Query logs (with filters) |
| GET | `/api/logs/stats` | Log severity counts |
| POST | `/api/simulator/stop` | Stop active scenario |

## License

MIT
