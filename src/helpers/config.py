from pydantic_settings import BaseSettings, SettingsConfigDict

# Settings class that's used in main get the app configurations
class Settings(BaseSettings):

    # ---------------------- APP Config ----------------------
    APP_NAME: str
    APP_VERSION: str
    
    # ---------------------- FILES Config ----------------------
    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    FILE_IMAGES_MAX_WIDTH: int
    FILE_IMAGES_DPI: int
    
    # ---------------------- DB Config ----------------------
    MONGODB_URL: str
    MONGODB_DATABASE: str
    CHAT_DOCUMENT_TTL: float
    
    # ---------------------- LLM Config ----------------------

    AGENT_BACKEND: str
    EXTRACTION_BACKEND: str
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str
    RERANKING_BACKEND: str

    OPENROUTER_API_KEY: str
    OPENAI_API_KEY: str
    OPENAI_API_URL: str
    COHERE_API_KEY: str

    AGENT_MODEL_ID: str = None
    EXTRACTION_MODEL_ID: str = None
    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None
    RERANKING_MODEL_ID: str = None

    EXTRACTION_MAX_OUTPUT_TOKENS: int = None
    INPUT_MAX_CHARACTERS: int = None
    GENERATION_OUTPUT_MAX_TOKENS: int = None
    GENERATION_TEMPERATURE: float = None


    # ---------------------- VectorDB Config ----------------------
    VECTOR_DB_BACKEND: str 
    VECTOR_DB_URL: str
    VECTOR_DB_PATH: str
    VECTOR_DB_DISTANCE_METHOD: str

    # ---------------------- Template Config ----------------------
    PRIMARY_LANG: str
    DEFAULT_LANG: str

    class Config():
        env_file = ".env"       # .env path described for the BaseSettings class

def get_settings():
    return Settings()
