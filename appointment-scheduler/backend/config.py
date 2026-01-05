"""
Configuration management.
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Application configuration."""
    
    def __init__(self):
        """Initialize configuration."""
        logger.info("[config.py.Config.__init__] Initializing configuration")
        
        # OpenAI
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
        
        # Application
        self.APP_NAME = "Appointment Scheduler API"
        self.APP_VERSION = "1.0.0"
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        
        logger.info(f"[config.py.Config.__init__] Configuration loaded - Model: {self.OPENAI_MODEL}, Debug: {self.DEBUG}")
        
        if not self.OPENAI_API_KEY:
            logger.warning("[config.py.Config.__init__] OPENAI_API_KEY not set in environment variables")


config = Config()
