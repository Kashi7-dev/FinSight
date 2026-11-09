from datetime import date, datetime
from uuid import UUID
from typing import Literal
from pydantic import BaseModel, ConfigDict


class FinancialReportSummary(BaseModel):
    id: UUID
    report_type: str
    statement_scope: str
    fiscal_year: int
    fiscal_quarter: int | None
    period_start: date | None
    period_end: date | None
    currency: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
class FinancialReportDetail(BaseModel):
    id: UUID
    company_profile_id: UUID
    report_type: str
    statement_scope: str
    fiscal_year: int
    fiscal_quarter: int | None
    period_start: date | None
    period_end: date | None
    currency: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
class ReportUploadAccepted(BaseModel):
    report_id: UUID
    extraction_job_id: UUID
    job_status: Literal["QUEUED"]
    message: str
    
class ReportProcessingStatus(BaseModel):
    report_id: UUID
    original_filename: str | None
    report_status: str

    extraction_job_id: UUID
    job_status: str
    error_message: str | None
    job_created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None