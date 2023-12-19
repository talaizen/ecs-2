import os
import logging
from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from jose import JWTError, jwt

from .pydantic_forms import User
from .mongo_db import MongoDB


__all__ = [
    "get_current_client_user",
    "get_current_master_user",
    "create_access_token",
    "get_landing_page_url",
    "authenticate_user",
]

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# Create a logger for this module
logger = logging.getLogger(__name__)


async def get_user(mongo_db: MongoDB, personal_id: int, password: str) -> User:
    """
    Retrieve a user (either master or client) from the database based on personal ID and password.

    Args:
        mongo_db (MongoDB): The MongoDB connection instance.
        personal_id (int): The personal ID of the user.
        password (str): The password of the user.

    Returns:
        User: A User object if the user is found, else None.
    """
    logger.info(f"get user {personal_id, password}")

    master_user = await mongo_db.get_master_user(personal_id, password)
    if master_user:
        return User(
            type="master",
            full_name=f'{master_user.get("first_name")} {master_user.get("last_name")}',
            personal_id=master_user.get("personal_id"),
            password=master_user.get("password"),
            email=master_user.get("email"),
        )

    client_user = await mongo_db.get_client_user(personal_id, password)
    if client_user:
        return User(
            type="client",
            full_name=f'{client_user.get("first_name")} {client_user.get("last_name")}',
            personal_id=client_user.get("personal_id"),
            password=client_user.get("password"),
            email=client_user.get("email"),
            palga=client_user.get("palga"),
            team=client_user.get("team"),
        )


async def authenticate_user(mongo_db: MongoDB, personal_id: int, password: str) -> User:
    """
    Authenticate a user against the database.

    Args:
        mongo_db (MongoDB): The MongoDB connection instance.
        personal_id (int): The personal ID of the user.
        password (str): The password of the user.

    Returns:
        User: A User object if authentication is successful, else False.
    """
    logger.info(f"authuser {personal_id, password}")
    user = await get_user(mongo_db, personal_id, password)
    if not user:
        return False

    return user


def get_landing_page_url(user_type: str) -> str:
    """
    Determine the landing page URL based on the user type.

    Args:
        user_type (str): The type of the user ("master" or "client").

    Returns:
        str: The URL of the landing page corresponding to the user type.
    """
    return "/master_landing_page" if user_type == "master" else "/client_landing_page"


def create_access_token(data: dict, expires_delta: timedelta or None = None) -> str:
    """
    Create a JWT access token with the given data and expiration.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (timedelta, optional): The time delta for token expiration. Defaults to 15 minutes.

    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request, mongo_db: MongoDB) -> User:
    """
    Retrieve the current user based on the access token provided in the request.

    Args:
        request (Request): The request object.
        mongo_db (MongoDB): The MongoDB connection instance.

    Raises:
        HTTPException: If the token is missing, invalid, or if no user is found.

    Returns:
        User: The authenticated User object.
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
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


async def get_current_master_user(request: Request, mongo_db: MongoDB) -> User:
    """
    Retrieve the current user as a master user.

    Args:
        request (Request): The request object.
        mongo_db (MongoDB): The MongoDB connection instance.

    Raises:
        ValueError: If the current user is not a master user.

    Returns:
        User: The authenticated master User object.
    """
    user = await get_current_user(request, mongo_db)
    if user.type != "master":
        raise ValueError("this url can be accessed by master users only")

    return user


async def get_current_client_user(request: Request, mongo_db: MongoDB) -> User:
    """
    Retrieve the current user as a client user.

    Args:
        request (Request): The request object.
        mongo_db (MongoDB): The MongoDB connection instance.

    Raises:
        ValueError: If the current user is not a client user.

    Returns:
        User: The authenticated client User object.
    """
    user = await get_current_user(request, mongo_db)
    if user.type != "client":
        raise ValueError("this url can be accessed by master users only")

    return user
