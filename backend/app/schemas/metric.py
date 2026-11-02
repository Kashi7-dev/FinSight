from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MetricResultResponse(BaseModel):
    id: UUID
    metric_run_id: UUID
    metric_code: str
    period_end: date
    value: Decimal | None
    unit: str
    result_status: str
    formula_version: str
    explanation: str | None

    model_config = ConfigDict(from_attributes=True)