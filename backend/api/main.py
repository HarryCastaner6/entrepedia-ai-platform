"""
FastAPI main application with all routes and middleware.
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn

from backend.utils.config import settings
from backend.utils.logger import app_logger
from backend.utils.security import decode_access_token
from backend.api.routes import auth_db as auth, documents, query, integrations, settings


security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    app_logger.info("Starting Entrepedia AI Platform API")

    # Initialize database
    from backend.database.database import init_db
    try:
        init_db()
        app_logger.info("Database initialized successfully")
    except Exception as e:
        app_logger.error(f"Failed to initialize database: {e}")
        raise

    yield
    app_logger.info("Shutting down Entrepedia AI Platform API")


# Initialize FastAPI app
app = FastAPI(
    title="Entrepedia AI Platform",
    description="""
    🎓 **AI-Enhanced Education Platform**
    
    A comprehensive platform for intelligent learning with:
    - 📄 Multi-format document processing (Text, PDF, Images, Audio)
    - 🧠 RAG-powered knowledge base with vector search
    - 🤖 AI Agents (Coach & Strategist) for personalized guidance
    - 📚 Entrepedia course scraping and integration
    - 🔐 Secure authentication and user management
    
    **Quick Start:**
    1. Login with `testuser` / `test123`
    2. Upload documents via `/documents/upload`
    3. Query knowledge base via `/query/search`
    4. Get AI guidance via `/query/ask`
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Entrepedia AI Platform",
        "url": "https://app.entrepedia.co",
    },
    license_info={
        "name": "MIT",
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",  # Vite dev server alternate port
        "http://localhost:5173",  # Vite default port
        "http://localhost:5174",  # Vite alternate port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all incoming requests."""
    import time
    start_time = time.time()
    
    # Log request
    app_logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response time
    process_time = time.time() - start_time
    app_logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
    
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all unhandled exceptions."""
    app_logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "success": False,
        "error": "Internal server error",
        "detail": str(exc) if settings.debug else "An unexpected error occurred"
    }


# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user info."""
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check():
    """
    Health check endpoint.
    
    Returns system status and version information.
    """
    from backend.embeddings.vector_store import global_vector_store
    
    # Check vector store status
    vector_store_status = "healthy"
    vector_count = 0
    try:
        if global_vector_store.index is not None:
            vector_count = global_vector_store.index.ntotal
    except:
        vector_store_status = "unavailable"
    
    return {
        "status": "healthy",
        "app": settings.app_name,
        "environment": settings.app_env,
        "version": "1.0.0",
        "components": {
            "api": "healthy",
            "vector_store": vector_store_status,
            "vector_count": vector_count
        }
    }


# Root endpoint
@app.get("/", tags=["system"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Entrepedia AI Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/debug-system", tags=["system"])
async def debug_system():
    """Debug system configuration and connectivity."""
    import os
    import sys
    
    results = {
        "python_version": sys.version,
        "env_vars": {
            "DATABASE_URL_SET": "DATABASE_URL" in os.environ,
            "SUPABASE_URL_SET": "SUPABASE_URL" in os.environ,
            "GEMINI_API_KEY_SET": "GEMINI_API_KEY" in os.environ,
        },
        "imports": {},
        "database": {}
    }
    
    # Check imports
    try:
        import psycopg2
        results["imports"]["psycopg2"] = f"Success: {psycopg2.__version__}"
    except ImportError as e:
        results["imports"]["psycopg2"] = f"Failed: {e}"
        
    try:
        import bcrypt
        results["imports"]["bcrypt"] = "Success"
    except ImportError as e:
        results["imports"]["bcrypt"] = f"Failed: {e}"
        
    try:
        from sqlalchemy import create_engine, text
        results["imports"]["sqlalchemy"] = f"Success: {sqlalchemy.__version__}"
        
        # Test DB Connection
        try:
            db_url = os.environ.get("DATABASE_URL")
            if db_url:
                engine = create_engine(db_url)
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    results["database"]["connection"] = f"Success: {result.scalar()}"
            else:
                results["database"]["connection"] = "Failed: DATABASE_URL not set"
        except Exception as e:
            results["database"]["connection"] = f"Failed: {e}"
            
    except ImportError as e:
        results["imports"]["sqlalchemy"] = f"Failed: {e}"
        
    return results


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(query.router, prefix="/query", tags=["query"])
app.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
app.include_router(settings.router, prefix="/settings", tags=["settings"])


if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )