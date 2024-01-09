# Initialize configuration
import logging
from utils.init_config import initialize

initialize()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from routes.general_routes.registration_routes import router as registration_router
from routes.general_routes.authentication_routes import router as authentication_router
from routes.general_routes.landing_pages_routes import router as landing_pages_routes

from routes.master_routes.tables_routes import router as master_tables_routes
from routes.master_routes.tables_data_routes import router as master_tables_data_routes
from routes.master_routes.get_actions_routes import router as master_get_actions_routes
from routes.master_routes.post_actions_routes import router as master_post_actions_routes

from routes.client_routes.tables_routes import router as client_tables_routes
from routes.client_routes.tables_data_routes import router as client_tables_data_routes
from routes.client_routes.get_actions_routes import router as client_get_actions_routes
from routes.client_routes.post_actions_routes import router as client_post_actions_routes

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="ecs")

templates = Jinja2Templates(directory="templates")

# Mount folders as static directories
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/vendor", StaticFiles(directory="vendor"), name="vendor")

# General routes
app.include_router(registration_router)
app.include_router(authentication_router)
app.include_router(landing_pages_routes)

# Master routes
app.include_router(master_tables_routes)
app.include_router(master_tables_data_routes)
app.include_router(master_get_actions_routes)
app.include_router(master_post_actions_routes)

# Client routes
app.include_router(client_tables_routes)
app.include_router(client_tables_data_routes)
app.include_router(client_get_actions_routes)
app.include_router(client_post_actions_routes)
