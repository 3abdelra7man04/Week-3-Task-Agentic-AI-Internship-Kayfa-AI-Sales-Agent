from abc import ABC, abstractmethod
from .schemes.retrieved_documents import RetrievedDocuments
class VectordbInterface(ABC):

    @abstractmethod
    def does_collection_exist(self, collection_name: str) -> bool:
        pass

    @abstractmethod
    def list_all_collections(self) -> list:
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> dict:
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass

    @abstractmethod
    def delete_file_indices(self, collection_name: str, chunk_ids: list):
        pass

    @abstractmethod
    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        pass

    @abstractmethod
    def insert_vectors(self, collection_name: str, embedding_texts: list, embedding_vectors: list,
                         metadatas: list = None, batch_size: int = 50):
        pass

    @abstractmethod
    def search_vectors(self, collection_name: str, query_text: str, HyDE: str,
                       query_vector: list, HyDE_vector: list, limit: int) -> list[RetrievedDocuments]:
        pass
