import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from utils.mongo_db import MongoDB
from utils.dependecy_functions import get_mongo_db
from utils.helpers import get_current_client_user


logger = logging.getLogger(__name__)

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/client/inventory", response_class=HTMLResponse)
async def client_inventory(request: Request, mongo_db: MongoDB = Depends(get_mongo_db)):
    try:
        user = await get_current_client_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "/client_user/client_inventory.html",
        {"request": request, "username": user.full_name},
    )


@router.get("/client/signings", response_class=HTMLResponse)
async def client_signings(request: Request, mongo_db: MongoDB = Depends(get_mongo_db)):
    try:
        user = await get_current_client_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "/client_user/client_signings.html",
        {"request": request, "username": user.full_name},
    )


@router.get("/client/switch_requests", response_class=HTMLResponse)
async def client_switch_requests(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user = await get_current_client_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "/client_user/client_switch_requests.html",
        {"request": request, "username": user.full_name},
    )


@router.get("/client/approve_switch_requests", response_class=HTMLResponse)
async def client_approve_switch_requests(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user = await get_current_client_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "/client_user/client_approve_switch.html",
        {"request": request, "username": user.full_name},
    )
