from fastapi import APIRouter, Body, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from models.UserModel import UserModel
from models.ProjectModel import ProjectModel
from models.db_schemes.user import User
import uuid
from models.enums.ResponseEnums import ResponseSignal
from bson.objectid import ObjectId

# User API router
user_router = APIRouter(
    prefix="/api/v1/user",
    tags=["api_v1", "user"],
)

# register route
@user_router.post("/register/{project_id}")
async def register(request: Request, project_id: str, registered_user: dict = Body(...)):

    # retrieve db_client
    db_client = request.app.db_client

    project_model = await ProjectModel.create_instance(db_client=db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)
    

    # create user object
    user = User(
        user_name = registered_user["name"],
        user_password = registered_user["password"],
        user_email= registered_user["email"]
    )

    # user model instance
    user_model = await UserModel.create_instance(db_client= db_client)

    existing_user = await user_model.create_user(user = user)

    # # if email is already there
    if not existing_user:
        return JSONResponse(
            status_code = status.HTTP_409_CONFLICT,
            content = {"signal": ResponseSignal.EMAIL_EXISTS.value}
        )
    
    return JSONResponse(
            content = {"signal": ResponseSignal.USER_REGISTER_SUCCESS.value,
                       "user_id": str(user.id)}
        )

# login route
@user_router.post("/login/{project_id}")
async def login(request: Request, project_id: str, credentials: dict = Body(...)):

    # retrieve db_client
    db_client = request.app.db_client

    project_model = await ProjectModel.create_instance(db_client=db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    # user model instance
    user_model = await UserModel.create_instance(db_client= db_client)

    # get user by email
    user = await user_model.get_user_by_email(credentials["email"])

    # user found
    if user and user.user_password == credentials["password"]:
        return JSONResponse(
            content = {"signal": ResponseSignal.LOGIN_SUCCESS.value,
                       "user_id": str(user.id)}
        )
    
    return JSONResponse(
            status_code = status.HTTP_401_UNAUTHORIZED,
            content = {"signal": ResponseSignal.LOGIN_FAILED.value}
        )

# get profile route
@user_router.get("/get-profile/{project_id}")
async def get_profile(request: Request, project_id: str, user_id: str):

    # retrieve db_client
    db_client = request.app.db_client

    project_model = await ProjectModel.create_instance(db_client=db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    # user model instance
    user_model = await UserModel.create_instance(db_client= db_client)

    # get user by email
    user = await user_model.get_user_by_id(id = user_id)

    # convert id from ObjectId to normal string 
    user.id = str(user.id)

    # user not found
    if not user:
        return JSONResponse(
            status_code = status.HTTP_404_NOT_FOUND,
            content = {"signal": ResponseSignal.PROFILE_NOT_FOUND.value}
        )
    
    return JSONResponse(
            content = {"signal": ResponseSignal.PROFILE_FOUND.value,
                       "userData": user.model_dump()}
        )
