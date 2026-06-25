import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger("integration.helpers")

def check_env() -> bool:
    """Loads environment variables and checks that API keys are set."""
    load_dotenv()
    google_key = os.getenv("GOOGLE_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not google_key:
        logger.warning("GOOGLE_API_KEY is not set in environment variables/dotenv.")
    if not tavily_key:
        logger.warning("TAVILY_API_KEY is not set in environment variables/dotenv.")
        
    return bool(google_key)

def clean_reports_dir(dir_name: str = "reports"):
    """Ensures reports directory exists and is clean."""
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
