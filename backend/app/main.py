import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import get_session
from app.routes.auth import router as auth_router
from app.utils import sanitize_string, get_logger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = get_logger()

app = FastAPI(
    title="JobHuntr",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True, # for OAuth2/JWT later
    allow_methods=["*"],
    allow_headers=["*"]
)

logger.debug("Loading auth routes")
app.include_router(auth_router)

@app.get("/health")
async def root():
    health = {"status": "ok", "database": "unreachable"}
    try:
        db = next(get_session())
        db.execute(text("SELECT 1"))
        health["database"] = "connected"
    except Exception as e:
        health["error"] = f"An error occurred: {sanitize_string(str(e))}"
    
    return health