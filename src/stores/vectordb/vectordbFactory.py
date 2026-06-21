from .providers.QdrantDBProvider import QdrantDBProvider
from .vectordb_enums import VectordbEnums

class VectordbFactory:
    def __init__(self, settings: dict):
        self.settings = settings
    
    def create_provider_instance(self, provider: str):

        # qdrant
        if provider == VectordbEnums.QDRANT.value:
            return QdrantDBProvider(db_url= self.settings.VECTOR_DB_URL, db_key= self.settings.VECTOR_DB_API_KEY,
                                    distance_method= self.settings.VECTOR_DB_DISTANCE_METHOD,)

        return None
    