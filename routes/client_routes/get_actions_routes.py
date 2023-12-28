import logging

from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

from utils.mongo_db import MongoDB
from utils.dependecy_functions import get_mongo_db
from utils.pydantic_forms import ClientUser, User
from utils.helpers import get_current_client_user


logger = logging.getLogger(__name__)

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/client/verify-switch-signing-access")
async def client_switch_signing_verification(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user: User = await get_current_client_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "/client_user/switch_signing_lock.html",
        {"request": request, "username": user.full_name},
    )

@router.get("/client/switch_signing", response_class=HTMLResponse)
async def client_switch_signing(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user: User = await get_current_client_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    session = request.session
    new_personal_id = session.get("client_switch_new_personal_id", None)

    old_signer: ClientUser = await mongo_db.get_client_by_personal_id(
        user.personal_id
    )

    new_signer: ClientUser = await mongo_db.get_client_by_personal_id(
        new_personal_id
    )

    if old_signer is None or new_signer is None:
        return RedirectResponse(
            url="/client/verify-switch-signing-access", status_code=status.HTTP_302_FOUND
        )

    return templates.TemplateResponse(
        "/client_user/client_switch_signing.html",
        {"request": request, "username": user.full_name, "old_signer": old_signer, "new_signer": new_signer},
    )