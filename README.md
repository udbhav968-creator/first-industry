# Group 2: Tech Stack Issues Finder

Tech Stack Issues Finder audits declared dependencies and versions against public CVE advisories, end-of-life timelines, and upgrade paths.

## Monorepo Layout

- `packages/web`: Frontend application (React + Vite)
- `packages/api`: Backend application (FastAPI)
- `packages/tests`: Integration tests and evaluation suites
- `packages/shared`: Shared types and data contracts
- `packages/db`: Database migrations and schema definitions
- `packages/infra`: Infrastructure and container orchestration
- `docs`: Architecture documentation, OpenAPI contract, and data model

## Services

### SearXNG (Search)
Web search component used during intelligence gathering.
- Port: `8080`
- Command: `docker compose up -d searxng`
- Test: `curl -i http://localhost:8080`

### Crawl4AI (Scraper)
Content extraction service for target advisory and release pages.
- Port: `11235`
- Command: `docker compose up -d crawl4ai`
- Test: `curl -i http://localhost:11235/health`

## Quickstart

### 1. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 2. Start Services via Docker Compose
```bash
docker compose up -d
```

### 3. Service Verification
```bash
# bash
./scripts/smoke_test_searxng.sh
./scripts/smoke_test_crawl4ai.sh

# powershell
.\scripts\smoke_test_searxng.ps1
.\scripts\smoke_test_crawl4ai.ps1
```

### 4. Running Backend Tests
```bash
pytest tests/ -v
```

### 5. Running Frontend Web App
```bash
cd packages/web
npm run dev
```
