from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.core.database import engine, Base, SessionLocal
from src.api import config
from src.api import data
from src.api import dashboard
from src.api import analysis
from src.api import auth
from src.services.auth import create_admin_user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PB-BI 数据分析平台 API", version="1.0.0")

def allow_all_origins(request: Request):
    return request.headers.get("origin", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://.*:3000|http://localhost:3000",
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
app.include_router(data.router)
app.include_router(dashboard.router)
app.include_router(analysis.router)

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
