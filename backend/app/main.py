import time
import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlmodel import Session
from app.db.database import engine, get_session, create_db_and_tables
from app.api.tasks import router as tasks_router
from app.api.routes.chat import router as chatbot_router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    print("Starting up the application...")

    # Create database tables if they don't exist
    create_db_and_tables()
    print("Database tables created/verified successfully.")

    # Verify database connectivity
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
        print("Database connection established successfully.")
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise

    yield

    # Shutdown
    print("Shutting down the application...")


app = FastAPI(
    title="Todo Backend API",
    description="REST API for managing user tasks with JWT authentication",
    version="1.0.0",
    lifespan=lifespan
)


# Logging and performance monitoring middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log incoming requests and add timing information to responses.
    """
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")

    try:
        response = await call_next(request)

        # Calculate process time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        # Log response
        logger.info(f"Response: {response.status_code} in {process_time:.2f}s")

        return response
    except Exception as e:
        # Log exceptions
        process_time = time.time() - start_time
        logger.error(f"Request failed: {request.method} {request.url.path} - {str(e)} in {process_time:.2f}s")
        raise


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(tasks_router)
app.include_router(chatbot_router, prefix="/api/v1")  # Cohere chatbot at /api/v1/{user_id}/chat

@app.get("/")
async def root():
    """
    Root endpoint for the API.
    """
    return {"message": "Welcome to the Todo Backend API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API and database connectivity.
    """
    try:
        # Test database connectivity
        with Session(engine) as session:
            result = session.exec(text("SELECT 1")).first()

        return {
            "status": "healthy",
            "database": "connected",
            "message": "API is running and database is accessible"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

@app.get("/health/database")
async def database_health_check(session: Session = Depends(get_session)):
    """
    Database health check endpoint to verify database connectivity.
    """
    try:
        result = session.exec(text("SELECT 1")).first()
        return {
            "status": "healthy",
            "database": "connected",
            "message": "Database is accessible and responding"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

# Additional API documentation endpoints are automatically available at:
# /docs - Swagger UI
# /redoc - ReDoc