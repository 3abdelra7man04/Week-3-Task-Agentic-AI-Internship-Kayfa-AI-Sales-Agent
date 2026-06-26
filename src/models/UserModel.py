from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes.user import User
from pymongo.errors import DuplicateKeyError
from pydantic import EmailStr
from bson.objectid import ObjectId

class UserModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client[DataBaseEnum.USERS_COLLECTION_NAME.value]
    
    @classmethod
    def create_instance(cls, db_client):
        instance = cls(db_client)
        instance.init_connection()
        return instance

    def init_connection(self):
        all_collections  = self.db_client.list_collection_names()

        if DataBaseEnum.USERS_COLLECTION_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.USERS_COLLECTION_NAME.value]
            indexes = User.get_indexes()
            
            for index in indexes:
                self.collection.create_index(
                keys = index["key"],
                name = index["name"],
                unique = index["unique"]
            )
        
    # check if user is already created and then create it 
    def create_user(self, user: User):
        # user is unique
        try:
            result = self.collection.insert_one(user.model_dump(by_alias=True, exclude_unset=True))
            user.id = result.inserted_id
            return user
        # user is not unique
        except DuplicateKeyError:
            return None
    
    # get user by email
    def get_user_by_email(self, email: EmailStr):

        user = self.collection.find_one({"user_email": email})

        if user:
            return User(**user)
        else:
            return None
    
    # get user by id
    def get_user_by_id(self, id: str):

        user = self.collection.find_one({"_id": ObjectId(id)})

        if user:
            return User(**user)
        else:
            return None
            
    # get all users
    def get_all_users(self):
        users = self.collection.find({})
        return [User(**user) for user in users]
        