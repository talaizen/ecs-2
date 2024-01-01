import logging

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from utils.mongo_db import MongoDB
from utils.dependecy_functions import get_mongo_db
from utils.helpers import generate_user_presentation
from utils.pydantic_forms import (
    LogCollectionItem,
    ClientUser,
    MasterUser,
    SigningsCollectionItem,
    PendingSigningsCollectionItem,
    ClientUserCollectionItem,
    InventoryCollectionItem,
    SigningItem,
    SwitchRequestItem,
    UpdateClientUserCollectionItem
)


logger = logging.getLogger(__name__)

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/collections-data/logs")
async def get_logs(mongo_db: MongoDB = Depends(get_mongo_db)):
    data = []
    async for document in await mongo_db.get_logs_data():
        data.append(
            LogCollectionItem(
                action=document.get("action"),
                description=document.get("description"),
                date=document.get("date").strftime("%Y-%m-%d %H:%M"),
            )
        )
    return data


@router.get("/collections-data/signings")
async def get_signings_data(mongo_db: MongoDB = Depends(get_mongo_db)):
    data = []
    async for document in await mongo_db.get_signings_data():
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


@router.get("/collections-data/pending_signings")
async def get_inventory_data(mongo_db: MongoDB = Depends(get_mongo_db)):
    data = []
    async for document in await mongo_db.get_pending_signings_data():
        item_info = await mongo_db.get_inventory_item_by_object_id(
            document.get("item_id")
        )
        signer: ClientUser = await mongo_db.get_client_by_personal_id(
            document.get("client_personal_id")
        )
        issuer: MasterUser = await mongo_db.get_master_by_personal_id(
            document.get("master_personal_id")
        )
        print(f"this is item info {item_info}")
        data.append(
            PendingSigningsCollectionItem(
                object_id=str(document.get("_id")),
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
            )
        )
    return data


@router.get("/collections-data/client_users")
async def get_client_users_data(mongo_db: MongoDB = Depends(get_mongo_db)):
    data = []
    async for document in await mongo_db.get_client_users_data():
        data.append(
            ClientUserCollectionItem(
                first_name=document.get("first_name"),
                last_name=document.get("last_name"),
                personal_id=document.get("personal_id"),
                email=document.get("email"),
                palga=document.get("palga"),
                team=document.get("team"),
            )
        )
    return data


@router.get("/collections-data/inventory")
async def get_inventory_data(mongo_db: MongoDB = Depends(get_mongo_db)):
    data = []
    async for document in await mongo_db.get_inventory_data():
        data.append(
            InventoryCollectionItem(
                object_id=str(document.get("_id")),
                name=document.get("name"),
                category=document.get("category"),
                count=f'{document.get("count")} / {document.get("total_count")}',
                color=document.get("color"),
                palga=document.get("palga"),
                mami_serial=document.get("mami_serial"),
                manufacture_mkt=document.get("manufacture_mkt"),
                katzi_mkt=document.get("katzi_mkt"),
                serial_no=document.get("serial_no"),
                description=document.get("description"),
                max_amount=document.get("count"),
            )
        )
    return data

@router.get("/collections-data/remove_signing")
async def get_remove_signing_data(mongo_db: MongoDB = Depends(get_mongo_db)):
    data = []
    async for document in await mongo_db.get_signings_data():
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


@router.get("/collections-data/switch_signing")
async def get_switch_signing_data(request: Request, mongo_db: MongoDB = Depends(get_mongo_db)):
    data = []
    session = request.session
    client_old_personal_id = session.get("switch_old_personal_id", None)

    async for document in await mongo_db.get_signings_data_by_personal_id(client_old_personal_id):
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


@router.get("/collections-data/master_approve_switch_requests")
async def get_approve_switch_requests(request: Request, mongo_db: MongoDB = Depends(get_mongo_db)):
    data = []
    status_mapping = {1: "new signer approval required", 2: "sent to Mami approval", 3: "immposible request, reject it"}

    async for document in await mongo_db.get_switch_requests():
        signing_info = await mongo_db.get_signing_item_by_object_id(document.get("signing_id"))
        item_info = await mongo_db.get_inventory_item_by_object_id(
            signing_info.get("item_id")
        )
        signer: ClientUser = await mongo_db.get_client_by_personal_id(
            signing_info.get("client_personal_id")
        )
        new_signer: ClientUser = await mongo_db.get_client_by_personal_id(document.get("new_pid"))
        switch_description = document.get("description")
        switch_status = status_mapping.get(document.get("status"))
        switch_quantity = document.get("quantity")
        data.append(
                    SwitchRequestItem(
                        request_id=str(document.get("_id")),
                        name=item_info.get("name"),
                        category=item_info.get("category"),
                        quantity= switch_quantity,
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
                        status=switch_status
                    )
                )
    return data

@router.get("/collections-data/update_client_users")
async def get_update_client_users_data(mongo_db: MongoDB = Depends(get_mongo_db)):
    data = []
    async for document in await mongo_db.get_client_users_data():
        data.append(
            UpdateClientUserCollectionItem(
                user_id=str(document.get("_id")),
                first_name=document.get("first_name"),
                last_name=document.get("last_name"),
                personal_id=document.get("personal_id"),
                email=document.get("email"),
                palga=document.get("palga"),
                team=document.get("team"),
                password=document.get("password")
            )
        )
    return data
