from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId

from forms.jason_forms import LoginForm, MasterAccount

class MongoDB:
    MASTER_USERS_COLLECTION = "master_users"
    
    def __init__(self, db_url: str, db_name: str) -> None:
        self.client = AsyncIOMotorClient(db_url)
        self.db = self.client[db_name]
    
    async def insert_master_account(self, account_data: MasterAccount) -> ObjectId:
        collection = self.db[self.MASTER_USERS_COLLECTION]
        result = await collection.insert_one(account_data)
        print(f'result id: {result.inserted_id}, {type(result.inserted_id)}')
        return result.inserted_id
    
    def close_session(self):
        self.client.close()




