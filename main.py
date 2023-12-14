from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils.mongo_db import MongoDB
from utils.pydantic_forms import LoginForm, MasterAccount, ClientAccount


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


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mount folders as static directories
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/vendor", StaticFiles(directory="vendor"), name="vendor")


@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    """
    Route to serve the index.html file.

    Args:
        request (Request): The incoming request.

    Returns:
        TemplateResponse: HTML response containing the index.html content.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/master_landing_page", response_class=HTMLResponse)
def master_landing_page(request: Request):
    """
    Route to serve the master landing page.

    Args:
        request (Request): The incoming request.

    Returns:
        TemplateResponse: HTML response containing the master landing page content.
    """
    return templates.TemplateResponse("/services/master_landing_page.html", {"request": request})


@app.get("/client_landing_page", response_class=HTMLResponse)
def client_landing_page(request: Request):
    """
    Route to serve the client landing page.

    Args:
        request (Request): The incoming request.

    Returns:
        TemplateResponse: HTML response containing the client landing page content.
    """
    return templates.TemplateResponse("/services/client_landing_page.html", {"request": request})



@app.post("/login")
async def login(login_data: LoginForm, mongo_db: MongoDB = Depends(get_mongo_db)):
    """
    Route to authenticate a user and redirect to the master landing page.

    Args:
        login_data (LoginForm): User login credentials.
        mongo_db (MongoDB): MongoDB instance.

    Returns:
        dict: Redirect URL for successful authentication.

    Raises:
        HTTPException: If the user is not found.
    """
    print(login_data)
    personal_id = login_data.personal_id
    password = login_data.password

    if await mongo_db.login_master(personal_id, password):
        return {"redirect_url": "/master_landing_page"}
    
    elif await mongo_db.login_client(personal_id, password):
        return {"redirect_url": "/client_landing_page"}

    raise HTTPException(status_code=400, detail="User was not found")



@app.post("/create_master_account")
async def create_master_account(master_account_data: MasterAccount, mongo_db: MongoDB = Depends(get_mongo_db)):
    """
    Route to create a master account.

    Args:
        master_account_data (MasterAccount): Master account details.
        mongo_db (MongoDB): MongoDB instance.

    Raises:
        HTTPException: If there are validation errors or the personal ID is already in use.
    """
    print(master_account_data)
    account_dict = dict(master_account_data)

    if not await mongo_db.is_master_password(account_dict.get("master_password")):
        raise HTTPException(status_code=400, detail="master password is incorrect")

    if await mongo_db.is_existing_master(account_dict.get("personal_id")):
        raise HTTPException(status_code=400, detail=f'this personal id is already used: {account_dict.get("personal_id")}')

    user_data = {
        "first_name": account_dict.get("first_name"),
        "last_name": account_dict.get("last_name"),
        "personal_id": account_dict.get("personal_id"),
        "email": account_dict.get("email"),
        "password": account_dict.get("password")
    }
    await mongo_db.insert_master_account(user_data)


@app.post("/create_client_account")
async def create_client_account(client_account_data: ClientAccount, mongo_db: MongoDB = Depends(get_mongo_db)):
    """
    Route to create a client account.

    Args:
        client_account_data (ClientAccount): Client account details.
        mongo_db (MongoDB): MongoDB instance.

    Raises:
        HTTPException: If there are validation errors or the personal ID is already in use.
    """
    print(client_account_data)
    account_dict = dict(client_account_data)

    if not await mongo_db.is_master_password(account_dict.get("master_password")):
        raise HTTPException(status_code=400, detail="master password is incorrect")

    if await mongo_db.is_existing_client(account_dict.get("personal_id")):
        raise HTTPException(status_code=400, detail=f'this personal id is already used: {account_dict.get("personal_id")}')

    user_data = {
        "first_name": account_dict.get("first_name"),
        "last_name": account_dict.get("last_name"),
        "personal_id": account_dict.get("personal_id"),
        "email": account_dict.get("email"),
        "palga": account_dict.get("palga"),
        "team": account_dict.get("team"),
        "password": account_dict.get("password")
    }
    await mongo_db.insert_client_account(user_data)
