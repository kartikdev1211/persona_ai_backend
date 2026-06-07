from fastapi import FastAPI
from sqlalchemy import text
from app.db.database import engine, Base
import app.models
from app.core.security import hash_password
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.assessment import router as assessment_router
from app.api.v1.routes.persona import router as persona_router
app = FastAPI(
    title="PersonaAI Backend",
    version="1.0.0"
)
app.include_router(auth_router)
app.include_router(assessment_router)
app.include_router(persona_router)
Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Persona AI Backend is running"}

@app.get("/health")
async def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {
            "status":"success",
            "database": "connected"
        }
    except Exception as e:
        return{
            "status":"error",
            "database": str(e)
        }

@app.get("/test-hash")
async def test_hash():
    hashed=hash_password("password123")
    return{
        "hashed_password":hashed
    }