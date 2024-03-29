import logging
from bson.objectid import ObjectId
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from .pydantic_forms import ClientUser, MasterUser, InventoryCollectionItemUpdates


logger = logging.getLogger(__name__)


class MongoDB:
    MASTER_USERS_COLLECTION = "master_users"
    CLIENT_USERS_COLLECTION = "client_users"
    INVENTORY_COLLECTION = "inventory"
    KITS_COLLECTION = "kits"
    PENDING_SIGNINGS_COLLECTION = "pending_signings"
    SIGNINGS_COLLECTION = "signings"
    LOGS_COLLECTION = "logs"
    SWITCH_REQUESTS_COLLECTION = "switch_requests"
    KITS_ITEMS_COLLECTION = "kits_items"
    AMPLIFIER_TRACKING_COLLECTION = "amplifier_tracking"

    def __init__(self, db_url: str, db_name: str) -> None:
        self.client = AsyncIOMotorClient(db_url)
        self.db = self.client[db_name]

    # --------------------------------------  collections properties  --------------------------------------

    @property
    def master_users_collection(self):
        return self.db[self.MASTER_USERS_COLLECTION]

    @property
    def client_users_collection(self):
        return self.db[self.CLIENT_USERS_COLLECTION]

    @property
    def inventory_collection(self):
        return self.db[self.INVENTORY_COLLECTION]

    @property
    def kits_collection(self):
        return self.db[self.KITS_COLLECTION]

    @property
    def pending_signings_collection(self):
        return self.db[self.PENDING_SIGNINGS_COLLECTION]

    @property
    def signings_collection(self):
        return self.db[self.SIGNINGS_COLLECTION]

    @property
    def logs_collection(self):
        return self.db[self.LOGS_COLLECTION]

    @property
    def switch_requests_collection(self):
        return self.db[self.SWITCH_REQUESTS_COLLECTION]

    @property
    def kits_items_collection(self):
        return self.db[self.KITS_ITEMS_COLLECTION]

    @property
    def amplifier_tracking_collection(self):
        return self.db[self.AMPLIFIER_TRACKING_COLLECTION]

    # --------------------------------------  master users collection  --------------------------------------
    async def is_master_password(self, password: str) -> bool:
        MASTER_PASSWORD = "Aizen"
        document = await self.master_users_collection.find_one({"password": password})
        return document is not None or password == MASTER_PASSWORD

    async def is_existing_master(self, personal_id) -> bool:
        document = await self.master_users_collection.find_one(
            {"personal_id": personal_id}
        )
        return document is not None

    async def insert_master_account(self, account_data: dict) -> ObjectId:
        result = await self.master_users_collection.insert_one(account_data)
        logger.info(f"result id: {result.inserted_id}, {type(result.inserted_id)}")
        return result.inserted_id

    async def login_master(self, personal_id: int, password: str) -> bool:
        document = await self.master_users_collection.find_one(
            {"personal_id": personal_id, "password": password}
        )
        return document is not None

    async def get_master_user(self, personal_id: int, password: str) -> bool:
        document = await self.master_users_collection.find_one(
            {"personal_id": personal_id, "password": password}
        )
        return document

    async def get_master_by_personal_id(self, personal_id) -> MasterUser or None:
        document = await self.master_users_collection.find_one(
            {"personal_id": personal_id}
        )
        if document is not None:
            return MasterUser(**document)

    # --------------------------------------  client users collection  --------------------------------------
    async def is_existing_client(self, personal_id) -> bool:
        document = await self.client_users_collection.find_one(
            {"personal_id": personal_id}
        )
        return document is not None

    async def get_client_by_personal_id(self, personal_id) -> ClientUser or None:
        document = await self.client_users_collection.find_one(
            {"personal_id": personal_id}
        )
        if document is not None:
            return ClientUser(**document)

    async def get_client_by_object_id(self, user_id: ObjectId) -> ClientUser or None:
        document = await self.client_users_collection.find_one({"_id": user_id})
        if document is not None:
            return ClientUser(**document)

    async def insert_client_account(self, account_data: dict) -> ObjectId:
        result = await self.client_users_collection.insert_one(account_data)
        logger.info(f"result id: {result.inserted_id}, {type(result.inserted_id)}")
        return result.inserted_id

    async def login_client(self, personal_id: int, password: str) -> bool:
        document = await self.client_users_collection.find_one(
            {"personal_id": personal_id, "password": password}
        )
        return document is not None

    async def get_client_user(self, personal_id: int, password: str) -> bool:
        document = await self.client_users_collection.find_one(
            {"personal_id": personal_id, "password": password}
        )
        return document

    async def get_client_users_data(self):
        return self.client_users_collection.find()

    async def delete_client_user(self, user_id: ObjectId):
        await self.client_users_collection.delete_one({"_id": user_id})

    # --------------------------------------  inventory collection  --------------------------------------
    async def get_inventory_data(self):
        return self.inventory_collection.find()

    async def add_item_to_inventory(self, document: dict):
        result = await self.inventory_collection.insert_one(document)
        return result.inserted_id

    async def get_inventory_item_by_object_id(self, object_id: ObjectId):
        document = await self.inventory_collection.find_one({"_id": object_id})
        return document
    
    async def get_inventory_item_by_kit_id(self, kit_id: ObjectId):
        document = await self.inventory_collection.find_one({"kit_id": kit_id})
        return document

    async def inventory_decrease_count_by_quantity(
        self, object_id: ObjectId, quantity: int
    ):
        result = await self.inventory_collection.update_one(
            {"_id": object_id}, {"$inc": {"count": -quantity}}
        )
        return result

    async def inventory_increase_count_quantity(
        self, object_id: ObjectId, quantity: int
    ):
        result = await self.inventory_collection.update_one(
            {"_id": object_id}, {"$inc": {"count": quantity}}
        )
        return result

    async def edit_inventory_item_by_id(
        self,
        item_id: ObjectId,
        new_info: InventoryCollectionItemUpdates,
        new_count: int,
    ):
        result = await self.inventory_collection.update_one(
            {"_id": item_id},
            {
                "$set": {
                    "name": new_info.name,
                    "category": new_info.category,
                    "count": new_count,
                    "color": new_info.color,
                    "palga": new_info.palga,
                    "mami_serial": new_info.mami_serial,
                    "manufacture_mkt": new_info.manufacture_mkt,
                    "katzi_mkt": new_info.katzi_mkt,
                    "serial_no": new_info.serial_no,
                    "description": new_info.description,
                    "total_count": new_info.total_count,
                }
            },
        )
        return result

    async def delete_item_from_inventory(self, item_id: ObjectId):
        await self.inventory_collection.delete_one({"_id": item_id})

    async def get_kit_description_from_inventory(self, kit_id: ObjectId):
        document = await self.inventory_collection.find_one({"kit_id": kit_id})
        if document:
            return document.get("description")

    async def delete_kit_from_inventory(self, kit_id: ObjectId):
        await self.inventory_collection.delete_one({"kit_id": kit_id})

    # --------------------------------------  pending signings collection  --------------------------------------
    async def add_item_to_pending_signings(self, document: dict):
        result = await self.pending_signings_collection.insert_one(document)
        return result.inserted_id

    async def get_pending_signings_data(self):
        return self.pending_signings_collection.find()

    async def get_pending_signing_by_object_id(self, object_id: ObjectId):
        document = await self.pending_signings_collection.find_one({"_id": object_id})
        return document

    async def get_pending_signing_by_client_pid(self, client_pid: int):
        return await self.pending_signings_collection.find_one(
            {"client_personal_id": client_pid}
        )

    async def delete_pending_signing_by_object_id(self, object_id: ObjectId):
        await self.pending_signings_collection.delete_one({"_id": object_id})

    async def get_involved_item_in_pending_signings(self, item_id: ObjectId):
        return await self.pending_signings_collection.find_one({"item_id": item_id})

    # --------------------------------------  signings collection  --------------------------------------
    async def add_item_to_signings(self, document: dict):
        result = await self.signings_collection.insert_one(document)
        return result.inserted_id

    async def get_signings_data(self):
        return self.signings_collection.find()

    async def get_signings_data_by_personal_id(self, personal_id: int):
        document = self.signings_collection.find({"client_personal_id": personal_id})
        return document

    async def get_signing_item_by_object_id(self, signing_id: ObjectId):
        document = await self.signings_collection.find_one({"_id": signing_id})
        return document

    async def remove_signing(self, signing_id: ObjectId, quantity: int):
        document = await self.signings_collection.find_one({"_id": signing_id})
        if document.get("quantity") == quantity:
            await self.signings_collection.delete_one({"_id": signing_id})
        elif document.get("quantity") > quantity:
            await self.signings_collection.update_one(
                {"_id": signing_id}, {"$inc": {"quantity": -quantity}}
            )
        else:
            raise ValueError("invalid signing id or quantity")

    async def switch_signing(
        self,
        signing_id: ObjectId,
        quantity: int,
        client_pid: int,
        master_pid: int,
        signing_description: str,
    ):
        date = datetime.utcnow()
        document = await self.signings_collection.find_one({"_id": signing_id})
        if document.get("quantity") == quantity:
            await self.signings_collection.update_one(
                {"_id": signing_id},
                {
                    "$set": {
                        "master_personal_id": master_pid,
                        "client_personal_id": client_pid,
                        "description": signing_description,
                        "date": date,
                    }
                },
            )
        elif document.get("quantity") > quantity:
            await self.signings_collection.update_one(
                {"_id": signing_id}, {"$inc": {"quantity": -quantity}}
            )
            await self.signings_collection.insert_one(
                {
                    "item_id": document.get("item_id"),
                    "master_personal_id": master_pid,
                    "client_personal_id": client_pid,
                    "quantity": quantity,
                    "description": signing_description,
                    "date": date,
                }
            )
        else:
            raise ValueError("invalid signing id or quantity")

    async def involved_signing_by_personal_id(self, personal_id: int):
        document = await self.signings_collection.find_one(
            {"client_personal_id": personal_id}
        )
        return document

    async def get_involved_item_in_signings(self, item_id: ObjectId):
        return await self.signings_collection.find_one({"item_id": item_id})

    # --------------------------------------  logs collection  --------------------------------------
    async def add_item_to_logs(self, document: dict):
        result = await self.logs_collection.insert_one(document)
        return result.inserted_id

    async def get_logs_data(self):
        return self.logs_collection.find()

    # --------------------------------------  switch requests  ----------------------------------------
    async def get_switch_requests(self):
        return self.switch_requests_collection.find()

    async def get_switch_request_by_id(self, request_id: ObjectId):
        return await self.switch_requests_collection.find_one({"_id": request_id})

    async def add_item_to_switch_requests(self, document: dict):
        result = await self.switch_requests_collection.insert_one(document)
        return result.inserted_id

    async def get_switch_requests_by_old_signer_pid(self, personal_id: int):
        return self.switch_requests_collection.find({"old_pid": personal_id})

    async def get_switch_requests_by_new_signer_pid(self, personal_id: int):
        return self.switch_requests_collection.find({"new_pid": personal_id})

    async def delete_switch_request_by_id(self, request_id: ObjectId):
        await self.switch_requests_collection.delete_one({"_id": request_id})

    async def approve_switch_request_by_id(self, request_id: ObjectId):
        await self.switch_requests_collection.update_one(
            {"_id": request_id}, {"$set": {"status": 2}}
        )  # 2 is representing status being parsed later

    async def reject_status_switch_request_by_id(self, request_id: ObjectId):
        await self.switch_requests_collection.update_one(
            {"_id": request_id}, {"$set": {"status": 3}}
        )

    async def reject_switch_request_by_id(self, request_id: ObjectId):
        await self.switch_requests_collection.delete_one({"_id": request_id})

    async def involved_in_switch_requests(self, personal_id: int):
        query = {"$or": [{"new_pid": personal_id}, {"old_pid": personal_id}]}
        return await self.switch_requests_collection.find_one(query)

    # --------------------------------------  kits collection  ----------------------------------------

    async def involved_kit_by_name(self, kit_name: str):
        return await self.kits_collection.find_one({"name": kit_name})

    async def insert_new_kit(self, document: dict):
        result = await self.kits_collection.insert_one(document)
        return result.inserted_id

    async def get_kits_data(self):
        return self.kits_collection.find()

    async def get_kit_by_id(self, kit_id: ObjectId):
        return await self.kits_collection.find_one({"_id": kit_id})

    async def delete_kit(self, kit_id: ObjectId):
        await self.kits_collection.delete_one({"_id": kit_id})

    # --------------------------------------  kit items collection  ----------------------------------------

    async def add_doc_to_kits_items(self, document: dict):
        kit_id = document.get("kit_id")
        item_id = document.get("item_id")
        quantity = document.get("quantity")
        existing_item = await self.kits_items_collection.find_one(
            {"kit_id": kit_id, "item_id": item_id}
        )
        if existing_item:
            await self.kits_items_collection.update_one(
                {"kit_id": kit_id, "item_id": item_id}, {"$inc": {"quantity": quantity}}
            )
            return existing_item.get("_id")
        else:
            result = await self.kits_items_collection.insert_one(document)
            return result.inserted_id

    async def involved_kit_items(self, kit_id: ObjectId):
        return await self.kits_items_collection.find_one({"kit_id": kit_id})

    async def get_kit_items_by_id(self, kit_id: ObjectId):
        return self.kits_items_collection.find({"kit_id": kit_id})

    async def get_kit_item_object_by_id(self, kit_item_id: ObjectId):
        return await self.kits_items_collection.find_one({"_id": kit_item_id})

    async def remove_kit_item(self, kit_item_id: ObjectId, quantity: int):
        document = await self.kits_items_collection.find_one({"_id": kit_item_id})
        if document.get("quantity") == quantity:
            await self.kits_items_collection.delete_one({"_id": kit_item_id})
        elif document.get("quantity") > quantity:
            await self.kits_items_collection.update_one(
                {"_id": kit_item_id}, {"$inc": {"quantity": -quantity}}
            )
        else:
            raise ValueError("invalid signing id or quantity")

    # --------------------------------------  amplifier tracking collection  ----------------------------------------

    async def add_doc_to_amplifier_tracking(self, document: dict):
        existing_document = await self.amplifier_tracking_collection.find_one(
            {"item_id": document.get("item_id"), "test_type": document.get("test_type")}
        )
        if existing_document:
            raise ValueError(
                "an amplifier tracking with this item and test type already exist"
            )
        await self.amplifier_tracking_collection.insert_one(document)

    async def get_amplifier_tracking_data(self):
        return self.amplifier_tracking_collection.find()

    async def update_amplifier_results(self, object_id: ObjectId, results: str):
        date = datetime.utcnow()
        await self.amplifier_tracking_collection.update_one(
            {"_id": object_id}, {"$set": {"results": results, "last_updated": date}}
        )

    async def update_amplifier_interval(self, object_id: ObjectId, interval: int):
        await self.amplifier_tracking_collection.update_one(
            {"_id": object_id}, {"$set": {"days_interval": interval}}
        )

    async def delete_amplifier_tracking(self, object_id: ObjectId):
        await self.amplifier_tracking_collection.delete_one({"_id": object_id})

    # --------------------------------------  close connection  --------------------------------------
    def close_session(self):
        """
        Closes the MongoDB client session.
        """
        self.client.close()
