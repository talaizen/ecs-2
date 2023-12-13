from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils.mongo_db import MongoDB
from utils.pydantic_forms import LoginForm, MasterAccount

# Initiating mongo db connection at app startup
MONGO_URL = "mongodb://admin:password@localhost:27017"
MONGO_DB_NAME = "ecs"
mongo_db = MongoDB(MONGO_URL, MONGO_DB_NAME)


# Closing mongo db connection at app shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("starting app")
    yield
    print("closing mongo connection")
    mongo_db.close_session()


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

# Mount folders as static directories
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/vendor", StaticFiles(directory="vendor"), name="vendor")


# Serve the index.html file
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/login")
async def login(login_data: LoginForm):
    username = login_data.username
    password = login_data.password
    print(username, password)
    return {"message": "Login successful"}


@app.post("/create_master_account")
async def create_master_account(master_account_data: MasterAccount):
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
