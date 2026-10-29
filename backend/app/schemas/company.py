from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CompanySummary(BaseModel):
    id: UUID
    name: str
    ticker_symbol: str | None

    model_config = ConfigDict(from_attributes=True)