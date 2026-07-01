from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import get_session
from app.utils import sanitize_string

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
        health["error"] = f"An error occurred: {sanitize_string(e)}"
    
    return health