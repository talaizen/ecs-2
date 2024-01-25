import logging
from bson import ObjectId

from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from utils.mongo_db import MongoDB
from utils.dependecy_functions import get_mongo_db
from utils.helpers import generate_user_presentation, get_current_client_user
from utils.pydantic_forms import (
    User,
    ClientUser,
    MasterUser,
    SigningsCollectionItem,
    SigningItem,
    SwitchRequestItem,
)

logger = logging.getLogger(__name__)

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/collections-data/client_signings")
async def get_client_signings_data(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user: User = await get_current_client_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    data = []
    async for document in await mongo_db.get_signings_data_by_personal_id(
        user.personal_id
    ):
        item_info = await mongo_db.get_inventory_item_by_object_id(
            document.get("item_id")
        )
        signer: ClientUser = await mongo_db.get_client_by_personal_id(
            document.get("client_personal_id")
        )
        issuer: MasterUser = await mongo_db.get_master_by_personal_id(
            document.get("master_personal_id")
        )
        date = document.get("date").strftime("%Y-%m-%d %H:%M")

        data.append(
            SigningsCollectionItem(
                name=item_info.get("name"),
                category=item_info.get("category"),
                quantity=document.get("quantity"),
                color=item_info.get("color"),
                palga=item_info.get("palga"),
                mami_serial=item_info.get("mami_serial"),
                manufacture_mkt=item_info.get("manufacture_mkt"),
                katzi_mkt=item_info.get("katzi_mkt"),
                serial_no=item_info.get("serial_no"),
                item_description=item_info.get("description"),
                signer=generate_user_presentation(signer),
                issuer=generate_user_presentation(issuer),
                signing_description=document.get("description"),
                date=date,
            )
        )
    return data


@router.get("/collections-data/client_switch_signing")
async def get_switch_signing_data(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user: User = await get_current_client_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    data = []
    client_old_personal_id = user.personal_id

    async for document in await mongo_db.get_signings_data_by_personal_id(
        client_old_personal_id
    ):
        item_info = await mongo_db.get_inventory_item_by_object_id(
            document.get("item_id")
        )
        signer: ClientUser = await mongo_db.get_client_by_personal_id(
            document.get("client_personal_id")
        )
        issuer: MasterUser = await mongo_db.get_master_by_personal_id(
            document.get("master_personal_id")
        )
        date = document.get("date").strftime("%Y-%m-%d %H:%M")
        data.append(
            SigningItem(
                signing_id=str(document.get("_id")),
                name=item_info.get("name"),
                category=item_info.get("category"),
                quantity=document.get("quantity"),
                color=item_info.get("color"),
                palga=item_info.get("palga"),
                mami_serial=item_info.get("mami_serial"),
                manufacture_mkt=item_info.get("manufacture_mkt"),
                katzi_mkt=item_info.get("katzi_mkt"),
                serial_no=item_info.get("serial_no"),
                item_description=item_info.get("description"),
                signer=generate_user_presentation(signer),
                issuer=generate_user_presentation(issuer),
                signing_description=document.get("description"),
                date=date,
            )
        )
    return data


@router.get("/collections-data/client_switch_requests")
async def get_switch_requests(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user: User = await get_current_client_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    data = []
    status_mapping = {1: "signer approval required", 2: "sent to Mami approval"}

    async for document in await mongo_db.get_switch_requests_by_old_signer_pid(
        user.personal_id
    ):
        signing_info = await mongo_db.get_signing_item_by_object_id(
            document.get("signing_id")
        )
        if not signing_info:
            logger.info(f"deleting swith request with the following id due to signing credit: {document.get("_id")}")
            await mongo_db.delete_switch_request_by_id(ObjectId(document.get("_id")))
            continue

        item_info = await mongo_db.get_inventory_item_by_object_id(
            signing_info.get("item_id")
        )
        signer: ClientUser = await mongo_db.get_client_by_personal_id(
            signing_info.get("client_personal_id")
        )
        new_signer: ClientUser = await mongo_db.get_client_by_personal_id(
            document.get("new_pid")
        )
        switch_description = document.get("description")
        switch_status = status_mapping.get(document.get("status"))
        switch_quantity = document.get("quantity")
        data.append(
            SwitchRequestItem(
                request_id=str(document.get("_id")),
                name=item_info.get("name"),
                category=item_info.get("category"),
                quantity=switch_quantity,
                color=item_info.get("color"),
                palga=item_info.get("palga"),
                mami_serial=item_info.get("mami_serial"),
                manufacture_mkt=item_info.get("manufacture_mkt"),
                katzi_mkt=item_info.get("katzi_mkt"),
                serial_no=item_info.get("serial_no"),
                item_description=item_info.get("description"),
                signer=generate_user_presentation(signer),
                signing_description=signing_info.get("description"),
                new_signer=generate_user_presentation(new_signer),
                switch_description=switch_description,
                status=switch_status,
            )
        )
    return data


@router.get("/collections-data/client_approve_switch_requests")
async def get_approve_switch_requests(
    request: Request, mongo_db: MongoDB = Depends(get_mongo_db)
):
    try:
        user: User = await get_current_client_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    data = []
    status_mapping = {1: "your approval required", 2: "sent to Mami approval"}

    async for document in await mongo_db.get_switch_requests_by_new_signer_pid(
        user.personal_id
    ):
        signing_info = await mongo_db.get_signing_item_by_object_id(
            document.get("signing_id")
        )
        if not signing_info:
            logger.info(f"deleting swith request with the following id due to signing credit: {document.get("_id")}")
            await mongo_db.delete_switch_request_by_id(ObjectId(document.get("_id")))
            continue

        item_info = await mongo_db.get_inventory_item_by_object_id(
            signing_info.get("item_id")
        )
        signer: ClientUser = await mongo_db.get_client_by_personal_id(
            signing_info.get("client_personal_id")
        )
        new_signer: ClientUser = await mongo_db.get_client_by_personal_id(
            document.get("new_pid")
        )
        switch_description = document.get("description")
        switch_status = status_mapping.get(document.get("status"))
        switch_quantity = document.get("quantity")
        data.append(
            SwitchRequestItem(
                request_id=str(document.get("_id")),
                name=item_info.get("name"),
                category=item_info.get("category"),
                quantity=switch_quantity,
                color=item_info.get("color"),
                palga=item_info.get("palga"),
                mami_serial=item_info.get("mami_serial"),
                manufacture_mkt=item_info.get("manufacture_mkt"),
                katzi_mkt=item_info.get("katzi_mkt"),
                serial_no=item_info.get("serial_no"),
                item_description=item_info.get("description"),
                signer=generate_user_presentation(signer),
                signing_description=signing_info.get("description"),
                new_signer=generate_user_presentation(new_signer),
                switch_description=switch_description,
                status=switch_status,
            )
        )
    return data
