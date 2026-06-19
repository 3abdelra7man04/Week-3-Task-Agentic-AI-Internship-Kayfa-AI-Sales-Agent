from .providers.QdrantDBProvider import QdrantDBProvider
from .vectordb_enums import VectordbEnums
from controllers.BaseController import BaseController

class VectordbFactory:
    def __init__(self, settings: dict):
        self.settings = settings
    
    def create_provider_instance(self, provider: str):

        # qdrant
        if provider == VectordbEnums.QDRANT.value:
            return QdrantDBProvider(db_url= self.settings.VECTOR_DB_URL, distance_method= self.settings.VECTOR_DB_DISTANCE_METHOD,)

        return None
    