"""
TenderLens - Main Application Entrypoint
========================================
Runs the unified FastAPI application via Uvicorn.
"""

import uvicorn
from backend.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )
