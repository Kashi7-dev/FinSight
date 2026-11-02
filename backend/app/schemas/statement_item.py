from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StatementItemResponse(BaseModel):
    id: UUID
    statement_type: str
    period_end: date
    item_code: str | None
    normalized_code: str | None
    raw_label: str
    raw_value_text: str | None
    value: Decimal | None
    unit: str
    value_status: str
    source_page: int | None
    extraction_confidence: Decimal | None

    model_config = ConfigDict(from_attributes=True)