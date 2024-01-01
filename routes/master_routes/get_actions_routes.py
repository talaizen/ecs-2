import logging

from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

from utils.mongo_db import MongoDB
from utils.dependecy_functions import get_mongo_db
from utils.pydantic_forms import ClientUser
from utils.helpers import get_current_master_user


logger = logging.getLogger(__name__)

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/master/new_signing", response_class=HTMLResponse)
async def master_new_signing(
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

    session = request.session
    current_signer_personal_id = session.get("signer_personal_id", None)
    current_signer: ClientUser = await mongo_db.get_client_by_personal_id(
        current_signer_personal_id
    )

    if current_signer is None:
        return RedirectResponse(
            url="/master/verify-new-signing-access", status_code=status.HTTP_302_FOUND
        )

    return templates.TemplateResponse(
        "/master_user/master_new_signing.html",
        {"request": request, "username": user.full_name, "signer": current_signer},
    )


@router.get("/master/verify-new-signing-access")
async def get_new_signing_verification(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "/master_user/new_signing_lock.html",
        {"request": request, "username": user.full_name},
    )

@router.get("/master/remove_signing", response_class=HTMLResponse)
async def remove_signing(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse(
        "/master_user/master_remove_signing.html",
        {"request": request, "username": user.full_name},
    )

@router.get("/master/verify-switch-signing-access")
async def get_switch_signing_verification(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "/master_user/switch_signing_lock.html",
        {"request": request, "username": user.full_name},
    )

@router.get("/master/switch_signing", response_class=HTMLResponse)
async def master_switch_signing(
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

    session = request.session
    old_personal_id = session.get("switch_old_personal_id", None)
    new_personal_id = session.get("switch_new_personal_id", None)

    old_signer: ClientUser = await mongo_db.get_client_by_personal_id(
        old_personal_id
    )

    new_signer: ClientUser = await mongo_db.get_client_by_personal_id(
        new_personal_id
    )

    if old_signer is None or new_signer is None:
        return RedirectResponse(
            url="/master/verify-switch-signing-access", status_code=status.HTTP_302_FOUND
        )

    return templates.TemplateResponse(
        "/master_user/master_switch_signing.html",
        {"request": request, "username": user.full_name, "old_signer": old_signer, "new_signer": new_signer},
    )

@router.get("/master/update_users", response_class=HTMLResponse)
async def update_users(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse(
        "/master_user/master_update_users.html",
        {"request": request, "username": user.full_name},
    )

@router.get("/master/update_inventory", response_class=HTMLResponse)
async def update_users(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse(
        "/master_user/master_update_inventory.html",
        {"request": request, "username": user.full_name},
    )