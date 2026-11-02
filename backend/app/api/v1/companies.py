from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.models.company_profile import CompanyProfile
from app.schemas.company import CompanySummary
from app.models.financial_report import FinancialReport
from app.schemas.financial_report import FinancialReportSummary
from app.models.metric_run import MetricRun
from app.models.metric_result import MetricResult
from app.schemas.metric import MetricResultResponse
from app.models.forecast_run import ForecastRun
from app.schemas.forecast import ForecastRunSummary
from app.models.forecast_point import ForecastPoint
from app.schemas.forecast import ForecastPointResponse
from app.schemas.comparison import CompanyMetricComparison
from datetime import date

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

@router.get(
    "/{company_id}/metrics",
    response_model=list[MetricResultResponse],
)
def list_company_metrics(
    company_id: UUID,
    db: Session = Depends(get_db),
) -> list[MetricResultResponse]:
    latest_run_statement = (
        select(MetricRun.id)
        .join(
            CompanyProfile,
            CompanyProfile.id == MetricRun.company_profile_id,
        )
        .where(
            MetricRun.company_profile_id == company_id,
            CompanyProfile.scope == "SHARED",
            MetricRun.status == "COMPLETED",
        )
        .order_by(MetricRun.finished_at.desc())
        .limit(1)
    )

    latest_run_id = db.scalar(latest_run_statement)

    if latest_run_id is None:
        return []

    results_statement = (
        select(MetricResult)
        .where(MetricResult.metric_run_id == latest_run_id)
        .order_by(
            MetricResult.period_end.desc(),
            MetricResult.metric_code,
        )
    )

    results = db.scalars(results_statement).all()
    return list(results)

@router.get(
    "/{company_id}/forecasts",
    response_model=list[ForecastRunSummary],
)
def list_company_forecast_runs(
    company_id: UUID,
    db: Session = Depends(get_db),
) -> list[ForecastRunSummary]:
    statement = (
        select(ForecastRun)
        .join(
            CompanyProfile,
            CompanyProfile.id == ForecastRun.company_profile_id,
        )
        .where(
            ForecastRun.company_profile_id == company_id,
            CompanyProfile.scope == "SHARED",
        )
        .order_by(ForecastRun.created_at.desc())
    )

    forecast_runs = db.scalars(statement).all()
    return list(forecast_runs)


@router.get(
    "/{company_id}/forecasts/{forecast_run_id}/points",
    response_model=list[ForecastPointResponse],
)
def list_forecast_points(
    company_id: UUID,
    forecast_run_id: UUID,
    db: Session = Depends(get_db),
) -> list[ForecastPointResponse]:
    run_statement = (
        select(ForecastRun)
        .join(
            CompanyProfile,
            CompanyProfile.id == ForecastRun.company_profile_id,
        )
        .where(
            ForecastRun.id == forecast_run_id,
            ForecastRun.company_profile_id == company_id,
            CompanyProfile.scope == "SHARED",
        )
    )

    forecast_run = db.scalar(run_statement)

    if forecast_run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared company forecast not found",
        )

    if forecast_run.status != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Forecast run is not completed",
        )

    points_statement = (
        select(ForecastPoint)
        .where(ForecastPoint.forecast_run_id == forecast_run_id)
        .order_by(ForecastPoint.step_number)
    )

    points = db.scalars(points_statement).all()
    return list(points)


@router.get(
    "/compare",
    response_model=list[CompanyMetricComparison],
)
def compare_company_metric(
    company_ids: list[UUID] = Query(...),
    metric_code: str = Query(..., min_length=1),
    period_end: date = Query(...),
    db: Session = Depends(get_db),
) -> list[CompanyMetricComparison]:
    if not 2 <= len(company_ids) <= 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide between 2 and 5 company IDs",
        )

    if len(set(company_ids)) != len(company_ids):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Company IDs must be unique",
        )

    companies_statement = select(CompanyProfile).where(
        CompanyProfile.id.in_(company_ids),
        CompanyProfile.scope == "SHARED",
    )
    companies = db.scalars(companies_statement).all()

    if len(companies) != len(company_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more shared companies were not found",
        )

    results_statement = (
        select(CompanyProfile, MetricRun, MetricResult)
        .join(
            MetricRun,
            MetricRun.company_profile_id == CompanyProfile.id,
        )
        .join(
            MetricResult,
            MetricResult.metric_run_id == MetricRun.id,
        )
        .where(
            CompanyProfile.id.in_(company_ids),
            CompanyProfile.scope == "SHARED",
            MetricRun.status == "COMPLETED",
            MetricResult.metric_code == metric_code,
            MetricResult.period_end == period_end,
        )
        .order_by(
            MetricRun.finished_at.desc().nullslast(),
            MetricRun.started_at.desc(),
        )
    )

    rows = db.execute(results_statement).all()

    latest_result_by_company: dict[UUID, CompanyMetricComparison] = {}

    for company, _run, result in rows:
        if company.id not in latest_result_by_company:
            latest_result_by_company[company.id] = CompanyMetricComparison(
                company_id=company.id,
                company_name=company.name,
                ticker_symbol=company.ticker_symbol,
                metric_code=result.metric_code,
                period_end=result.period_end,
                value=result.value,
                unit=result.unit,
                result_status=result.result_status,
            )

    return [
        latest_result_by_company.get(company.id)
        or CompanyMetricComparison(
            company_id=company.id,
            company_name=company.name,
            ticker_symbol=company.ticker_symbol,
            metric_code=metric_code,
            period_end=period_end,
            value=None,
            unit=None,
            result_status="NO_DATA",
        )
        for company in companies
    ]