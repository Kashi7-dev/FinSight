from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.company_profile import CompanyProfile
from app.schemas.company import CompanySummary
from app.models.financial_report import FinancialReport
from app.schemas.financial_report import FinancialReportSummary

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.get("/", response_model=list[CompanySummary])
def list_shared_companies(
    db: Session = Depends(get_db),
) -> list[CompanySummary]:
    statement = (
        select(CompanyProfile)
        .where(CompanyProfile.scope == "SHARED")
        .order_by(CompanyProfile.name)
    )
    companies = db.scalars(statement).all()
    return list(companies)

@router.get(
    "/{company_id}",
    response_model=CompanySummary,
)
def get_shared_company(
    company_id: UUID,
    db: Session = Depends(get_db),
) -> CompanySummary:
    statement = select(CompanyProfile).where(
        CompanyProfile.id == company_id,
        CompanyProfile.scope == "SHARED",
    )
    company = db.scalar(statement)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared company not found",
        )

    return company

@router.get(
    "/{company_id}/reports",
    response_model=list[FinancialReportSummary],
)
def list_company_reports(
    company_id: UUID,
    db: Session = Depends(get_db),
) -> list[FinancialReportSummary]:
    statement = (
        select(FinancialReport)
        .join(
            CompanyProfile,
            CompanyProfile.id == FinancialReport.company_profile_id,
        )
        .where(
            CompanyProfile.id == company_id,
            CompanyProfile.scope == "SHARED",
            FinancialReport.origin == "EXTERNAL",
        )
        .order_by(
            FinancialReport.fiscal_year.desc(),
            FinancialReport.fiscal_quarter.desc(),
        )
    )

    reports = db.scalars(statement).all()
    return list(reports)