import logging
from bson import ObjectId

from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from utils.mongo_db import MongoDB
from utils.dependecy_functions import get_mongo_db
from utils.pydantic_forms import (
    User,
    SwitchSigningData, 
    ClientSwitchSigningAccessForm,
    CanceledSwitchRequest,
    ApproveSwitchRequestData,
    RejectSwitchRequestData,
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
    return {"redirect_url": "/client/switch_requests"}

@router.post("/client/cancel_switch_request")
async def delete_item_from_pending_signings(
    canceled_request: CanceledSwitchRequest, mongo_db: MongoDB = Depends(get_mongo_db)
):
    object_id = ObjectId(canceled_request.canceled_request_id)
    await mongo_db.delete_switch_request_by_id(object_id)

    return {"redirect_url": "/client/switch_requests"}

@router.post("/client/approve_switch_rquest")
async def approve_switch_rquest(
    approved_rquests_object: ApproveSwitchRequestData, mongo_db: MongoDB = Depends(get_mongo_db)
):
    approved_requests = approved_rquests_object.selected_requests
    for approved_request in approved_requests:
        switch_request_id = ObjectId(approved_request.switch_request_id)
        await mongo_db.approve_switch_request_by_id(switch_request_id)
    
    return {"redirect_url": "/client/approve_switch_requests"}

@router.post("/client/reject_switch_rquest")
async def reject_switch_rquest(
    rejected_rquests_object: RejectSwitchRequestData, mongo_db: MongoDB = Depends(get_mongo_db)
):
    rejected_requests = rejected_rquests_object.selected_requests
    for rejected_request in rejected_requests:
        switch_request_id = ObjectId(rejected_request.switch_request_id)
        await mongo_db.reject_switch_request_by_id(switch_request_id)
    
    return {"redirect_url": "/client/approve_switch_requests"}
