import logging
from bson import ObjectId
from datetime import datetime

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
    RejectSwitchRequestData,
    ApproveSwitchRequestData,
    ClientUserObjectId,
    ClientUser,
    InventoryCollectionItemUpdates,
    InventoryDelteItem,
    InventoryAddItem,
    NewKitLock,
    NewKitItems,
    KitContent,
    RemoveKitItemData,
    ExistingKitAddItems,
    AddAmplifierTracking,
    UpdateAmplifierResults,
    UpdateAmplifierInterval,
    DeleteAmplifierTracking,
)
from utils.helpers import (
    get_current_master_user,
    create_new_signing_document,
    create_new_signing_log_document,
    create_credit_log_document,
    create_switch_log_document,
    create_delete_item_log_document,
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
async def add_items_to_pending_signings(
    request: Request,
    new_signing_data: NewSigningData,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
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
        await mongo_db.inventory_decrease_count_by_quantity(
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
    pending_signing = await mongo_db.get_pending_signing_by_object_id(object_id)
    await mongo_db.inventory_increase_count_quantity(
        pending_signing.get("item_id"), pending_signing.get("quantity")
    )
    await mongo_db.delete_pending_signing_by_object_id(object_id)

    return {"redirect_url": "/master/pending_signings"}


@router.post("/master/add_items_to_signings")
async def add_items_to_signings(
    new_signing_data: AddSigningData, mongo_db: MongoDB = Depends(get_mongo_db)
):
    selected_pending_items = new_signing_data.selected_items

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

    return {"redirect_url": "/master/signings"}


@router.post("/master/remove_signing")
async def remove_signings(
    request: Request,
    reove_signing_data: RemoveSigningData,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
    try:
        user: User = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    for remove_signing_item in reove_signing_data.selected_items:
        signing_id = ObjectId(remove_signing_item.signing_id)
        quantity = int(remove_signing_item.quantity)
        signing_item = await mongo_db.get_signing_item_by_object_id(signing_id)
        inventory_item_id = signing_item.get("item_id")
        credit_log_document = await create_credit_log_document(
            mongo_db,
            user.personal_id,
            signing_item.get("client_personal_id"),
            inventory_item_id,
            quantity,
        )
        await mongo_db.remove_signing(signing_id, quantity)
        await mongo_db.inventory_increase_count_quantity(inventory_item_id, quantity)
        await mongo_db.add_item_to_logs(credit_log_document)

    return {"redirect_url": "/master/remove_signing"}


@router.post("/master/verify-switch-signing-access")
async def switch_signing_access(
    request: Request,
    access_data: SwitchSigningAccessForm,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
    logger.info("in verify switch signing")
    try:
        user = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    session = request.session
    old_personal_id = int(access_data.old_personal_id)
    new_personal_id = int(access_data.new_personal_id)
    master_password = access_data.master_password

    if not await mongo_db.is_existing_client(old_personal_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A client with the given personal id doesn't exist: {old_personal_id}",
        )

    if not await mongo_db.is_existing_client(new_personal_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A client with the given personal id doesn't exist: {new_personal_id}",
        )

    if master_password != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"The given master password is incorrect",
        )

    session["switch_old_personal_id"] = old_personal_id
    session["switch_new_personal_id"] = new_personal_id

    return {"redirect_url": "/master/switch_signing"}


@router.post("/master/switch_signing")
async def switch_signing(
    request: Request,
    switch_signing_data: SwitchSigningData,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
    try:
        user: User = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    session = request.session
    old_personal_id = session.get("switch_old_personal_id", None)
    new_personal_id = session.get("switch_new_personal_id", None)
    if old_personal_id is None:
        raise ValueError("can't detect old signer personal id")

    if new_personal_id is None:
        raise ValueError("can't detect new signer personal id")

    switch_selected_items = switch_signing_data.selected_items
    switch_signing_description = switch_signing_data.signing_descrition

    for switch_signing_item in switch_selected_items:
        signing_id = ObjectId(switch_signing_item.signing_id)
        quantity = int(switch_signing_item.quantity)
        signing_item = await mongo_db.get_signing_item_by_object_id(signing_id)
        inventory_item_id = signing_item.get("item_id")
        switch_log_document = await create_switch_log_document(
            mongo_db,
            user.personal_id,
            old_personal_id,
            new_personal_id,
            inventory_item_id,
            quantity,
        )
        await mongo_db.switch_signing(
            signing_id,
            quantity,
            new_personal_id,
            user.personal_id,
            switch_signing_description,
        )
        await mongo_db.add_item_to_logs(switch_log_document)

    return {"redirect_url": "/master/signings"}


@router.post("/master/reject_switch_rquest")
async def reject_switch_rquest(
    rejected_rquests_object: RejectSwitchRequestData,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
    rejected_requests = rejected_rquests_object.selected_requests

    for rejected_request in rejected_requests:
        switch_request_id = ObjectId(rejected_request.switch_request_id)
        await mongo_db.reject_switch_request_by_id(switch_request_id)

    return {"redirect_url": "/master/approve_switch_requests"}


@router.post("/master/approve_switch_rquest")
async def approve_switch_rquest(
    request: Request,
    approved_rquests_object: ApproveSwitchRequestData,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
    try:
        user: User = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    approved_requests = approved_rquests_object.selected_requests

    for approved_request in approved_requests:
        switch_request_id = ObjectId(approved_request.switch_request_id)
        request_item = await mongo_db.get_switch_request_by_id(switch_request_id)
        request_quantity = request_item.get("quantity")
        signing_id = request_item.get("signing_id")
        signing_item = await mongo_db.get_signing_item_by_object_id(signing_id)
        inventory_item_id = signing_item.get("item_id")
        if signing_item is None or signing_item.get(
            "client_personal_id"
        ) != request_item.get("old_pid"):
            await mongo_db.reject_status_switch_request_by_id(switch_request_id)
            return {"redirect_url": "/master/approve_switch_requests"}

        if not request_quantity <= signing_item.get("quantity"):
            await mongo_db.reject_status_switch_request_by_id(switch_request_id)
            return {"redirect_url": "/master/approve_switch_requests"}

        switch_log_document = await create_switch_log_document(
            mongo_db,
            user.personal_id,
            request_item.get("old_pid"),
            request_item.get("new_pid"),
            inventory_item_id,
            request_quantity,
        )
        await mongo_db.switch_signing(
            signing_id,
            request_quantity,
            request_item.get("new_pid"),
            user.personal_id,
            request_item.get("description"),
        )
        await mongo_db.add_item_to_logs(switch_log_document)
        await mongo_db.delete_switch_request_by_id(switch_request_id)

    return {"redirect_url": "/master/approve_switch_requests"}


@router.post("/master/delete_client_user")
async def delete_client_user(
    deleted_object: ClientUserObjectId, mongo_db: MongoDB = Depends(get_mongo_db)
):
    user_id = ObjectId(deleted_object.user_id)
    cliet_user: ClientUser = await mongo_db.get_client_by_object_id(user_id)
    client_personal_id = cliet_user.personal_id

    involved_signings = await mongo_db.involved_signing_by_personal_id(
        client_personal_id
    )

    if involved_signings:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"This user can't be deleted. it has open signings",
        )

    involved_pending_signings = await mongo_db.get_pending_signing_by_client_pid(
        client_personal_id
    )
    if involved_pending_signings:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"This user can't be deleted. it has open pending signings",
        )

    involved_in_switch_requests = await mongo_db.involved_in_switch_requests(
        client_personal_id
    )
    if involved_in_switch_requests:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"This user can't be deleted. it has open switch requests",
        )

    await mongo_db.delete_client_user(user_id)

    return {"redirect_url": "/master/update_users"}


@router.post("/master/update_inventory")
async def update_inventory(
    inventory_edit_object: InventoryCollectionItemUpdates,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
    item_id = ObjectId(inventory_edit_object.item_id)
    total_count = inventory_edit_object.total_count

    inventory_item = await mongo_db.get_inventory_item_by_object_id(item_id)
    current_total_count = inventory_item.get("total_count")
    current_count = inventory_item.get("count")
    if total_count >= current_total_count:
        new_count = current_count + (total_count - current_total_count)
    else:
        if current_count == current_total_count:
            new_count = total_count
        elif current_count > total_count:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"total count can't be smaller than available items count",
            )
        else:
            new_count = current_count

    await mongo_db.edit_inventory_item_by_id(item_id, inventory_edit_object, new_count)

    return {"redirect_url": "/master/update_inventory"}


@router.post("/master/delete_item_from_inventory")
async def delete_item_from_inventory(
    request: Request,
    delete_object: InventoryDelteItem,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
    try:
        user: User = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    item_id = ObjectId(delete_object.item_id)

    #check here if total count equall to current count
    item_object = await mongo_db.get_inventory_item_by_object_id(item_id)
    involved_singings = await mongo_db.get_involved_item_in_signings(item_id)
    involved_pending_singings = await mongo_db.get_involved_item_in_pending_signings(
        item_id
    )

    if involved_singings:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"This item can't be deleted. it has open signings",
        )

    if involved_pending_singings:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"This item can't be deleted. it has open pending signings",
        )
    
    if item_object.get("count") != item_object.get("total_count"):
        logger.info(f"{item_id} can't be deleted becuse not all items are available")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"This item can't be deleted. not all items are available",
        )

    log_document = await create_delete_item_log_document(
        mongo_db, item_id, user.personal_id
    )
    logger.info(f"log documrnt: {log_document ,type(log_document)}")
    await mongo_db.delete_item_from_inventory(item_id)
    await mongo_db.add_item_to_logs(log_document)

    return {"redirect_url": "/master/update_inventory"}


@router.post("/master/add_item_to_inventory")
async def add_item_to_inventory(
    item_object: InventoryAddItem, mongo_db: MongoDB = Depends(get_mongo_db)
):
    item_dict = {
        "name": item_object.name,
        "category": item_object.category,
        "count": item_object.total_count,
        "total_count": item_object.total_count,
        "color": item_object.color,
        "palga": item_object.palga,
        "mami_serial": item_object.mami_serial,
        "manufacture_mkt": item_object.manufacture_mkt,
        "katzi_mkt": item_object.katzi_mkt,
        "serial_no": item_object.serial_no,
        "description": item_object.description,
    }

    await mongo_db.add_item_to_inventory(item_dict)

    return {"redirect_url": "/master/update_inventory"}


@router.post("/master/new_kit")
async def new_kit(
    request: Request, kit_data: NewKitLock, mongo_db: MongoDB = Depends(get_mongo_db)
):
    kit_name = kit_data.kit_name
    kit_palga = kit_data.palga
    exist_kit_name = await mongo_db.involved_kit_by_name(kit_name)
    if exist_kit_name:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"This kit name is already taken. choose different one.",
        )

    session = request.session
    session["new_kit_name"] = kit_name
    session["new_kit_palga"] = kit_palga

    return {"redirect_url": "/master/new_kit_items"}


@router.post("/master/add_items_to_kit")
async def add_items_to_kit(
    request: Request,
    new_kit_data: NewKitItems,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
    try:
        user: User = await get_current_master_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    session = request.session
    kit_name = session.get("new_kit_name", None)
    kit_palga = session.get("new_kit_palga", None)

    kit_id = await mongo_db.insert_new_kit({"name": kit_name})

    selected_kit_items = new_kit_data.selected_items
    kit_description = new_kit_data.kit_descrition

    for selected_item in selected_kit_items:
        item_id = ObjectId(selected_item.item_id)
        item_quantity = int(selected_item.quantity)
        item = await mongo_db.get_inventory_item_by_object_id(item_id)
        if item.get("kit_id"):
            print("has kit id", item.get("kit_id"))
            continue

        await mongo_db.inventory_decrease_count_by_quantity(item_id, item_quantity)

        kit_item = {"kit_id": kit_id, "item_id": item_id, "quantity": item_quantity}
        await mongo_db.add_doc_to_kits_items(kit_item)

    item_dict = {
        "name": kit_name,
        "category": "kit",
        "count": 1,
        "total_count": 1,
        "color": "",
        "palga": kit_palga,
        "mami_serial": "",
        "manufacture_mkt": "",
        "katzi_mkt": "",
        "serial_no": "",
        "description": kit_description,
        "kit_id": kit_id,
    }

    await mongo_db.add_item_to_inventory(item_dict)

    return {"redirect_url": "/master/kits"}


@router.post("/master/kit_content")
async def kit_content(kit_data: KitContent):
    redirect_url = f"/master/kit_content/{kit_data.kit_id}"

    return {"redirect_url": redirect_url}


@router.post("/master/kit_remove_items")
async def kit_remove_items(kit_data: KitContent):
    redirect_url = f"/master/kit_remove_items/{kit_data.kit_id}"

    return {"redirect_url": redirect_url}


@router.post("/master/kit_add_items")
async def kit_add_items(kit_data: KitContent):
    redirect_url = f"/master/kit_add_items/{kit_data.kit_id}"

    return {"redirect_url": redirect_url}


@router.post("/master/remove_kit_item")
async def remove_kit_item(
    remove_data: RemoveKitItemData, mongo_db: MongoDB = Depends(get_mongo_db)
):
    for remove_kit_item in remove_data.selected_items:
        kit_item_id = ObjectId(remove_kit_item.kit_item_id)
        quantity = int(remove_kit_item.quantity)
        kit_item_object = await mongo_db.get_kit_item_object_by_id(kit_item_id)
        inventory_item_id = kit_item_object.get("item_id")

        await mongo_db.remove_kit_item(kit_item_id, quantity)
        await mongo_db.inventory_increase_count_quantity(inventory_item_id, quantity)


@router.post("/master/add_items_to_existing_kit")
async def add_items_to_kit(
    existing_kit_data: ExistingKitAddItems,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
    kit_id = ObjectId(existing_kit_data.kit_id)

    selected_kit_items = existing_kit_data.selected_items

    for selected_item in selected_kit_items:
        item_id = ObjectId(selected_item.item_id)
        item_quantity = int(selected_item.quantity)
        item = await mongo_db.get_inventory_item_by_object_id(item_id)
        if item.get("kit_id"):
            continue

        await mongo_db.inventory_decrease_count_by_quantity(item_id, item_quantity)

        kit_item = {"kit_id": kit_id, "item_id": item_id, "quantity": item_quantity}
        await mongo_db.add_doc_to_kits_items(kit_item)

    redirect_url = f"/master/kit_content/{kit_id}"

    return {"redirect_url": redirect_url}


@router.post("/master/delete_kit")
async def delete_kit(kit_data: KitContent, mongo_db: MongoDB = Depends(get_mongo_db)):
    kit_id = ObjectId(kit_data.kit_id)

    involved_kit_items = await mongo_db.involved_kit_items(kit_id)
    if involved_kit_items:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"This kit has items assigned to it, can't be deleted.",
        )
    await mongo_db.delete_kit(kit_id)
    await mongo_db.delete_kit_from_inventory(kit_id)

    return {"redirect_url": "/master/kits"}


@router.post("/master/add_amplifier_tracking")
async def add_amplifier_tracking(
    amplifier_data: AddAmplifierTracking,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
    item_id = ObjectId(amplifier_data.item_id)
    amplifier_document = {
        "item_id": item_id,
        "test_type": (amplifier_data.test_type).strip().upper(),
        "days_interval": amplifier_data.days_interval,
        "last_updated": datetime.utcnow(),
        "results": "Hasn't been checked yet",
    }
    try:
        await mongo_db.add_doc_to_amplifier_tracking(amplifier_document)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    return {"redirect_url": "/master/amplifier_status"}


@router.post("/master/update_amplifier_results")
async def update_amplifier_results(
    amplifier_data: UpdateAmplifierResults,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
    await mongo_db.update_amplifier_results(
        ObjectId(amplifier_data.object_id), amplifier_data.results
    )

    return {"redirect_url": "/master/amplifier_status"}


@router.post("/master/update_amplifier_interval")
async def update_amplifier_interval(
    amplifier_data: UpdateAmplifierInterval,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
    await mongo_db.update_amplifier_interval(
        ObjectId(amplifier_data.object_id), amplifier_data.interval
    )

    return {"redirect_url": "/master/amplifier_status"}


@router.post("/master/delete_amplifier_tracking")
async def delete_amplifier_tracking(
    amplifier_data: DeleteAmplifierTracking,
    mongo_db: MongoDB = Depends(get_mongo_db),
):
    await mongo_db.delete_amplifier_tracking(ObjectId(amplifier_data.object_id))

    return {"redirect_url": "/master/amplifier_status"}
