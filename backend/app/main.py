import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from database import get_session
from utils import sanitize_string, get_logger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("JobHuntr")

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


@app.get("/health")
async def root():
    health = {"status": "ok", "database": "unreachable"}
    try:
        with get_session() as db: 
            db.execute(text("SELECT 1"))
        health["database"] = "connected"
    except Exception as e:
        health["error"] = f"An error occurred: {sanitize_string(str(e))}"
    
    return health