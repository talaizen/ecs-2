import os
import logging
from .mongo_db import MongoDB

# Create a logger for this module
logger = logging.getLogger(__name__)


async def get_mongo_db():
    """
    Coroutine function to create and yield a MongoDB instance.

    Yields:
        MongoDB: Instance of MongoDB.
    """
    logger.info("starts mongo db connection")
    MONGO_URL = os.getenv("MONGO_URL")
    DATA_BASE_NAME = os.getenv("DATA_BASE_NAME")
    mongo_db = MongoDB(MONGO_URL, DATA_BASE_NAME)
    try:
        yield mongo_db
    finally:
        logger.info("closing mongo db connection")
        mongo_db.close_session()
