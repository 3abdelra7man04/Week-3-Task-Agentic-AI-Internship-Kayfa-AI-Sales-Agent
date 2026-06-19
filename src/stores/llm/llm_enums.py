from enum import Enum

class LLMEnums(Enum):

    OPENAI = "openai"
    COHERE = "cohere"

class OPENAIEnum(Enum):

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class CoHereEnum(Enum):

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "chatbot"

    DOCUMENT = "search_document"
    QUERY = "search_query"

class DocumentTypeEnum(Enum):

     DOCUMENT = "document"
     QUERY = "query"
