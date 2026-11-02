from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class CompanyMetricComparison(BaseModel):
    company_id: UUID
    company_name: str
    ticker_symbol: str | None
    metric_code: str
    period_end: date
    value: Decimal | None
    unit: str | None
    result_status: str