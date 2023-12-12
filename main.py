from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from utils.mongo_db import MongoDB
from forms.jason_forms import LoginForm, MasterAccount


MONGO_URL = "mongodb://admin:password@localhost:27017"
MONGO_DB_NAME = "ecs"
mongo = MongoDB(MONGO_URL, MONGO_DB_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("starting app")
    yield
    print("closing mongo connection")
    mongo.close_session()


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


# Mount folders as static directories
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/vendor", StaticFiles(directory="vendor"), name="vendor")


# Serve the index.html file
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
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
    await mongo.insert_master_account(account_dict)
