from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from .api import router
from .database import create_tables

# Load environment variables
load_dotenv()

# Create FastAPI app instance
app = FastAPI(
    title="AI-Powered Resume API",
    description="A comprehensive API for serving resume data with AI-powered query capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)

@app.get("/")
async def root():
    """Root endpoint with welcome message"""
    return {
        "message": "Welcome to the AI-Powered Resume API",
        "description": "An intelligent resume platform with RAG-based query capabilities",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "profile": "/api/v1/profile",
            "query": "/api/v1/query-resume",
            "sync": "/api/v1/sync-vector-db"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Startup event to initialize database"""
    print("🚀 Starting AI Resume API...")
    
    # Create database tables
    try:
        create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
    
    print("🎉 AI Resume API is ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    print("👋 Shutting down AI Resume API...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
