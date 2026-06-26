from bson import ObjectId
from models.ChatModel import ChatModel
from models.db_schemes.chat import Chat
from datetime import datetime

def create_chat(db_client, user_id: str, title: str, chat_history: list, chat_conversation: list):
    chat_model = ChatModel.create_instance(db_client)
    
    new_chat = Chat(
        chat_user_id=ObjectId(user_id) if user_id else None,
        is_guest_chat=False if user_id else True,
        chat_title=title,
        chat_history=chat_history,
        chat_conversation=chat_conversation,
        updatedAt=datetime.utcnow()
    )
    
    chat_id = chat_model.create_chat(new_chat)
    return str(chat_id)

def update_chat(db_client, chat_id: str, chat_history: list, question: str, answer: str):
    chat_model = ChatModel.create_instance(db_client)
    chat_model.update_chat_history_and_conversation(
        chat_id=ObjectId(chat_id),
        chat_history=chat_history,
        question=question,
        answer=answer
    )
    return True

def list_chats(db_client, user_id: str):
    if not user_id:
        return []
    chat_model = ChatModel.create_instance(db_client)
    chats = chat_model.list_all_user_chats(user_id=ObjectId(user_id), ascending=False)
    
    result = []
    for chat in chats:
        chat["_id"] = str(chat["_id"])
        if "updatedAt" in chat:
            chat["updatedAt"] = str(chat["updatedAt"])
        result.append(chat)
    return result

def get_chat(db_client, chat_id: str):
    chat_model = ChatModel.create_instance(db_client)
    chat = chat_model.get_chat_by_id(chat_id=ObjectId(chat_id))
    if chat:
        return chat
    return None

def delete_chat(db_client, chat_id: str):
    chat_model = ChatModel.create_instance(db_client)
    res = chat_model.delete_chat_by_id(chat_id=ObjectId(chat_id))
    return res.deleted_count > 0

def rename_chat(db_client, chat_id: str, new_title: str):
    chat_model = ChatModel.create_instance(db_client)
    res = chat_model.update_chat_title(chat_id=ObjectId(chat_id), chat_title=new_title)
    return res.modified_count > 0
