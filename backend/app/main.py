from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.datasets import router as datasets_router
from app.api.dataset_versions import router as dataset_versions_router
from app.services.storage import ensure_bucket_exists
from app.api.jobs import router as jobs_router
from app.api.indexes import router as indexes_router
from app.api.search import router as search_router
from app.api.eval import router as eval_router
from app.api.search_logs import router as search_logs_router

import app.models  # noqa: F401

app = FastAPI(title="ShiftScope API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    ensure_bucket_exists()


@app.get("/")
def read_root():
    return {
        "message": "ShiftScope backend is running",
        "database_url": settings.database_url,
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(datasets_router)
app.include_router(dataset_versions_router)
app.include_router(jobs_router)
app.include_router(indexes_router)
app.include_router(search_router)
app.include_router(eval_router)
app.include_router(search_logs_router)