from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils.mongo_db import MongoDB
from utils.pydantic_forms import LoginForm, MasterAccount, ClientAccount


async def get_mongo_db():
    print("starts mongo db connection")
    MONGO_URL = "mongodb://admin:password@localhost:27017"
    MONGO_DB_NAME = "ecs"
    mongo_db = MongoDB(MONGO_URL, MONGO_DB_NAME)
    try:
        yield mongo_db
    finally:
        print("closing mongo db connection")
        mongo_db.close_session()


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mount folders as static directories
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/vendor", StaticFiles(directory="vendor"), name="vendor")


# Serve the index.html file
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/master_landing_page", response_class=HTMLResponse)
def master_landing_page(request: Request):
    return templates.TemplateResponse(
        "/services/master_landing_page.html", {"request": request}
    )


@app.post("/login")
async def login(login_data: LoginForm, mongo_db: MongoDB = Depends(get_mongo_db)):
    personal_id = login_data.personal_id
    password = login_data.password
    print(login_data)
    if await mongo_db.login_master(personal_id, password):
        return {"redirect_url": "/master_landing_page"}
    elif await mongo_db.login_client(personal_id, password):
        print("this is a client user")
    raise HTTPException(status_code=400, detail="this user was not found")


@app.post("/create_master_account")
async def create_master_account(
    master_account_data: MasterAccount, mongo_db: MongoDB = Depends(get_mongo_db)
):
    print(master_account_data)
    account_dict = dict(master_account_data)
    try:
        if not await mongo_db.is_master_password(account_dict.get("master_password")):
            raise ValueError("master password is incorrect")

        if await mongo_db.is_existing_master(account_dict.get("personal_id")):
            raise ValueError(
                f'this personal id is already used: {account_dict.get("personal_id")}'
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
    print(client_account_data)
    account_dict = dict(client_account_data)
    try:
        if not await mongo_db.is_master_password(account_dict.get("master_password")):
            raise ValueError("master password is incorrect")

        if await mongo_db.is_existing_client(account_dict.get("personal_id")):
            raise ValueError(
                f'this personal id is already used: {account_dict.get("personal_id")}'
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
