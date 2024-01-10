import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from utils.mongo_db import MongoDB
from utils.pydantic_forms import MasterAccount, ClientAccount
from utils.dependecy_functions import get_mongo_db


logger = logging.getLogger(__name__)

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/master_signup", response_class=HTMLResponse)
async def master_signup(request: Request):
    return templates.TemplateResponse("master-signup.html", {"request": request})


@router.get("/client_signup", response_class=HTMLResponse)
async def client_signup(request: Request):
    return templates.TemplateResponse("client-signup.html", {"request": request})


@router.post("/create_master_account")
async def create_master_account(
    master_account_data: MasterAccount, mongo_db: MongoDB = Depends(get_mongo_db)
):
    if not await mongo_db.is_master_password(master_account_data.master_password):
        raise HTTPException(status_code=400, detail="master password is incorrect")

    if await mongo_db.is_existing_master(master_account_data.personal_id):
        raise HTTPException(
            status_code=400,
            detail=f"this personal id is already used: {master_account_data.personal_id}",
        )

    user_data = {
        "first_name": master_account_data.first_name,
        "last_name": master_account_data.last_name,
        "personal_id": master_account_data.personal_id,
        "email": master_account_data.email,
        "password": master_account_data.password,
    }
    await mongo_db.insert_master_account(user_data)


@router.post("/create_client_account")
async def create_client_account(
    client_account_data: ClientAccount, mongo_db: MongoDB = Depends(get_mongo_db)
):
    if not await mongo_db.is_master_password(client_account_data.master_password):
        raise HTTPException(status_code=400, detail="master password is incorrect")

    if await mongo_db.is_existing_client(client_account_data.personal_id):
        raise HTTPException(
            status_code=400,
            detail=f"this personal id is already used: {client_account_data.personal_id}",
        )

    user_data = {
        "first_name": client_account_data.first_name,
        "last_name": client_account_data.last_name,
        "personal_id": client_account_data.personal_id,
        "email": client_account_data.email,
        "palga": client_account_data.palga,
        "team": client_account_data.team,
        "password": client_account_data.password,
    }
    await mongo_db.insert_client_account(user_data)
