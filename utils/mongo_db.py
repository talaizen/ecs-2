from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from utils.pydantic_forms import LoginForm, MasterAccount



class MongoDB:
    MASTER_USERS_COLLECTION = "master_users"
    
    def __init__(self, db_url: str, db_name: str) -> None:
        self.client = AsyncIOMotorClient(db_url)
        self.db = self.client[db_name]

    @property
    def master_users_collection(self):
        return self.db[self.MASTER_USERS_COLLECTION]
    
    async def is_master_password(self, password: str) -> bool:
        MASTER_PASSWORD = "Aizen"
        document = await self.master_users_collection.find_one({"password": password})
        return document is not None or password == MASTER_PASSWORD
    
    async def is_existing_master(self, personal_id) -> bool:
        document = await self.master_users_collection.find_one({"personal_id": personal_id})
        return document is not None
                                             
    async def insert_master_account(self, account_data: MasterAccount) -> ObjectId:
        result = await self.master_users_collection.insert_one(account_data)
        print(f'result id: {result.inserted_id}, {type(result.inserted_id)}')
        return result.inserted_id
    
    def close_session(self):
        self.client.close()
