from bson import ObjectId
from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import logging
from .schemes.chat import ChatRequest, RenameChatRequest
from models.ProjectModel import ProjectModel
from models.ChatModel import ChatModel
from models.enums.ResponseEnums import ResponseSignal
from controllers import NLPController
from models.db_schemes.chat import Chat
from datetime import datetime, timedelta


# Uvicorn logger instance
logger = logging.getLogger("uvicorn.error")

# nlp API router
chat_router = APIRouter(
    prefix="/api/v1/chat",
    tags=["api_v1", "chat"],
)

# start conversation
@chat_router.post("/{project_id}")
async def start_conversation(request: Request, project_id: str,  chat_request: ChatRequest):

    # get projects collection or create it
    db_client = request.app.db_client  # get the db_client

    project_model = await ProjectModel.create_instance(
        db_client=db_client
    )  # create the ProjectModel instance

    project = await project_model.get_project_or_create_one(project_id=project_id)

    # project not found
    if not project:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
            )
    
    # nlp_controller instance
    nlp_controller = NLPController(generation_client= request.app.generation_client,
                                   embedding_client=request.app.embedding_client,
                                   vectordb_client= request.app.vectordb_client,
                                   template_parser=request.app.template_parser,
                                   reranking_client= request.app.reranking_client)
    
    answer, full_prompt, chat_history, *_ = nlp_controller.answer_rag_questions(project, query = chat_request.query, limit=chat_request.limit)

    # chat model
    chat_model = await ChatModel.create_instance(db_client)

    # chat title
    chat_title = None
    if not chat_request.is_guest:
        chat_title = chat_request.query[:30]

    # chat conversation
    chat_conversation = [{"question": chat_request.query, "answer": answer}]

    # create chat
    ## if not guest
    if not chat_request.is_guest:
        chat_id = await chat_model.create_chat(Chat(
            chat_project_id= project.id,
            chat_user_id= ObjectId(chat_request.user_id),
            is_guest_chat= False,
            chat_title= chat_title,
            chat_history=chat_history,
            chat_conversation= chat_conversation,
            updatedAt=datetime.utcnow()
        ))
    ## if guest
    else:
        chat_id = await chat_model.create_chat(Chat(
            chat_project_id= project.id,
            is_guest_chat= True,
            chat_title= chat_title,
            chat_history=chat_history,
            chat_conversation= chat_conversation,
            updatedAt=datetime.utcnow(),
            expiresAt=datetime.utcnow() + timedelta(seconds=request.app.guest_chat_TTL)
        ))


    if not answer:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.RAG_ANSWER_ERROR.value}
        )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
                 "answer": answer,
                 "chat_id": str(chat_id),
                 "chat_title": chat_title}
    )
    

@chat_router.post("/{project_id}/c/{chat_id}")
async def continue_conversation(request: Request, project_id: str, chat_id: str,  chat_request: ChatRequest):

    # get projects collection or create it
    db_client = request.app.db_client  # get the db_client

    project_model = await ProjectModel.create_instance(
        db_client=db_client
    )  # create the ProjectModel instance

    project = await project_model.get_project_or_create_one(project_id=project_id)

    # project not found
    if not project:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
            )
    
    # nlp_controller instance
    nlp_controller = NLPController(generation_client= request.app.generation_client,
                                   embedding_client=request.app.embedding_client,
                                   vectordb_client= request.app.vectordb_client,
                                   template_parser=request.app.template_parser,
                                   reranking_client= request.app.reranking_client)
    
    # chat model
    chat_model = await ChatModel.create_instance(db_client)

    # get chat history
    chat = await chat_model.get_chat_by_id(chat_id= ObjectId(chat_id))

    chat_history = chat.chat_history

    
    # get answer
    answer, full_prompt, chat_history, *_ = nlp_controller.answer_rag_questions(project, query = chat_request.query,
                                                                            limit=chat_request.limit,
                                                                            chat_history = chat_history)

    
    print(f"chat_id: {chat_id}")

    # update chat history
    _ = await chat_model.update_chat_history_and_conversation(
        chat_id= ObjectId(chat_id),
        chat_history=chat_history,
        question= chat_request.query,
        answer = answer
    )

    # if guest update expiry  
    if chat_request.is_guest:
        _ = await chat_model.update_chat_expiry(chat_id= ObjectId(chat_id), TTL = request.app.guest_chat_TTL)

    # return response
    if not answer:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.RAG_ANSWER_ERROR.value}
        )
    
    return JSONResponse(
        status_code= status.HTTP_200_OK,
        content={"signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
                 "answer": answer,
                 "chat_id": str(chat_id),
                 "chat_title": chat.chat_title}
    )

@chat_router.get("/{project_id}/list/{user_id}")
async def list_chats(request: Request, project_id: str, user_id: str):
    
     # get projects collection or create it
    db_client = request.app.db_client  # get the db_client

    project_model = await ProjectModel.create_instance(
        db_client=db_client
    )  # create the ProjectModel instance

    project = await project_model.get_project_or_create_one(project_id=project_id)

    # project not found
    if not project:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
            )
    
    # chat model instance
    chat_model = await ChatModel.create_instance(db_client)

    # get all chats
    all_chats = await chat_model.list_all_user_chats(project_id= ObjectId(project.id),
                                                     user_id = ObjectId(user_id),
                                                     ascending=False)
    
    for chat in all_chats:
        chat["_id"] = str(chat["_id"])
        chat["updatedAt"] = str(chat["updatedAt"])

    # return response
    if not all_chats:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.LIST_CHATS_ERROR.value}
        )
    
    return JSONResponse(
        status_code= status.HTTP_200_OK,
        content={"signal": ResponseSignal.LIST_CHATS_SUCCESS.value,
                 "all_chats": all_chats}
    )

@chat_router.get("/{project_id}/get/{chat_id}")
async def get_chat_conversation(request: Request, project_id: str, chat_id: str):
    
     # get projects collection or create it
    db_client = request.app.db_client

    project_model = await ProjectModel.create_instance(db_client=db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    # project not found
    if not project:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
            )
    
    # chat model instance
    chat_model = await ChatModel.create_instance(db_client)

    # get chat history safely
    try:
        chat = await chat_model.get_chat_by_id(chat_id= ObjectId(chat_id))
    except Exception:
        chat = None

    if not chat:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.LIST_CHATS_ERROR.value}
        )
    
    return JSONResponse(
        status_code= status.HTTP_200_OK,
        content={"signal": ResponseSignal.LIST_CHATS_SUCCESS.value,
                 "chat_conversation": chat.chat_conversation}
    )


@chat_router.delete("/{project_id}/delete/{chat_id}")
async def delete_conversation(request: Request, project_id: str, chat_id: str):

    # get projects collection or create it
    db_client = request.app.db_client

    project_model = await ProjectModel.create_instance(db_client=db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    # project not found
    if not project:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
            )
    
    # chat model instance
    chat_model = await ChatModel.create_instance(db_client)

    # delete conversation
    del_res = await chat_model.delete_chat_by_id(chat_id= ObjectId(chat_id))

    if not del_res:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.CHAT_DELETE_ERROR.value}
        )
    
    return JSONResponse(
        status_code= status.HTTP_200_OK,
        content={"signal": ResponseSignal.CHAT_DELETE_SUCCESS.value}
    )

@chat_router.put("/{project_id}/rename/{chat_id}")
async def rename_chat(request: Request, project_id: str, chat_id: str, rename_chat_request: RenameChatRequest):

    # get projects collection or create it
    db_client = request.app.db_client

    project_model = await ProjectModel.create_instance(db_client=db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    # project not found
    if not project:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
            )
    
    # chat model instance
    chat_model = await ChatModel.create_instance(db_client)

    # update chat title
    rename_res = await chat_model.update_chat_title(chat_id=ObjectId(chat_id),
                                                    chat_title= rename_chat_request.new_title)

    if not rename_res:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.CHAT_RENAME_ERROR.value}
        )
    
    return JSONResponse(
        status_code= status.HTTP_200_OK,
        content={"signal": ResponseSignal.CHAT_RENAME_SUCCESS.value}
    )
