#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src" / "backend"))

from main import app
import uvicorn
from config import settings

if __name__ == "__main__":
    print(f"Starting {settings.APP_NAME} backend...")
    print(f"URL: http://{settings.FASTAPI_HOST}:{settings.FASTAPI_PORT}")
    
    uvicorn.run(
        app,
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=settings.DEBUG
    )