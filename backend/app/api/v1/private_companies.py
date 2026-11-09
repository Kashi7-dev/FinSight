from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.api.dependencies import get_current_user
from app.db.dependencies import get_db
from app.models.company_profile import CompanyProfile
from app.models.user import User
from app.schemas.company import CompanyProfileCreate, CompanySummary
from app.schemas.company import (
    CompanyProfileCreate,
    CompanySummary,
    PrivateCompanyUpdate,
)

router = APIRouter(
    prefix="/my/companies",
    tags=["My Companies"],
)
from app.models.financial_report import FinancialReport
from app.schemas.financial_report import FinancialReportSummary
from datetime import date
from typing import Literal

from fastapi import File, Form, UploadFile
from app.models.extraction_job import ExtractionJob
from app.services.file_storage import (
    delete_private_pdf,
    save_private_pdf,
)
from app.schemas.financial_report import ReportUploadAccepted
from fastapi import BackgroundTasks
from app.services.report_processor import process_pdf_report
from app.schemas.financial_report import ReportProcessingStatus

@router.post(
    "/",
    response_model=CompanySummary,
    status_code=status.HTTP_201_CREATED,
)
def create_private_company(
    payload: CompanyProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CompanySummary:
    company_name = payload.name.strip()

    if not company_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Company name cannot be blank",
        )

    company = CompanyProfile(
        name=company_name,
        ticker_symbol=payload.ticker_symbol,
        scope="PRIVATE",
        owner_user_id=current_user.id,
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return company

@router.get(
    "/",
    response_model=list[CompanySummary],
)
def list_my_companies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CompanySummary]:
    statement = (
        select(CompanyProfile)
        .where(
            CompanyProfile.owner_user_id == current_user.id,
            CompanyProfile.scope == "PRIVATE",
        )
        .order_by(CompanyProfile.name)
    )

    companies = db.scalars(statement).all()
    return list(companies)

@router.get(
    "/{company_id}",
    response_model=CompanySummary,
)
def get_my_company(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CompanySummary:
    statement = select(CompanyProfile).where(
        CompanyProfile.id == company_id,
        CompanyProfile.owner_user_id == current_user.id,
        CompanyProfile.scope == "PRIVATE",
    )

    company = db.scalar(statement)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )

    return company

@router.patch(
    "/{company_id}",
    response_model=CompanySummary,
)
def update_my_company(
    company_id: UUID,
    payload: PrivateCompanyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CompanySummary:
    company = db.scalar(
        select(CompanyProfile).where(
            CompanyProfile.id == company_id,
            CompanyProfile.owner_user_id == current_user.id,
            CompanyProfile.scope == "PRIVATE",
        )
    )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )

    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide at least one field to update",
        )

    if "name" in updates:
        if updates["name"] is None or not updates["name"].strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Company name cannot be blank",
            )
        updates["name"] = updates["name"].strip()

    if "ticker_symbol" in updates and updates["ticker_symbol"] is not None:
        ticker = updates["ticker_symbol"].strip()
        updates["ticker_symbol"] = ticker or None

    for field, value in updates.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)

    return company

@router.get(
    "/{company_id}/reports",
    response_model=list[FinancialReportSummary],
)
def list_my_company_reports(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[FinancialReportSummary]:
    company = db.scalar(
        select(CompanyProfile).where(
            CompanyProfile.id == company_id,
            CompanyProfile.owner_user_id == current_user.id,
            CompanyProfile.scope == "PRIVATE",
        )
    )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )

    statement = (
        select(FinancialReport)
        .where(
            FinancialReport.company_profile_id == company_id,
            FinancialReport.uploaded_by_user_id == current_user.id,
            FinancialReport.origin == "USER_UPLOAD",
        )
        .order_by(FinancialReport.created_at.desc())
    )

    reports = db.scalars(statement).all()
    return list(reports)

@router.post(
    "/{company_id}/reports",
    response_model=ReportUploadAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_private_report(
    company_id: UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    report_type: Literal["ANNUAL", "QUARTERLY", "INTERIM"] = Form(...),
    statement_scope: Literal["CONSOLIDATED", "SEPARATE"] = Form(...),
    fiscal_year: int = Form(..., ge=1900, le=2100),
    currency: str = Form(..., min_length=3, max_length=3),
    fiscal_quarter: int | None = Form(default=None, ge=1, le=4),
    period_start: date | None = Form(default=None),
    period_end: date | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportUploadAccepted:
    company = db.scalar(
        select(CompanyProfile).where(
            CompanyProfile.id == company_id,
            CompanyProfile.owner_user_id == current_user.id,
            CompanyProfile.scope == "PRIVATE",
        )
    )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )

    if period_start and period_end and period_start > period_end:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="period_start cannot be after period_end",
        )

    currency_code = currency.strip().upper()
    if len(currency_code) != 3 or not currency_code.isascii() or not currency_code.isalpha():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="currency must be a three-letter code",
        )

    try:
        storage_key, original_filename = await save_private_pdf(file)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    report = FinancialReport(
        company_profile_id=company.id,
        uploaded_by_user_id=current_user.id,
        data_source_id=None,
        origin="USER_UPLOAD",
        report_type=report_type,
        statement_scope=statement_scope,
        fiscal_year=fiscal_year,
        fiscal_quarter=fiscal_quarter,
        period_start=period_start,
        period_end=period_end,
        currency=currency_code,
        original_filename=original_filename,
        storage_key=storage_key,
        status="UPLOADED",
    )

    try:
        db.add(report)
        db.flush()

        job = ExtractionJob(
            report_id=report.id,
            status="QUEUED",
            attempt_number=1,
        )
        db.add(job)
        db.commit()

        db.refresh(report)
        db.refresh(job)
    except Exception:
        db.rollback()
        delete_private_pdf(storage_key)
        raise
    background_tasks.add_task(
    process_pdf_report,
    report.id,
    )
    return ReportUploadAccepted(
        report_id=report.id,
        extraction_job_id=job.id,
        job_status="QUEUED",
        message="Report uploaded and queued for extraction",
    )
    
@router.get(
    "/{company_id}/reports/{report_id}",
    response_model=ReportProcessingStatus,
)
def get_my_report_status(
    company_id: UUID,
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportProcessingStatus:
    report = db.scalar(
        select(FinancialReport)
        .join(
            CompanyProfile,
            CompanyProfile.id == FinancialReport.company_profile_id,
        )
        .where(
            FinancialReport.id == report_id,
            FinancialReport.company_profile_id == company_id,
            CompanyProfile.owner_user_id == current_user.id,
            CompanyProfile.scope == "PRIVATE",
            FinancialReport.uploaded_by_user_id == current_user.id,
            FinancialReport.origin == "USER_UPLOAD",
        )
    )

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    job = db.scalar(
        select(ExtractionJob)
        .where(ExtractionJob.report_id == report.id)
        .order_by(ExtractionJob.created_at.desc())
        .limit(1)
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extraction job not found",
        )

    return ReportProcessingStatus(
        report_id=report.id,
        original_filename=report.original_filename,
        report_status=report.status,
        extraction_job_id=job.id,
        job_status=job.status,
        error_message=job.error_message,
        job_created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
    )