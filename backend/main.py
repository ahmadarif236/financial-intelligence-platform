import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from database import engine, Base

# Import all models to ensure they are registered with SQLAlchemy
from models.user import User
from models.company import Company
from models.upload import Upload
from models.account import MasterAccount, AccountMapping
from models.financial_data import TrialBalanceEntry, GeneralLedgerEntry

# Import routers
from routers import auth, company, upload, mapping, statements, ratios, ai_commentary, dashboard, export

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Financial Intelligence Platform for GCC CFOs",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for Vercel + HF
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(company.router)
app.include_router(upload.router)
app.include_router(mapping.router)
app.include_router(statements.router)
app.include_router(ratios.router)
app.include_router(ai_commentary.router)
app.include_router(dashboard.router)
app.include_router(export.router)


@app.on_event("startup")
def startup():
    # Create data directory
    os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "uploads"), exist_ok=True)

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started successfully!")


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


