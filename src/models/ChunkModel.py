from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes.data_chunk import DataChunk
from bson.objectid import ObjectId
from pymongo import InsertOne
class ChunkModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.CHUNKS_COLLECTION_NAME.value] # create "chunks" collection 
    
    @classmethod
    async def create_instance(cls, db_client):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        
        if DataBaseEnum.CHUNKS_COLLECTION_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.CHUNKS_COLLECTION_NAME.value]
            indexes = DataChunk.get_indexes()
            for index in indexes:
               await  self.collection.create_index(
                    key = index["key"],
                    name = index["name"],
                    unique = index["unique"]
                )
    

    # add a chunk document to collection
    async def add_chunk(self, data_chunk: DataChunk):
        result = await self.collection.insert_one(data_chunk.model_dump(by_alias = True, exclude_unset = True))
        data_chunk.id = result.inserted_id

        return data_chunk
    
    # add many chunks
    async def add_many_chunks(self, data_chunks: list, batch_size: int = 100):

        for i in range(0, len(data_chunks), batch_size):
            self.collection.insert_many([chunk.dict(by_alias = True, exclude_unset = True) for chunk in data_chunks[i : i + batch_size]])

        return len(data_chunks)
    

    # get a chunk from collection
    async def get_chunk_by_id(self, chunk_id: str):
        document = await self.collection.find_one({
            "id": ObjectId(chunk_id)
        })
       
        if document is None:
            return None
        
        return DataChunk(**document)
    
    # get a specific number of a project chunks from collection
    async def get_chunks_from_project(self, project_id: ObjectId, page_num: int = 1, page_size: int = 50):
    
        documents = await self.collection.find({
            "chunk_project_id": project_id
        }).skip((page_num - 1) * page_size).limit(page_size).to_list(length = None)
    
        return [DataChunk(**document) for document in documents]
    

    # delete chunks by project_id and return how many were deleted
    async def delete_chunks_by_project_id(self, project_id: ObjectId):

        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })

        return result.deleted_count

    # get all chunks belonging to a specific asset (file)
    async def get_chunks_by_asset_id(self, asset_id: ObjectId):
        documents = await self.collection.find({
            "chunk_asset_id": asset_id
        }).to_list(length=None)

        return [DataChunk(**document) for document in documents]

    # delete chunks by asset_id and return how many were deleted
    async def delete_chunks_by_asset_id(self, asset_id: ObjectId):
        result = await self.collection.delete_many({
            "chunk_asset_id": asset_id
        })

        return result.deleted_count
    