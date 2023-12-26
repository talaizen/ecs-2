import logging

from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates

from utils.mongo_db import MongoDB
from utils.dependecy_functions import get_mongo_db
from utils.pydantic_forms import (
    LogCollectionItem,
    ClientUser,
    MasterUser,
    SigningsCollectionItem,
    PendingSigningsCollectionItem,
    ClientUserCollectionItem,
    InventoryCollectionItem,
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
async def get_inventory_data(mongo_db: MongoDB = Depends(get_mongo_db)):
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
                signer=f"{signer.first_name} {signer.last_name}({signer.personal_id})",
                issuer=f"{issuer.first_name} {issuer.last_name}({issuer.personal_id})",
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
                signer=f"{signer.first_name} {signer.last_name}({signer.personal_id})",
                issuer=f"{issuer.first_name} {issuer.last_name}({issuer.personal_id})",
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
