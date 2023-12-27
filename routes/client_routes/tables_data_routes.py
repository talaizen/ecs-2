import logging

from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from utils.mongo_db import MongoDB
from utils.dependecy_functions import get_mongo_db
from utils.helpers import generate_user_presentation, get_current_client_user
from utils.pydantic_forms import (
    User,
    LogCollectionItem,
    ClientUser,
    MasterUser,
    SigningsCollectionItem,
    PendingSigningsCollectionItem,
    ClientUserCollectionItem,
    InventoryCollectionItem,
    SigningItem
)


logger = logging.getLogger(__name__)

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/collections-data/client_signings")
async def get_client_signings_data(request: Request,mongo_db: MongoDB = Depends(get_mongo_db)):
    try:
        user: User = await get_current_client_user(request, mongo_db)
    except (ValueError, HTTPException):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    data = []
    async for document in await mongo_db.get_signings_data_by_personal_id(user.personal_id):
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
