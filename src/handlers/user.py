from models.UserModel import UserModel
from models.db_schemes.user import User
import uuid
from models.enums.ResponseEnums import ResponseSignal
from bson.objectid import ObjectId

def register(db_client, registered_user: dict):
    # create user object
    user = User(
        user_name = registered_user["name"],
        user_password = registered_user["password"],
        user_email= registered_user["email"],
        user_role= registered_user.get("role", "user")
    )

    # user model instance
    user_model = UserModel.create_instance(db_client= db_client)
    existing_user = user_model.create_user(user = user)

    # if email is already there
    if not existing_user:
        return {"signal": ResponseSignal.EMAIL_EXISTS.value}
    
    return {"signal": ResponseSignal.USER_REGISTER_SUCCESS.value,
            "user_id": str(user.id)}

def login(db_client, credentials: dict):
    # user model instance
    user_model = UserModel.create_instance(db_client= db_client)

    # get user by email
    user = user_model.get_user_by_email(credentials["email"])

    # user found
    if user and user.user_password == credentials["password"]:
        return {"signal": ResponseSignal.LOGIN_SUCCESS.value,
                "user_id": str(user.id),
                "user_role": getattr(user, 'user_role', 'user')}
    
    return {"signal": ResponseSignal.LOGIN_FAILED.value}

def get_profile(db_client, user_id: str):
    # user model instance
    user_model = UserModel.create_instance(db_client= db_client)

    # get user by id
    user = user_model.get_user_by_id(id = user_id)

    # user not found
    if not user:
        return {"signal": ResponseSignal.PROFILE_NOT_FOUND.value}
    
    # convert id from ObjectId to normal string 
    user.id = str(user.id)
    
    return {"signal": ResponseSignal.PROFILE_FOUND.value,
            "userData": user.model_dump()}
