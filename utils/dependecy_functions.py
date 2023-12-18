from fastapi import Request, HTTPException, Depends, status
from jose import JWTError, jwt

from .mongo_db import MongoDB
from .helpers import get_user


SECRET_KEY = "7f4aefaacda0e25168873895a24f3009025bd52eabca0c99083d15b45ece651c"
ALGORITHM = "HS256"


async def get_mongo_db():
    """
    Coroutine function to create and yield a MongoDB instance.

    Yields:
        MongoDB: Instance of MongoDB.
    """
    print("starts mongo db connection")
    MONGO_URL = "mongodb://admin:password@localhost:27017"
    MONGO_DB_NAME = "ecs"
    mongo_db = MongoDB(MONGO_URL, MONGO_DB_NAME)
    try:
        yield mongo_db
    finally:
        print("closing mongo db connection")
        mongo_db.close_session()

async def get_current_user(request: Request, mongo_db: MongoDB = Depends(get_mongo_db)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token = request.cookies.get("access_token")
    if not token:
        raise credential_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        personal_id: int = int(payload.get("sub"))
        password: str = payload.get("pwd")
        if personal_id is None:
            raise credential_exception
    except JWTError:
        raise credential_exception
    
    user = await get_user(mongo_db, personal_id, password)
    if user is None:
        raise credential_exception
    
    return user
