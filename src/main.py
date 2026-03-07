from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path

from src.core.database import engine, Base, SessionLocal
from src.core.config import CONFIG_DIR
from src.api import config
from src.api import data
from src.api import dashboard
from src.api import analysis
from src.api import auth
from src.api import vector
from src.api import mcp
from src.api import config_async
from src.api import data_async
from src.api import dashboard_async
from src.api import ai
from src.api import feedback
from src.api import conversation
from src.api import settings
from src.api import chart_export
from src.api import echarts_api
from src.api import chart_recommend
from src.api import chart_config
from src.mcp import mcp_client
from src.services.auth import create_admin_user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PB-BI 数据分析平台 API", version="1.0.0")

CHARTS_DIR = CONFIG_DIR / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/api/charts", StaticFiles(directory=str(CHARTS_DIR)), name="charts")

def allow_all_origins(request: Request):
    return request.headers.get("origin", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://.*:300[0-9]|http://localhost:300[0-9]",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key="pb-bi-secret-key-change-in-production",
    max_age=86400,
    same_site="lax",
    https_only=False,
)

app.include_router(auth.router)
app.include_router(config.router)
app.include_router(config_async.router)
app.include_router(data.router)
app.include_router(data_async.router)
app.include_router(dashboard.router)
app.include_router(dashboard_async.router)
app.include_router(analysis.router)
app.include_router(vector.router)
app.include_router(mcp.router)
app.include_router(mcp_client.router)
app.include_router(ai.router)
app.include_router(feedback.router)
app.include_router(conversation.router)
app.include_router(settings.router)
app.include_router(chart_export.router)
app.include_router(echarts_api.router)
app.include_router(chart_recommend.router)
app.include_router(chart_config.router)

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        create_admin_user(db)
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "NEDI数据分析平台 API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
