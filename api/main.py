import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import JSONResponse
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

app = FastAPI(
    title="Group 2 Tech Stack Issues Finder API",
    version="1.0.0",
    description="Analyzes tech stacks for CVE advisories, EOL status, and upgrade paths.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demonstration and fast local test execution
jobs_db: Dict[str, Dict] = {}
reports_db: Dict[str, Dict] = {}

@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
    tags=["Monitoring"],
)
async def get_health():
    """Returns 200 and status ok. Does not verify external dependencies."""
    return HealthResponse(status="ok")

@app.post(
    "/research-jobs",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit tech stack for analysis",
    tags=["Research Jobs"],
)
async def create_research_job(payload: CreateJobRequest):
    """Submits a tech stack and active versions. Queues job for CVE & advisory research."""
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

    # Seed mock report generation for immediate downstream pipeline consumption
    findings: List[Finding] = []
    upgrade_paths: List[UpgradePath] = []
    sources: List[str] = []

    for item in payload.stack:
        sources.append(f"https://nvd.nist.gov/vuln/search/results?query={item.name}")
        sources.append(f"https://endoflife.date/{item.name}")

        # Basic baseline advisory structure per component
        findings.append(
            Finding(
                id=f"ADV-{item.name.upper()}-001",
                severity="medium",
                component=item.name,
                affected_versions=f"<= {item.version}",
                fixed_in=f"{item.version}.1",
                end_of_life_date="2027-01-01",
                description=f"Public advisory check for {item.name} version {item.version}.",
            )
        )
        upgrade_paths.append(
            UpgradePath(
                component=item.name,
                current_version=item.version,
                target_version=f"{item.version}.1",
                breaking_changes_note="Patch release containing recommended security fixes.",
            )
        )

    reports_db[report_id] = {
        "report_id": report_id,
        "job_id": job_id,
        "findings": findings,
        "severity_distribution": SeverityDistribution(medium=len(findings)),
        "upgrade_paths": upgrade_paths,
        "sources": sources,
        "generated_at": now,
    }

    return JobResponse(**job_record)

@app.get(
    "/research-jobs/{job_id}",
    response_model=JobResponse,
    summary="Get job status",
    tags=["Research Jobs"],
)
async def get_research_job(job_id: str):
    job = jobs_db.get(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found.",
        )
    return JobResponse(**job)

@app.get(
    "/research-jobs",
    summary="List research jobs",
    tags=["Research Jobs"],
)
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

@app.get(
    "/reports/{report_id}",
    response_model=ReportResponse,
    summary="Fetch vulnerability report",
    tags=["Reports"],
)
async def get_report(report_id: str):
    report = reports_db.get(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{report_id}' not found.",
        )
    return ReportResponse(**report)
