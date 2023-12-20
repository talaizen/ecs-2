# Initialize configuration
import logging
from utils.init_config import initialize

initialize()

from typing import List

from fastapi import FastAPI, Request, HTTPException, Depends, Response, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import timedelta
from starlette.responses import RedirectResponse

from utils.mongo_db import MongoDB
from utils.pydantic_forms import LoginForm, MasterAccount, ClientAccount, TokenResponse, InventoryCollectionItem, ClientUserCollectionItem
from utils.dependecy_functions import get_mongo_db
from utils.helpers import *

ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Create a logger for this module
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mount folders as static directories
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/vendor", StaticFiles(directory="vendor"), name="vendor")


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request, response: Response):
    """
    Route to serve the index.html file.

    Args:
        request (Request): The incoming request.

    Returns:
        TemplateResponse: HTML response containing the index.html content.
    """
    logger.info("entering index.html, resetting cookie access token")
    response.delete_cookie(key="access_token")
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/master_landing_page", response_class=HTMLResponse)
async def master_landing_page(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    """
    Route to serve the master landing page.

    Args:
        request (Request): The incoming request.

    Returns:
        TemplateResponse: HTML response containing the master landing page content.
    """
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "/master_user/master_landing_page.html",
        {"request": request, "username": user.full_name},
    )


@app.get("/master/inventory", response_class=HTMLResponse)
async def master_landing_page(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    """
    Route to serve the master landing page.

    Args:
        request (Request): The incoming request.

    Returns:
        TemplateResponse: HTML response containing the master landing page content.
    """
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "/master_user/master_inventory.html",
        {"request": request, "username": user.full_name},
    )

@app.get("/master/client_users", response_class=HTMLResponse)
async def master_landing_page(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    """
    Route to serve the master landing page.

    Args:
        request (Request): The incoming request.

    Returns:
        TemplateResponse: HTML response containing the master landing page content.
    """
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "/master_user/master_clients_table.html",
        {"request": request, "username": user.full_name},
    )


@app.get("/client_landing_page", response_class=HTMLResponse)
async def client_landing_page(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    """
    Route to serve the client landing page.

    Args:
        request (Request): The incoming request.

    Returns:
        TemplateResponse: HTML response containing the client landing page content.
    """
    try:
        user = await get_current_client_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "/services/client_landing_page.html",
        {"request": request, "full_name": user.full_name},
    )


@app.post("/create_master_account")
async def create_master_account(
    master_account_data: MasterAccount, mongo_db: MongoDB = Depends(get_mongo_db)
):
    """
    Route to create a master account.

    Args:
        master_account_data (MasterAccount): Master account details.
        mongo_db (MongoDB): MongoDB instance.

    Raises:
        HTTPException: If there are validation errors or the personal ID is already in use.
    """
    logger.info(f"this is master account data {master_account_data}")
    account_dict = dict(master_account_data)

    if not await mongo_db.is_master_password(account_dict.get("master_password")):
        raise HTTPException(status_code=400, detail="master password is incorrect")

    if await mongo_db.is_existing_master(account_dict.get("personal_id")):
        raise HTTPException(
            status_code=400,
            detail=f'this personal id is already used: {account_dict.get("personal_id")}',
        )

    user_data = {
        "first_name": account_dict.get("first_name"),
        "last_name": account_dict.get("last_name"),
        "personal_id": account_dict.get("personal_id"),
        "email": account_dict.get("email"),
        "password": account_dict.get("password"),
    }
    await mongo_db.insert_master_account(user_data)


@app.post("/create_client_account")
async def create_client_account(
    client_account_data: ClientAccount, mongo_db: MongoDB = Depends(get_mongo_db)
):
    """
    Route to create a client account.

    Args:
        client_account_data (ClientAccount): Client account details.
        mongo_db (MongoDB): MongoDB instance.

    Raises:
        HTTPException: If there are validation errors or the personal ID is already in use.
    """
    logger.info(client_account_data)
    account_dict = dict(client_account_data)

    if not await mongo_db.is_master_password(account_dict.get("master_password")):
        raise HTTPException(status_code=400, detail="master password is incorrect")

    if await mongo_db.is_existing_client(account_dict.get("personal_id")):
        raise HTTPException(
            status_code=400,
            detail=f'this personal id is already used: {account_dict.get("personal_id")}',
        )

    user_data = {
        "first_name": account_dict.get("first_name"),
        "last_name": account_dict.get("last_name"),
        "personal_id": account_dict.get("personal_id"),
        "email": account_dict.get("email"),
        "palga": account_dict.get("palga"),
        "team": account_dict.get("team"),
        "password": account_dict.get("password"),
    }
    await mongo_db.insert_client_account(user_data)


@app.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    response: Response, login_data: LoginForm, mongo_db: MongoDB = Depends(get_mongo_db)
):
    """
    Authenticate a user and return a redirect URL.

    This endpoint authenticates a user using their personal ID and password.
    If authentication is successful, it generates an access token, sets it in an HTTP-only cookie,
    and provides a URL to redirect the user to the appropriate landing page based on their user type.

    Args:
        response (Response): The response object used to set the cookie.
        login_data (LoginForm): A form containing the user's personal ID and password.
        mongo_db (MongoDB): The MongoDB connection instance.

    Returns:
        dict: A dictionary with a `redirect_url` key containing the URL to redirect the authenticated user.

    Raises:
        HTTPException: 401 error if authentication fails (incorrect username or password).
    """
    user = await authenticate_user(
        mongo_db, login_data.personal_id, login_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.personal_id), "pwd": user.password},
        expires_delta=access_token_expires,
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=3600,
        samesite="Lax",
    )
    redirect_url = get_landing_page_url(user.type)

    return {"redirect_url": redirect_url}


@app.get("/collections-data/inventory")
async def get_inventory_data(mongo_db: MongoDB = Depends(get_mongo_db)):
    data = []
    async for document in await mongo_db.get_inventory_data():
        data.append(
            InventoryCollectionItem(
            name=document.get("name"),
            category=document.get("category"),
            count=f'{document.get("count")} / {document.get("total_count")}',
            color=document.get("color"),
            palga=document.get("palga"),
            mami_serial=document.get("mami_serial"),
            manufacture_mkt=document.get("manufacture_mkt"),
            katzi_mkt=document.get("katzi_mkt"),
            serial_no=document.get("serial_no"),
            description=document.get("description")
            )
        )
    logger.info(data)
    return data

@app.get("/collections-data/client_users")
async def get_client_users_data(mongo_db: MongoDB = Depends(get_mongo_db)):
    data = []
    async for document in await mongo_db.get_client_users_data():
        data.append(
            ClientUserCollectionItem(
                first_name=document.get("first_name"),
                last_name=document.get("last_name"),
                personal_id=document.get("personal_id"),
                email=document.get("email"),
                palga=document.get("palga"),
                team=document.get("team")
            )
        )
    logger.info(data)
    return data


    