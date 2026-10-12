import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.app.database import engine, Base
from backend.app.routes import router
from backend.app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Asynchronously create database tables if they do not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="Intelligent LLM-Based Automated Code Review and Auto-Fix System",
    description="Backend API for automated code reviews using Gemini/OpenAI.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development ease; narrow down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    # Hide password/credentials from settings.database_url if logging
    clean_db_url = settings.database_url.split("@")[-1] if "@" in settings.database_url else settings.database_url
    return {
        "status": "healthy",
        "service": "Intelligent LLM-Based Code Review API",
        "database": clean_db_url,
        "llm_configured": bool(
            settings.gemini_api_key or
            settings.openai_api_key or
            settings.deepseek_api_key or
            settings.morphllm_api_key
        )
    }

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "backend.app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        reload_dirs=["backend/app"]
    )
