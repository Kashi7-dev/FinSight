from fastapi import FastAPI

from app.api.v1.companies import router as companies_router

app = FastAPI(
    title="FinSight API",
    description="API phân tích báo cáo tài chính",
    version="0.1.0",
)

app.include_router(companies_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}