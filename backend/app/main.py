from fastapi import FastAPI

app = FastAPI(
    title="FinSight API",
    description="API phân tích báo cáo tài chính",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}