import os
import logging
from dotenv import load_dotenv
from .logger_config import setup_logging


def initialize():
    # Setup logging configuration
    setup_logging()
    logger = logging.getLogger(__name__)

    # Load environment variables
    if os.getenv("ENVIRONMENT") != "production":
        logger.info("Loading environment variables from .env file")
        load_dotenv()
