import logging
from bson import ObjectId

from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from utils.mongo_db import MongoDB
from utils.dependecy_functions import get_mongo_db
from utils.pydantic_forms import (
    NewSigningAccessForm,
    NewSigningData,
    User,
    AddSigningData,
    PendingSigningObjectId,
)
from utils.helpers import (
    get_current_master_user,
    create_new_signing_document,
    create_new_signing_log_document,
)


logger = logging.getLogger(__name__)

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.post("/master/verify-new-signing-access")
async def new_signing_access(
    request: Request,
    access_data: NewSigningAccessForm,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
    logger.info("in verify")
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    session = request.session
    client_personal_id = access_data.signer_personal_id
    master_password = access_data.master_password

    if not await mongo_db.is_existing_client(client_personal_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A client with the given personal id doesn't exist: {client_personal_id}",
        )

    if master_password != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"The given master password is incorrect",
        )

    session["signer_personal_id"] = client_personal_id

    return {"redirect_url": "/master/new_signing"}


@router.post("/master/add_items_to_pending_signings")
async def new_signing_access(
    request: Request,
    new_signing_data: NewSigningData,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
    logger.info(f"this is selected items: {new_signing_data}")
    try:
        user: User = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    session = request.session
    client_personal_id = session.get("signer_personal_id", None)
    if client_personal_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"unrecognized signer pesonal id",
        )

    selected_signing_items = new_signing_data.selected_items
    signing_description = new_signing_data.signing_descrition

    for signing_item in selected_signing_items:
        item_object_id = ObjectId(signing_item.item_id)
        signing_quantity = int(signing_item.quantity)
        await mongo_db.inventory_decrease_count_by_signing_info(
            item_object_id, signing_quantity
        )
        new_pending_signing = {
            "item_id": item_object_id,
            "master_personal_id": user.personal_id,
            "client_personal_id": client_personal_id,
            "quantity": signing_quantity,
            "description": signing_description,
        }
        await mongo_db.add_item_to_pending_signings(new_pending_signing)

    return {"redirect_url": "/master/pending_signings"}


@router.post("/master/delete_item_from_pending_signings")
async def delete_item_from_pending_signings(
    deleted_object: PendingSigningObjectId, mongo_db: MongoDB = Depends(get_mongo_db)
):
    object_id = ObjectId(deleted_object.pending_signing_id)
    logger.info(f"in delete pen sign: {object_id}")
    pending_signing = await mongo_db.get_pending_signing_by_object_id(object_id)
    await mongo_db.inventory_increase_count_by_signing_info(
        pending_signing.get("item_id"), pending_signing.get("quantity")
    )
    await mongo_db.delete_pending_signing_by_object_id(object_id)
    print("sending redirection pending")

    return {"redirect_url": "/master/pending_signings"}


@router.post("/master/add_items_to_signings")
async def new_signing_access(
    new_signing_data: AddSigningData, mongo_db: MongoDB = Depends(get_mongo_db)
):
    selected_pending_items = new_signing_data.selected_items
    logger.info(f"selected add to signing: {selected_pending_items}")
    for pending_signing_item in selected_pending_items:
        pending_signing_object_id = ObjectId(pending_signing_item.pending_signing_id)
        pending_signing = await mongo_db.get_pending_signing_by_object_id(
            pending_signing_object_id
        )
        master_personal_id = pending_signing.get("master_personal_id")
        client_personal_id = pending_signing.get("client_personal_id")
        item_id = pending_signing.get("item_id")
        quantity = pending_signing.get("quantity")
        description = pending_signing.get("description")

        new_signing_document = create_new_signing_document(
            item_id, master_personal_id, client_personal_id, quantity, description
        )
        log_document = await create_new_signing_log_document(
            mongo_db, master_personal_id, client_personal_id, item_id, quantity
        )
        await mongo_db.add_item_to_signings(new_signing_document)
        await mongo_db.delete_pending_signing_by_object_id(pending_signing_object_id)
        await mongo_db.add_item_to_logs(log_document)
    print(" sending redirection signings")

    return {"redirect_url": "/master/signings"}
