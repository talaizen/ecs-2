import logging
from bson import ObjectId

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
        {"request": request, "username": user.full_name}
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
        {"request": request, "username": user.full_name}
    )

@router.get("/master/kits", response_class=HTMLResponse)
async def kits(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse(
        "/master_user/master_kits.html",
        {"request": request, "username": user.full_name}
    )

@router.get("/master/new_kit", response_class=HTMLResponse)
async def kits(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse(
        "/master_user/master_kit_lock.html",
        {"request": request, "username": user.full_name}
    )

@router.get("/master/new_kit_items", response_class=HTMLResponse)
async def new_kit_items(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    session = request.session
    kit_name = session.get("new_kit_name", None)
    print("this is kit name", kit_name)
    
    return templates.TemplateResponse(
        "/master_user/master_new_kit_items.html",
        {"request": request, "username": user.full_name, "kit_name": kit_name}
    )

@router.get("/master/kit_content/{kit_id}", response_class=HTMLResponse)
async def kit_content(
    kit_id: str, request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    kit_object_id = ObjectId(kit_id)
    kit_object = await mongo_db.get_kit_by_id(kit_object_id)
    kit_description = await mongo_db.get_kit_description_from_inventory(kit_object_id)
    
    return templates.TemplateResponse(
        "/master_user/master_kit_content.html",
        {"request": request, "username": user.full_name, "kit_name": kit_object.get("name"), "kit_id": kit_id, "kit_description": kit_description}
    )
    
@router.get("/master/kit_remove_items/{kit_id}", response_class=HTMLResponse)
async def kit_content(
    kit_id: str, request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    kit_object_id = ObjectId(kit_id)
    kit_object = await mongo_db.get_kit_by_id(kit_object_id)
    kit_description = await mongo_db.get_kit_description_from_inventory(kit_object_id)
    
    return templates.TemplateResponse(
        "/master_user/master_kit_remove_items.html",
        {"request": request, "username": user.full_name, "kit_name": kit_object.get("name"), "kit_id": kit_id, "kit_description": kit_description}
    )

@router.get("/master/kit_add_items/{kit_id}", response_class=HTMLResponse)
async def kit_content(
    kit_id: str, request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    kit_object_id = ObjectId(kit_id)
    kit_object = await mongo_db.get_kit_by_id(kit_object_id)
    kit_description = await mongo_db.get_kit_description_from_inventory(kit_object_id)
    
    return templates.TemplateResponse(
        "/master_user/master_kit_add_items.html",
        {"request": request, "username": user.full_name, "kit_name": kit_object.get("name"), "kit_id": kit_id, "kit_description": kit_description}
    )

@router.get("/master/amplifier_selection", response_class=HTMLResponse)
async def amplifier_selection(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse(
        "/master_user/master_amplifier_selection.html",
        {"request": request, "username": user.full_name}
    )

@router.get("/master/amplifier_status", response_class=HTMLResponse)
async def amplifier_status(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse(
        "/master_user/master_amplifier_status.html",
        {"request": request, "username": user.full_name}
    )