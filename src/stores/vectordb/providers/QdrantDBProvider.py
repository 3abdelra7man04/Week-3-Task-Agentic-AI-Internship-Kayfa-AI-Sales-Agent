from ..vectordb_interface import VectordbInterface
from ..vectordb_enums import DistanceMethodsEnums
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams, SparseVectorParams, SparseIndexParams, Modifier
import uuid
from qdrant_client.models import Document, Prefetch, FusionQuery, Fusion
from ..schemes.retrieved_documents import RetrievedDocuments
class QdrantDBProvider(VectordbInterface):
    
    # constructor
    def __init__(self, db_url: str, db_key: str, distance_method: str):
        super().__init__()

        self.db_url = db_url

        self.client = QdrantClient(url = db_url, api_key=db_key)

        # cosine distance
        if distance_method == DistanceMethodsEnums.COSINE.value:
            self.distance_method = Distance.COSINE
        
        # dot distance
        if distance_method == DistanceMethodsEnums.DOT.value:
            self.distance_method = Distance.DOT

        self.logger = logging.getLogger(__name__)

    # collection existence
    def does_collection_exist(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    # list all collections
    def list_all_collections(self) -> list:
        return self.client.get_collections()
    
    # collection info
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    # delete collection
    def delete_collection(self, collection_name):
        if self.does_collection_exist(collection_name):
            try:
                # Try to completely drop the collection
                return self.client.delete_collection(collection_name=collection_name)
            except Exception as e:
                # On Windows, deleting the collection folder might throw PermissionError due to file locks.
                # Fallback: keep the collection but delete all points inside it.
                self.logger.warning(f"Failed to delete collection {collection_name} fully, falling back to clearing points. Error: {e}")
                return False

        self.logger.error(f"cannot find collection of name : {collection_name}")
        return False

    # delete indices of a specific file from the collection
    def delete_file_indices(self, collection_name: str, chunk_ids: list):
        """
        Delete all vector points belonging to a specific file from a Qdrant collection.
        
        Args:
            collection_name: Name of the Qdrant collection.
            chunk_ids: List of MongoDB chunk _id strings associated with the file.
                       These are converted to the same uuid5 hex used during insertion.
        
        Returns:
            True if deletion succeeded, False otherwise.
        """
        if not self.does_collection_exist(collection_name):
            self.logger.error(f"cannot find collection of name : {collection_name}")
            return False

        if not chunk_ids or len(chunk_ids) == 0:
            self.logger.warning("No chunk IDs provided for deletion.")
            return False

        # Convert MongoDB chunk IDs to the Qdrant point IDs
        # (same formula used in insert_vectors)
        point_ids = [
            uuid.uuid5(uuid.NAMESPACE_OID, str(cid)).hex
            for cid in chunk_ids
        ]

        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=point_ids,
            )
            self.logger.info(
                f"Deleted {len(point_ids)} points from collection '{collection_name}'"
            )
            return True
        except Exception as e:
            self.logger.error(
                f"Error deleting file indices from {collection_name}: {e}"
            )
            return False

    # create collection for hybrid search (dense + sparse)
    def create_collection(self, collection_name, embedding_size, do_reset):
        
        if do_reset:
            self.delete_collection(collection_name)
        
        # if collection does not exist
        if not self.does_collection_exist(collection_name):
            self.client.create_collection(collection_name = collection_name,
                                          vectors_config = {"dense": VectorParams(size= embedding_size,
                                                                                     distance=self.distance_method)},
                                          sparse_vectors_config = {"sparse": SparseVectorParams(index = SparseIndexParams(on_disk = False), 
                                                                                     modifier = Modifier.IDF)})

            return True
        
        # if collection does exist
        return False
    
    def insert_vectors(self, collection_name: str, embedding_texts: list, embedding_vectors: list,
                         metadatas: list = None, chunk_ids: list = None, batch_size: int = 50):

        # handle none metadata
        if metadatas is None:
            metadatas = [None] * len(embedding_texts)
            
        # handle none chunk_ids
        if chunk_ids is None:
            chunk_ids = [uuid.uuid4().hex for _ in range(len(embedding_texts))]
        
        # check collection existence
        if not self.does_collection_exist(collection_name= collection_name):
            self.logger.error(f"cannot find collection of name : {collection_name}")
            return False
        
        # insert vectors (dense and sparse (bm25 model))
        for i in range(0, len(embedding_texts), batch_size):
            batch_end = i + batch_size

            batch_embedding_texts = embedding_texts[i:batch_end]
            batch_embedding_vectors = embedding_vectors[i:batch_end]
            batch_metadatas = metadatas[i:batch_end]
            batch_chunk_ids = chunk_ids[i:batch_end]
            
            try:
                self.client.upsert(collection_name= collection_name,
                                wait=True,
                                points= [PointStruct(id= uuid.uuid5(uuid.NAMESPACE_OID, str(batch_chunk_ids[j])).hex, vector= {"dense": batch_embedding_vectors[j],
                                                                         "sparse": Document(text=batch_embedding_texts[j],
                                                                                            model="qdrant/bm25")},
                                                    payload={
                                                        "text": batch_embedding_texts[j],
                                                        "metadata": batch_metadatas[j]
                                                    }) 
                                        for j in range(len(batch_embedding_texts))]
                                )
            except Exception as e:
                self.logger.error(f"Error while inserting batch {e}")
                return False
        
        return True
    
    def search_vectors(self, collection_name: str, query_text: str, HyDE: str, 
                       query_vector: list, HyDE_vector: list, limit: int):
        # check collection existence
        if not self.does_collection_exist(collection_name= collection_name):
            self.logger.error(f"cannot find collection of name : {collection_name}")
            return None
        
        results =  self.client.query_points(collection_name= collection_name,
                                            prefetch=[
                                                        # query : Semantic search
                                                        Prefetch(
                                                            query=query_vector,
                                                            using="dense",
                                                            limit= limit
                                                        ),
                                                        # query : Keyword search
                                                        Prefetch(
                                                            query= Document(text=query_text, model="qdrant/bm25"),
                                                            using="sparse",
                                                            limit= limit
                                                        ),
                                                        # HyDE : Semantic search
                                                        Prefetch(
                                                            query=HyDE_vector,
                                                            using="dense",
                                                            limit= limit
                                                        ),
                                                        # HyDE : Keyword search
                                                        Prefetch(
                                                            query= Document(text=HyDE, model="qdrant/bm25"),
                                                            using="sparse",
                                                            limit= limit
                                                        ),
                                                    ],
                                            query=FusionQuery(fusion=Fusion.RRF), limit=limit, with_payload=True).points
        
        if not results:
            self.logger.error(f"search error : {collection_name}")
            return None
        
        return [RetrievedDocuments(**{
            "text": result.payload.get("text", "") if result.payload else "",
            "score": result.score
        }) for result in results if result.payload]
    