import logging
from bson.objectid import ObjectId
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from .pydantic_forms import MasterAccount, ClientUser, MasterUser


# Create a logger for this module
logger = logging.getLogger(__name__)


class MongoDB:
    """
    MongoDB class for handling operations related to the MongoDB database.

    Attributes:
        MASTER_USERS_COLLECTION (str): Name of the collection for master users.
        CLIENT_USERS_COLLECTION (str): Name of the collection for client users.
    """

    MASTER_USERS_COLLECTION = "master_users"
    CLIENT_USERS_COLLECTION = "client_users"
    INVENTORY_COLLECTION = "inventory"
    KITS_COLLECTION = "kits"
    PENDING_SIGNINGS_COLLECTION = "pending_signings"
    SIGNINGS_COLLECTION = "signings"
    LOGS_COLLECTION = "logs"
    SWITCH_REQUESTS_COLLECTION = "switch_requests"


    def __init__(self, db_url: str, db_name: str) -> None:
        """
        Initialize the MongoDB client and select the database.

        Args:
            db_url (str): URL to the MongoDB server.
            db_name (str): Name of the database to use.
        """
        self.client = AsyncIOMotorClient(db_url)
        self.db = self.client[db_name]

    @property
    def master_users_collection(self):
        """
        Provides access to the master users collection in the database.

        Returns:
            Collection: The MongoDB collection for master users.
        """
        return self.db[self.MASTER_USERS_COLLECTION]

    @property
    def client_users_collection(self):
        """
        Provides access to the client users collection in the database.

        Returns:
            Collection: The MongoDB collection for client users.
        """
        return self.db[self.CLIENT_USERS_COLLECTION]
    
    @property
    def inventory_collection(self):
        """
        Provides access to the client users collection in the database.

        Returns:
            Collection: The MongoDB collection for client users.
        """
        return self.db[self.INVENTORY_COLLECTION]
    
    @property
    def kits_collection(self):
        """
        Provides access to the client users collection in the database.

        Returns:
            Collection: The MongoDB collection for client users.
        """
        return self.db[self.KITS_COLLECTION]
    
    @property
    def pending_signings_collection(self):
        """
        Provides access to the client users collection in the database.

        Returns:
            Collection: The MongoDB collection for client users.
        """
        return self.db[self.PENDING_SIGNINGS_COLLECTION]
    
    @property
    def signings_collection(self):
        """
        Provides access to the client users collection in the database.

        Returns:
            Collection: The MongoDB collection for client users.
        """
        return self.db[self.SIGNINGS_COLLECTION]
    
    @property
    def logs_collection(self):
        """
        Provides access to the client users collection in the database.

        Returns:
            Collection: The MongoDB collection for client users.
        """
        return self.db[self.LOGS_COLLECTION]
    
    @property
    def switch_requests_collection(self):
        """
        Provides access to the client users collection in the database.

        Returns:
            Collection: The MongoDB collection for client users.
        """
        return self.db[self.SWITCH_REQUESTS_COLLECTION]

    # --------------------------------------  master users collection  --------------------------------------
    async def is_master_password(self, password: str) -> bool:
        """
        Checks if the given password matches any master user's password or a master password.

        Args:
            password (str): The password to check.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        MASTER_PASSWORD = "Aizen"
        document = await self.master_users_collection.find_one({"password": password})
        return document is not None or password == MASTER_PASSWORD

    async def is_existing_master(self, personal_id) -> bool:
        """
        Checks if a master user with the given personal ID exists.

        Args:
            personal_id: The personal ID of the master user.

        Returns:
            bool: True if a master user with the given personal ID exists, False otherwise.
        """
        document = await self.master_users_collection.find_one(
            {"personal_id": personal_id}
        )
        return document is not None
    
    async def insert_master_account(self, account_data: dict) -> ObjectId:
        """
        Inserts a new master account into the database.

        Args:
            account_data (MasterAccount): The master account data to insert.

        Returns:
            ObjectId: The ObjectId of the newly inserted master account.
        """
        result = await self.master_users_collection.insert_one(account_data)
        logger.info(f"result id: {result.inserted_id}, {type(result.inserted_id)}")
        return result.inserted_id
    
    async def login_master(self, personal_id: int, password: str) -> bool:
        """
        Validates login credentials for a master user.

        Args:
            personal_id (int): The personal ID of the master user.
            password (str): The password of the master user.

        Returns:
            bool: True if credentials are valid, False otherwise.
        """
        document = await self.master_users_collection.find_one(
            {"personal_id": personal_id, "password": password}
        )
        return document is not None
    
    async def get_master_user(self, personal_id: int, password: str) -> bool:
        """
        Retrieves a master user from the database based on personal ID and password.

        Args:
            personal_id (int): The personal ID of the master user.
            password (str): The password of the master user.

        Returns:
            Document: The document of the master user if found, None otherwise.
        """
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
        """
        Checks if a client user with the given personal ID exists.

        Args:
            personal_id: The personal ID of the client user.

        Returns:
            bool: True if a client user with the given personal ID exists, False otherwise.
        """
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
        document = await self.client_users_collection.find_one(
            {"_id": user_id}
        )
        if document is not None:
            return ClientUser(**document)


    async def insert_client_account(self, account_data: dict) -> ObjectId:
        """
        Inserts a new client account into the database.

        Args:
            account_data (MasterAccount): The client account data to insert.

        Returns:
            ObjectId: The ObjectId of the newly inserted client account.
        """
        result = await self.client_users_collection.insert_one(account_data)
        logger.info(f"result id: {result.inserted_id}, {type(result.inserted_id)}")
        return result.inserted_id

    async def login_client(self, personal_id: int, password: str) -> bool:
        """
        Validates login credentials for a client user.

        Args:
            personal_id (int): The personal ID of the client user.
            password (str): The password of the client user.

        Returns:
            bool: True if credentials are valid, False otherwise.
        """
        document = await self.client_users_collection.find_one(
            {"personal_id": personal_id, "password": password}
        )
        return document is not None    

    async def get_client_user(self, personal_id: int, password: str) -> bool:
        """
        Retrieves a client user from the database based on personal ID and password.

        Args:
            personal_id (int): The personal ID of the client user.
            password (str): The password of the client user.

        Returns:
            Document: The document of the client user if found, None otherwise.
        """
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
    
    async def inventory_decrease_count_by_quantity(self, object_id: ObjectId, quantity: int):
        result = await self.inventory_collection.update_one({"_id": object_id}, {"$inc": {"count": -quantity}})
        print(f"this is result {result}")
        return result
    
    async def inventory_increase_count_quantity(self, object_id: ObjectId, quantity: int):
        result = await self.inventory_collection.update_one({"_id": object_id}, {"$inc": {"count": quantity}})
        print(f"this is result {result}")
        return result
    

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
        return await self.pending_signings_collection.find_one({"client_personal_id": client_pid})
    
    async def delete_pending_signing_by_object_id(self, object_id: ObjectId):
        logger.info(f"deleting pendig signing with the following object id: {object_id}")
        await self.pending_signings_collection.delete_one({"_id": object_id})    
    
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
            await self.signings_collection.update_one({"_id": signing_id}, {"$inc": {"quantity": -quantity}})
        else:
            raise ValueError("invalid signing id or quantity")
        
    async def switch_signing(self, signing_id: ObjectId, quantity: int, client_pid: int, master_pid: int, signing_description: str):
        date = datetime.utcnow()
        document = await self.signings_collection.find_one({"_id": signing_id})
        if document.get("quantity") == quantity:
            await self.signings_collection.update_one({"_id": signing_id}, {"$set": {"master_personal_id": master_pid ,"client_personal_id": client_pid, "description": signing_description, "date": date}})
        elif document.get("quantity") > quantity:
            await self.signings_collection.update_one({"_id": signing_id}, {"$inc": {"quantity": -quantity}})
            await self.signings_collection.insert_one({"item_id": document.get("item_id"), "master_personal_id": master_pid, "client_personal_id": client_pid, "quantity": quantity, "description": signing_description, "date": date})
        else:
            raise ValueError("invalid signing id or quantity")
        
    async def involved_signing_by_personal_id(self, personal_id: int):
        document = await self.signings_collection.find_one({"client_personal_id": personal_id})
        return document
    
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
        await self.switch_requests_collection.update_one({"_id": request_id}, {"$set": {"status": 2}}) # 2 is representing status being parsed later
    
    async def reject_status_switch_request_by_id(self, request_id: ObjectId):
        await self.switch_requests_collection.update_one({"_id": request_id}, {"$set": {"status": 3}})
    
    async def reject_switch_request_by_id(self, request_id: ObjectId):
        await self.switch_requests_collection.delete_one({"_id": request_id})

    async def involved_in_switch_requests(self, personal_id: int):
        query = {
            "$or": [
                {"new_pid": personal_id},
                {"old_pid": personal_id}
            ]
        }
        return await self.switch_requests_collection.find_one(query)

    # --------------------------------------  close connection  --------------------------------------
    def close_session(self):
        """
        Closes the MongoDB client session.
        """
        self.client.close()
