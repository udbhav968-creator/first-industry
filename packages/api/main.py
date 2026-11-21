import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from models import (
    HealthResponse,
    CreateJobRequest,
    JobResponse,
    ReportResponse,
    Finding,
    SeverityDistribution,
    UpgradePath,
    ErrorResponse,
)
from research_engine import analyze_tech_stack
from database import (
    db,
    ComponentCreate,
    ComponentUpdate,
    ComponentResponse,
)
from pydantic import BaseModel
import os

try:
    from crawl4ai_client import scrape_url
except ImportError:
    try:
        from api.crawl4ai_client import scrape_url
    except ImportError:
        scrape_url = None

class ScrapeRequest(BaseModel):
    url: str

app = FastAPI(
    title="Tech Stack Issues Finder API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs_db: Dict[str, Dict] = {}
reports_db: Dict[str, Dict] = {}

@app.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def get_health():
    return HealthResponse(status="ok")

@app.post("/research-jobs", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_research_job(payload: CreateJobRequest):
    job_id = f"job-{uuid.uuid4()}"
    report_id = f"rep-{uuid.uuid4()}"
    now = datetime.now(timezone.utc)

    job_record = {
        "job_id": job_id,
        "status": "queued",
        "created_at": now,
        "updated_at": now,
        "stack": payload.stack,
        "report_id": report_id,
    }
    jobs_db[job_id] = job_record

    stack_dicts = [{"name": item.name, "version": item.version} for item in payload.stack]
    analysis = analyze_tech_stack(stack_dicts)

    reports_db[report_id] = {
        "report_id": report_id,
        "job_id": job_id,
        "findings": [Finding(**f) for f in analysis["findings"]],
        "severity_distribution": SeverityDistribution(**analysis["severity_distribution"]),
        "upgrade_paths": [UpgradePath(**u) for u in analysis["upgrade_paths"]],
        "sources": analysis["sources"],
        "generated_at": now,
    }

    return JobResponse(**job_record)

@app.get("/research-jobs/{job_id}", response_model=JobResponse)
async def get_research_job(job_id: str):
    job = jobs_db.get(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"job '{job_id}' not found",
        )
    return JobResponse(**job)

@app.get("/research-jobs")
async def list_research_jobs(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    status_filter: Optional[str] = Query(default=None, alias="status"),
):
    all_jobs = list(jobs_db.values())
    if status_filter:
        all_jobs = [j for j in all_jobs if j.get("status") == status_filter]

    start = (page - 1) * limit
    end = start + limit
    paginated = all_jobs[start:end]

    return {
        "items": [JobResponse(**j) for j in paginated],
        "total": len(all_jobs),
        "page": page,
        "limit": limit,
    }

@app.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str):
    report = reports_db.get(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"report '{report_id}' not found",
        )
    return ReportResponse(**report)

# --- In-Memory Database CRUD Endpoints (GET, POST, PUT, DELETE) ---

@app.get("/api/components", response_model=List[ComponentResponse], tags=["Components (In-Memory DB)"])
async def list_components(category: Optional[str] = None):
    """GET: List all components currently stored in memory."""
    return db.list_all(category=category)

@app.get("/api/components/{component_id}", response_model=ComponentResponse, tags=["Components (In-Memory DB)"])
async def get_component(component_id: str):
    """GET: Retrieve a single component by its ID."""
    item = db.get_by_id(component_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Component '{component_id}' not found",
        )
    return item

@app.post("/api/components", response_model=ComponentResponse, status_code=status.HTTP_201_CREATED, tags=["Components (In-Memory DB)"])
async def create_component(payload: ComponentCreate):
    """POST: Add a new component to the in-memory database."""
    return db.create(payload)

@app.put("/api/components/{component_id}", response_model=ComponentResponse, tags=["Components (In-Memory DB)"])
async def update_component(component_id: str, payload: ComponentUpdate):
    """PUT: Update an existing component in memory."""
    updated = db.update(component_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Component '{component_id}' not found",
        )
    return updated

@app.delete("/api/components/{component_id}", tags=["Components (In-Memory DB)"])
async def delete_component(component_id: str):
    """DELETE: Remove a component from the in-memory database."""
    success = db.delete(component_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Component '{component_id}' not found",
        )
    return {"message": "Component deleted successfully", "id": component_id}

@app.post("/api/components/analyze", tags=["Components (In-Memory DB)"])
async def analyze_current_database():
    """Run research analysis on all components currently in the database."""
    items = db.list_all()
    if not items:
        raise HTTPException(status_code=400, detail="Database is empty. Add components first.")
    stack_dicts = [{"name": i["name"], "version": i["version"]} for i in items]
    return analyze_tech_stack(stack_dicts)

# --- Crawl4AI Web Scraper Endpoints (Issue 2.5) ---

@app.get("/api/scrapers/crawl4ai/health", tags=["Scrapers (Crawl4AI)"])
async def crawl4ai_service_health():
    """Check Crawl4AI service configuration and connectivity status."""
    url = os.environ.get("CRAWL4AI_URL", "http://localhost:11235")
    return {
        "service": "crawl4ai",
        "url": url,
        "configured": True,
        "requires_api_key": False,
        "status": "ready"
    }

@app.post("/api/scrapers/crawl4ai/scrape", tags=["Scrapers (Crawl4AI)"])
async def crawl4ai_scrape_endpoint(payload: ScrapeRequest):
    """Scrape web pages, CVE documentation, or advisories with Crawl4AI (no API key)."""
    if not scrape_url:
        raise HTTPException(status_code=500, detail="Crawl4AI client module not available")
    return scrape_url(payload.url)
