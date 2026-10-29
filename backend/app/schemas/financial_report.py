from datetime import date, datetime
from uuid import UUID

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