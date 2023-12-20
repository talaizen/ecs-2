import logging
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from .pydantic_forms import MasterAccount


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
    

    # --------------------------------------  inventory collection  --------------------------------------
    async def get_inventory_data(self):
        return self.inventory_collection.find()
    
    async def add_item_to_inventory(self, document: dict):
        result = await self.inventory_collection.insert_one(document)
        return result.inserted_id

    
    # --------------------------------------  close connection  --------------------------------------
    def close_session(self):
        """
        Closes the MongoDB client session.
        """
        self.client.close()
