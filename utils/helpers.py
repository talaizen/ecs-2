from datetime import datetime, timedelta
from jose import jwt

from .pydantic_forms import User
from .mongo_db import MongoDB


SECRET_KEY = "7f4aefaacda0e25168873895a24f3009025bd52eabca0c99083d15b45ece651c"
ALGORITHM = "HS256"


async def get_user(mongo_db: MongoDB, personal_id: int, password: str) -> User:
    print(f"get user {personal_id, password}")

    master_user = await mongo_db.get_master_user(personal_id, password)
    if master_user:
        return User(
            type="master",
            full_name= f'{master_user.get("first_name")} {master_user.get("last_name")}',
            personal_id=master_user.get("personal_id"),
            password=master_user.get("password"),
            email=master_user.get("email")
        )
    
    client_user = await mongo_db.get_client_user(personal_id, password)
    if client_user:
        return User(
            type="client",
            full_name= f'{client_user.get("first_name")} {client_user.get("last_name")}',
            personal_id=client_user.get("personal_id"),
            password=client_user.get("password"),
            email=client_user.get("email"),
            palga=client_user.get("palga"),
            team=client_user.get("team")
        )
    
    
async def authenticate_user(mongo_db: MongoDB, personal_id: int, password: str) -> User:
    print(f'authuser {personal_id, password}')
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