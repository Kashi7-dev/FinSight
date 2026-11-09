from fastapi import FastAPI
from app.api.v1.reports import router as reports_router
from app.api.v1.companies import router as companies_router
from app.api.v1.auth import router as auth_router
from app.api.v1.private_companies import router as private_companies_router
app = FastAPI(
    title="FinSight API",
    description="API phân tích báo cáo tài chính",
    version="0.1.0",
)

app.include_router(companies_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(private_companies_router, prefix="/api/v1")
@app.get("/health")
def health_check():
    return {"status": "ok"}