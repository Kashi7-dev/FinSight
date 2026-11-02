from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.financial_report import FinancialReportDetail
from app.db.dependencies import get_db
from app.models.company_profile import CompanyProfile
from app.models.financial_report import FinancialReport
from app.models.statement_item import StatementItem
from app.schemas.statement_item import StatementItemResponse


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get(
    "/{report_id}/statement-items",
    response_model=list[StatementItemResponse],
)
def list_report_statement_items(
    report_id: UUID,
    db: Session = Depends(get_db),
) -> list[StatementItemResponse]:
    statement = (
        select(StatementItem)
        .join(
            FinancialReport,
            FinancialReport.id == StatementItem.report_id,
        )
        .join(
            CompanyProfile,
            CompanyProfile.id == FinancialReport.company_profile_id,
        )
        .where(
            StatementItem.report_id == report_id,
            FinancialReport.origin == "EXTERNAL",
            CompanyProfile.scope == "SHARED",
        )
        .order_by(
            StatementItem.statement_type,
            StatementItem.period_end,
            StatementItem.normalized_code,
        )
    )

    items = db.scalars(statement).all()
    return list(items)

@router.get(
    "/{report_id}",
    response_model=FinancialReportDetail,
)
def get_shared_report(
    report_id: UUID,
    db: Session = Depends(get_db),
) -> FinancialReport:
    statement = (
        select(FinancialReport)
        .join(
            CompanyProfile,
            CompanyProfile.id == FinancialReport.company_profile_id,
        )
        .where(
            FinancialReport.id == report_id,
            FinancialReport.origin == "EXTERNAL",
            CompanyProfile.scope == "SHARED",
        )
    )

    report = db.scalar(statement)

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared financial report not found",
        )

    return report