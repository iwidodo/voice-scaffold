"""
FastAPI application entry point for appointment scheduling system.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import config
from backend.api import appointments, conversation

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
logger.info("[main.py.root] Creating FastAPI application")
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="LLM-powered appointment scheduling system with healthcare providers"
)

# CORS middleware
logger.info("[main.py.root] Configuring CORS middleware")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
logger.info("[main.py.root] Including API routers")
app.include_router(appointments.router)
app.include_router(conversation.router)


@app.get("/")
async def root():
    """Root endpoint."""
    logger.info("[main.py.root] Root endpoint accessed")
    return {
        "message": "Appointment Scheduler API",
        "version": config.APP_VERSION,
        "endpoints": {
            "conversation": "/api/conversation",
            "appointments": "/api/appointments",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("[main.py.health_check] Health check endpoint accessed")
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
