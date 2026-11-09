from uuid import UUID
from pydantic import Field
from pydantic import BaseModel, ConfigDict

class CompanyProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    ticker_symbol: str | None = Field(default=None, max_length=20)
class CompanySummary(BaseModel):
    id: UUID
    name: str
    ticker_symbol: str | None

    model_config = ConfigDict(from_attributes=True)
    

class PrivateCompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    ticker_symbol: str | None = Field(default=None, max_length=20)

class PrivateCompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    ticker_symbol: str | None = Field(default=None, max_length=20)

    model_config = ConfigDict(extra="forbid")