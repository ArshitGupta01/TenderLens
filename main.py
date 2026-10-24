"""
TenderLens - Main Application Entrypoint
========================================
Exposes top-level FastAPI instance for Vercel Serverless and Uvicorn.
"""

import uvicorn
from backend.main import app
from backend.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )
