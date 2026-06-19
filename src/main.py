# import libraries
from fastapi import FastAPI
from routes import base, data, user, nlp, chat
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from fastapi.middleware.cors import CORSMiddleware
from stores.llm.LLMFactory import LLMFactory
from stores.vectordb.vectordbFactory import VectordbFactory
from stores.llm.templates.template_parser import TemplateParser

# fastAPI app
app = FastAPI()

# mongo connection startup
async def startup_db_client():

    # get app settings
    settings = get_settings()

    # initialize mongo connection
    app.mongo_connection = AsyncIOMotorClient(settings.MONGODB_URL) 

    # create db client
    app.db_client = app.mongo_connection[settings.MONGODB_DATABASE] 

    # LLMFactory instance
    llm_factory = LLMFactory(settings= settings)
    # create llm generation client
    app.generation_client = llm_factory.create_provider_instance(provider_name = settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    # create llm embedding client
    app.embedding_client = llm_factory.create_provider_instance(provider_name = settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id = settings.EMBEDDING_MODEL_ID, embedding_size = settings.EMBEDDING_MODEL_SIZE)

    # create llm reranker client
    app.reranking_client = llm_factory.create_provider_instance(provider_name = settings.RERANKING_BACKEND)
    app.reranking_client.set_reranking_model(model_id = settings.RERANKING_MODEL_ID)
    
    # create vector db client
    vectordb_factory = VectordbFactory(settings= settings)
    app.vectordb_client = vectordb_factory.create_provider_instance(provider=settings.VECTOR_DB_BACKEND)

    # template parser
    template_parser = TemplateParser(language=settings.PRIMARY_LANG, default_language=settings.DEFAULT_LANG)
    app.template_parser = template_parser

    # guest chat TTL
    app.guest_chat_TTL = settings.CHAT_DOCUMENT_TTL
    
# mongo connection shutdown
async def shutdown_db_client():
    app.mongo_connection.close()
    app.vectordb_client.close()

app.on_event("startup")(startup_db_client)
app.on_event("shutdown")(shutdown_db_client)

# include the base router created in base.py
app.include_router(base.base_router)
# include the data router created in data.py
app.include_router(data.data_router)
# include the nlp router created in nlp.py
app.include_router(nlp.nlp_router)
# include the user router created in user.py
app.include_router(user.user_router)
# include the chat router created in chat.py
app.include_router(chat.chat_router)

# أهم جزء للربط مع React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # في الـ Production حط رابط الـ React بتاعك بس
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
