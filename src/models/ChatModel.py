from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from .db_schemes.chat import Chat
from datetime import datetime, timedelta

class ChatModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client[DataBaseEnum.CHATS_COLLECTION_NAME.value]
    
    @classmethod
    def create_instance(cls, db_client: object):
        instance = cls(db_client = db_client)
        instance.init_collection()
        return instance
    
    def init_collection(self):
        all_collections = self.db_client.list_collection_names()
        
        if DataBaseEnum.CHATS_COLLECTION_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.CHATS_COLLECTION_NAME.value]
            indexes = Chat.get_indexes()
            for index in indexes:
                keys = index.pop("key")
                self.collection.create_index(
                    keys = keys,
                    **index
                )
    
    # creates chat and returns its id
    def create_chat(self, chat: Chat):
        result = self.collection.insert_one(chat.model_dump(by_alias=True, exclude_unset=True))
        chat.id = result.inserted_id

        return result.inserted_id
    
    def update_chat_history_and_conversation(self, chat_id: ObjectId, chat_history: list[dict], question: str, answer: str):
        result = self.collection.update_one(
            {"_id": chat_id},
            {"$set" : {"chat_history": chat_history, "updatedAt": datetime.utcnow()},
             "$push" : {"chat_conversation": {"question": question, "answer": answer}}}
        )

        return result
    
    def update_chat_expiry(self, chat_id: ObjectId, TTL: float):
        result = self.collection.update_one(
            {"_id": chat_id},
            {"$set" : {"expiresAt": datetime.utcnow() + timedelta(seconds= TTL)}}
        )

        return result

    def update_chat_title(self, chat_id: ObjectId, chat_title: str):
        result = self.collection.update_one(
            {"_id": chat_id},
            {"$set" : {"chat_title": chat_title}},
        )

        return result
    
    def delete_chat_by_id(self, chat_id: ObjectId):
        result = self.collection.delete_one({"_id": chat_id})

        return result

    def get_chat_by_id(self, chat_id: ObjectId):
        chat = self.collection.find_one({"_id": chat_id})

        if not chat:
            return None

        return Chat(**chat)

    def list_all_user_chats(self, user_id: ObjectId, ascending: bool = False):
        
        if ascending == True: 
            order = 1
        else:
            order = -1

        chats = list(self.collection.find({
                "chat_user_id": user_id}, 
                {   
                    "chat_project_id": 0,
                    "chat_user_id": 0,
                    "chat_history": 0,
                    "chat_conversation": 0
                }).sort("updatedAt", order))

        return chats

    def get_all_chats(self, ascending: bool = False):
        order = 1 if ascending else -1
        chats = list(self.collection.find({}).sort("updatedAt", order))
        return chats
