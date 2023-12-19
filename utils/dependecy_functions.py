import os
from .mongo_db import MongoDB


SECRET_KEY = "7f4aefaacda0e25168873895a24f3009025bd52eabca0c99083d15b45ece651c"
ALGORITHM = "HS256"


async def get_mongo_db():
    """
    Coroutine function to create and yield a MongoDB instance.

    Yields:
        MongoDB: Instance of MongoDB.
    """
    print("starts mongo db connection")
    MONGO_URL = os.getenv("MONGO_URL")
    DATA_BASE_NAME = os.getenv("DATA_BASE_NAME")
    mongo_db = MongoDB(MONGO_URL, DATA_BASE_NAME)
    try:
        yield mongo_db
    finally:
        print("closing mongo db connection")
        mongo_db.close_session()
