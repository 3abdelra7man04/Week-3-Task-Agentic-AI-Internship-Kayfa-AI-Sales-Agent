from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes.admin import Admin
from pymongo.errors import DuplicateKeyError
from pydantic import EmailStr
from bson.objectid import ObjectId

class AdminModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client[DataBaseEnum.ADMINS_COLLECTION_NAME.value]
    
    @classmethod
    async def create_instance(cls, db_client):
        instance = cls(db_client)
        await instance.init_connection()
        return instance

    async def init_connection(self):
        all_collections  = await self.db_client.list_collection_names()

        if DataBaseEnum.ADMINS_COLLECTION_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.ADMINS_COLLECTION_NAME.value]
            indexes = Admin.get_indexes()
            
            for index in indexes:
                await self.collection.create_index(
                keys = index["key"],
                name = index["name"],
                unique = index["unique"]
            )
        
    # check if admin is already created and then create it 
    async def create_admin(self, admin: Admin):
        # admin is unique
        try:
            result = await self.collection.insert_one(admin.model_dump(by_alias=True, exclude_unset=True))
            admin.id = result.inserted_id
            return admin
        # admin is not unique
        except DuplicateKeyError:
            return None
    
    # get admin by email
    async def get_admin_by_email(self, email: EmailStr):

        admin = await self.collection.find_one({"admin_email": email})

        if admin:
            return Admin(**admin)
        else:
            return None
    
    # get admin by id
    async def get_admin_by_id(self, id: str):

        admin = await self.collection.find_one({"_id": ObjectId(id)})

        if admin:
            return Admin(**admin)
        else:
            return None

    async def delete_admin_by_id(self, id: ObjectId):
        result = await self.collection.delete_one({"_id": id})

        return result

    async def list_all_admins(self,  project_id: ObjectId):
        admins = await self.collection.find({"admin_project_id": project_id}).to_list(length=None)

        return admins
