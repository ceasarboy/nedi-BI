from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.database import engine, Base
from src.api import config
from src.api import data
from src.api import dashboard
from src.api import analysis

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NEDI数据分析平台 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(config.router)
app.include_router(data.router)
app.include_router(dashboard.router)
app.include_router(analysis.router)

@app.get("/")
async def root():
    return {"message": "NEDI数据分析平台 API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
