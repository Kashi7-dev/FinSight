from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class ForecastRunSummary(BaseModel):
    id: UUID
    target_metric_code: str
    algorithm_name: str
    model_version: str
    frequency: str
    horizon_periods: int
    training_period_end: date
    status: str
    warning: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
class ForecastPointResponse(BaseModel):
    id: UUID
    step_number: int
    forecast_period_end: date
    predicted_value: Decimal
    lower_bound: Decimal | None
    upper_bound: Decimal | None

    model_config = ConfigDict(from_attributes=True)