import logging
from bson import ObjectId

from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from utils.mongo_db import MongoDB
from utils.dependecy_functions import get_mongo_db
from utils.pydantic_forms import (
    NewSigningAccessForm,
    SwitchSigningAccessForm,
    NewSigningData,
    User,
    AddSigningData,
    PendingSigningObjectId,
    RemoveSigningData,
    SwitchSigningData, 
    ClientSwitchSigningAccessForm
)
from utils.helpers import (
    get_current_client_user,
    create_new_signing_document,
    create_new_signing_log_document,
    create_credit_log_document,
    create_switch_log_document
)


logger = logging.getLogger(__name__)

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.post("/client/verify-switch-signing-access")
async def switch_access(
    request: Request,
    access_data: ClientSwitchSigningAccessForm,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
    logger.info("in verify switch signing")
    try:
        user = await get_current_client_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    session = request.session
    new_personal_id = int(access_data.new_personal_id)
    client_password = access_data.client_password

    if not await mongo_db.is_existing_client(new_personal_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A client with the given personal id doesn't exist: {new_personal_id}",
        )
    

    if client_password != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"The given password is incorrect",
        )
    
    session["client_switch_new_personal_id"] = new_personal_id

    return {"redirect_url": "/client/switch_signing"}

@router.post("/client/switch_signing")
async def client_switch_signings(
    request: Request, switch_signing_data: SwitchSigningData, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user: User = await get_current_client_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    session = request.session
    old_personal_id = user.personal_id
    new_personal_id = session.get("client_switch_new_personal_id", None)

    if new_personal_id is None:
        raise ValueError("can't detect new signer personal id")
    
    switch_selected_items = switch_signing_data.selected_items
    switch_signing_description = switch_signing_data.signing_descrition
    print("catch 2")
    for switch_signing_item in switch_selected_items:
        signing_id = ObjectId(switch_signing_item.signing_id)
        quantity = int(switch_signing_item.quantity)
        # signing_item = await mongo_db.get_signing_item_by_object_id(signing_id)
        # inventory_item_id = signing_item.get("item_id")
        switch_request_document = {
            "signing_id": signing_id,
            "old_pid": old_personal_id,
            "new_pid": new_personal_id,
            "quantity": quantity,
            "description": switch_signing_description,
            "status": 1
        }
        await mongo_db.add_item_to_switch_requests(switch_request_document)
        # print("catch 3")
        # switch_log_document = await create_switch_log_document(
        #     mongo_db, user.personal_id, old_personal_id, new_personal_id, inventory_item_id, quantity
        # )
        # await mongo_db.switch_signing(signing_id, quantity, new_personal_id, user.personal_id, switch_signing_description)
        # await mongo_db.add_item_to_logs(switch_log_document)

    return {"redirect_url": "/client/signings"}