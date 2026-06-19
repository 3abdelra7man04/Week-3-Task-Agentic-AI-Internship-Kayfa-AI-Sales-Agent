from enum import Enum


class ResponseSignal(Enum):

    # ---------------------- project validation signals ----------------------
    PROJECT_NOT_FOUND = "didn't find project"
    
    # ---------------------- file validation and upload signals ----------------------
    FILE_VALIDATED_SUCCESS = (
        "file_validate_successfully"  # File passed all validation checks
    )
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"  # Unsupported file type
    FILE_SIZE_EXCEEDED = "file_size_exceeded"  # File exceeds maximum allowed size
    FILE_UPLOAD_SUCCESS = "file_upload_success"  # File uploaded successfully
    FILE_UPLOAD_FAILED = "file_upload_failed"  # File upload failed

    # ---------------------- processing signals ----------------------
    PROCESSING_SUCCESS = "processing_success"
    PROCESSING_FAILED = "processing_failed"
    NO_FILES_ERROR = "not_found_files"
    FILE_ID_ERROR = "no_file_found_with_this_id"

    # ---------------------- user signals ----------------------
    EMAIL_EXISTS = "Email already exists"
    USER_REGISTER_SUCCESS = "User successfully registered"
    LOGIN_SUCCESS = "login success"
    LOGIN_FAILED = "login failed"
    PROFILE_FOUND = "profile found successfully"
    PROFILE_NOT_FOUND = "profile not found"

    # ---------------------- vector db signals ----------------------
    VECTOR_DB_INDEXING_ERROR = "error when inserting in vector db"
    VECTOR_DB_INDEXING_SUCCESS = "vectordb indexing success"
    VECTOR_DB_COLLECTION_NOT_FOUND = "vectordb collection not found"
    VECTOR_DB_GET_INFO_SUCCESS = "vectordb collection info retrieved successfully"
    VECTOR_DB_SEARCH_SUCCESS = "succecfully searched vectordb collection"

    # ---------------------- answer signals ----------------------
    RAG_ANSWER_ERROR = "answer error"
    RAG_ANSWER_SUCCESS = "your query is successfully answered"

    # ---------------------- List chat signals ----------------------
    LIST_CHATS_SUCCESS = "chats are successfully listed"
    LIST_CHATS_ERROR = "error in listing chats"
    
    # ---------------------- delete chat signal ----------------------
    CHAT_DELETE_SUCCESS = "chat is successfully deleted"
    CHAT_DELETE_ERROR = "error when deleting chat"
    DELETE_CHAT_SUCCESS = "chat is successfully deleted"
    DELETE_CHAT_ERROR = "error when deleting chat"
    
    # ---------------------- update chat signal ----------------------
    CHAT_RENAME_SUCCESS = "chat title is successfully renamed"
    CHAT_RENAME_ERROR = "error when renaming chat"
    