import os
import logging
from bson import ObjectId

from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from jose import JWTError, jwt

from .pydantic_forms import User, ClientUser, MasterUser
from .mongo_db import MongoDB


__all__ = [
    "get_current_client_user",
    "get_current_master_user",
    "create_access_token",
    "get_landing_page_url",
    "authenticate_user",
    "create_new_signing_log_document",
    "create_new_signing_document"
]

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# Create a logger for this module
logger = logging.getLogger(__name__)


async def get_user(mongo_db: MongoDB, personal_id: int, password: str) -> User:
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
    logger.info(f"authuser {personal_id, password}")
    user = await get_user(mongo_db, personal_id, password)
    if not user:
        return False

    return user


def get_landing_page_url(user_type: str) -> str:
    return "/master_landing_page" if user_type == "master" else "/client_landing_page"


def create_access_token(data: dict, expires_delta: timedelta or None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request, mongo_db: MongoDB) -> User:
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
    user = await get_current_user(request, mongo_db)
    if user.type != "master":
        raise ValueError("this url can be accessed by master users only")

    return user


async def get_current_client_user(request: Request, mongo_db: MongoDB) -> User:
    user = await get_current_user(request, mongo_db)
    if user.type != "client":
        raise ValueError("this url can be accessed by master users only")

    return user


def generate_user_presentation(user: ClientUser or MasterUser) -> str:
    return f"{user.first_name} {user.last_name}({user.personal_id})"


async def create_new_signing_log_document(
    mongo_db: MongoDB,
    master_user_pid: int,
    client_user_pid: int,
    item_id: ObjectId,
    quantity: int,
) -> dict:
    action = "New Signing"
    item_info = await mongo_db.get_inventory_item_by_object_id(item_id)
    master_user = await mongo_db.get_master_by_personal_id(master_user_pid)
    client_user = await mongo_db.get_client_by_personal_id(client_user_pid)
    description = f'{generate_user_presentation(client_user)} signed on {quantity} {item_info.get("name")}(color: {item_info.get("color")}, mami serial: {item_info.get("mami_serial")}).\n Issued by: {generate_user_presentation(master_user)}.'
    date = datetime.utcnow()
    return {"action": action, "description": description, "date": date}

async def create_credit_log_document(
    mongo_db: MongoDB,
    master_user_pid: int,
    client_user_pid: int,
    item_id: ObjectId,
    quantity: int,
) -> dict:
    action = "Credit"
    item_info = await mongo_db.get_inventory_item_by_object_id(item_id)
    master_user = await mongo_db.get_master_by_personal_id(master_user_pid)
    client_user = await mongo_db.get_client_by_personal_id(client_user_pid)
    description = f'{generate_user_presentation(client_user)} credited {quantity} {item_info.get("name")}(color: {item_info.get("color")}, mami serial: {item_info.get("mami_serial")}).\n Credited by: {generate_user_presentation(master_user)}.'
    date = datetime.utcnow()
    return {"action": action, "description": description, "date": date}

async def create_switch_log_document(
    mongo_db: MongoDB,
    master_user_pid: int,
    old_signer_pid: int,
    new_signer_pid: int,
    item_id: ObjectId,
    quantity: int,
) -> dict:
    action = "Switch Signing"
    item_info = await mongo_db.get_inventory_item_by_object_id(item_id)
    master_user = await mongo_db.get_master_by_personal_id(master_user_pid)
    old_signer_user = await mongo_db.get_client_by_personal_id(old_signer_pid)
    new_signer_user = await mongo_db.get_client_by_personal_id(new_signer_pid)
    description = f'{generate_user_presentation(old_signer_user)} passed to {generate_user_presentation(new_signer_user)} {quantity} {item_info.get("name")}(color: {item_info.get("color")}, mami serial: {item_info.get("mami_serial")}).\n Switched by: {generate_user_presentation(master_user)}.'
    date = datetime.utcnow()
    return {"action": action, "description": description, "date": date}

def create_new_signing_document(
    item_id: ObjectId,
    master_personal_id: int,
    client_personal_id: int,
    quantity: int,
    description: str,
):
    return {
        "item_id": item_id,
        "master_personal_id": master_personal_id,
        "client_personal_id": client_personal_id,
        "quantity": quantity,
        "description": description,
        "date": datetime.utcnow(),
    }

async def create_delete_item_log_document(
    mongo_db: MongoDB,
    item_id: ObjectId,
    master_user_pid: int
) -> dict:
    action = "Delete Inventory Item"
    item_info = await mongo_db.get_inventory_item_by_object_id(item_id)
    master_user = await mongo_db.get_master_by_personal_id(master_user_pid)
    description = f'{generate_user_presentation(master_user)} deleted item from inventory: {item_info.get("name")}(color: {item_info.get("color")}, mami serial: {item_info.get("mami_serial")}).'
    date = datetime.utcnow()
    return {"action": action, "description": description, "date": date}