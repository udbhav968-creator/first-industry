from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="Liveness status of the API")

class StackItem(BaseModel):
    name: str = Field(..., description="Library or framework name", min_length=1)
    version: str = Field(..., description="Semantic version string", min_length=1)

class CreateJobRequest(BaseModel):
    stack: List[StackItem] = Field(..., min_length=1, description="List of components and active versions")

class JobResponse(BaseModel):
    job_id: str
    status: str = Field(..., description="Job lifecycle state: queued, running, completed, failed")
    created_at: datetime
    updated_at: Optional[datetime] = None
    stack: Optional[List[StackItem]] = None
    report_id: Optional[str] = None

class Finding(BaseModel):
    id: str = Field(..., description="CVE or Advisory identifier")
    severity: str = Field(..., description="critical, high, medium, low, info")
    component: str
    affected_versions: str
    fixed_in: Optional[str] = None
    end_of_life_date: Optional[str] = None
    description: str
    impact_score: Optional[int] = Field(default=None, description="Impact score (1-5)")
    effort_score: Optional[int] = Field(default=None, description="Upgrade effort score (1-5)")

class SeverityDistribution(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0

class UpgradePath(BaseModel):
    component: str
    current_version: str
    target_version: str
    breaking_changes_note: Optional[str] = None

class ReportResponse(BaseModel):
    report_id: str
    job_id: str
    findings: List[Finding]
    severity_distribution: SeverityDistribution
    upgrade_paths: List[UpgradePath]
    sources: List[str]
    generated_at: datetime

class ErrorResponse(BaseModel):
    code: str
    message: str
