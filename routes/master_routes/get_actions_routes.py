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
