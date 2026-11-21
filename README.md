# Group 2: Tech Stack Issues Finder

A developer enters a tech stack and versions, and gets public security advisories, CVEs, end-of-life (EOL) dates, and safe upgrade paths.

---

## Architecture & Monorepo Structure

```
├── .github/
│   ├── workflows/ci.yml       # GitHub Actions CI pipeline (Milestone 7.1)
│   └── pull_request_template.md # Standard PR checklist & format (Milestone 3.7)
├── api/
│   ├── main.py                # FastAPI application & endpoints (Milestones 6.1, 6.3)
│   ├── models.py              # Pydantic schemas conforming to OpenAPI contract
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Container definition (Milestone 2.3)
├── docs/
│   ├── data-model.md          # ER diagram & entity specifications (Milestone 4.1)
│   ├── openapi.yaml           # OpenAPI 3.1 REST API contract (Milestone 4.7)
│   └── issues/                # Workshop roadmap & milestone documentation
├── tests/
│   ├── test_health.py         # Liveness check tests (Milestone 6.1)
│   └── test_research_jobs.py  # Validation and contract integration tests
├── .env.example               # Safe environment variable template (Milestone 2.2)
├── docker-compose.yml         # Compose stack: api, postgres, searxng, crawl4ai (Milestones 2.4, 2.5)
└── README.md
```

---

## Quickstart & Local Setup

### 1. Prerequisites
- Python 3.10+
- Docker & Docker Compose (optional for containerized run)

### 2. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Local Execution (Direct Python)
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r api/requirements.txt

# Start API server
uvicorn api.main:app --reload --port 8000
```
- Interactive Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json
- Health check: http://localhost:8000/health

### 4. Running Tests
```bash
pytest tests/ -v
```

### 5. Running with Docker Compose
```bash
docker compose up --build -d
```
All services (`api`, `postgres`, `searxng`, `crawl4ai`) will spin up with health checks enabled.
