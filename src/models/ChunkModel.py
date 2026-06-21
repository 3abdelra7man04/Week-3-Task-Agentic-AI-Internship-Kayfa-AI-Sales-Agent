from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes.data_chunk import DataChunk
from bson.objectid import ObjectId
from pymongo import InsertOne


class ChunkModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.CHUNKS_COLLECTION_NAME.value]  # create "chunks" collection

    @classmethod
    def create_instance(cls, db_client):
        instance = cls(db_client)
        instance.init_collection()
        return instance

    def init_collection(self):
        all_collections = self.db_client.list_collection_names()

        if DataBaseEnum.CHUNKS_COLLECTION_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.CHUNKS_COLLECTION_NAME.value]
            indexes = DataChunk.get_indexes()
            for index in indexes:
                self.collection.create_index(
                    keys=index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    # add a chunk document to collection
    def add_chunk(self, data_chunk: DataChunk):
        result = self.collection.insert_one(data_chunk.model_dump(by_alias=True, exclude_unset=True))
        data_chunk.id = result.inserted_id

        return data_chunk

    # add many chunks
    def add_many_chunks(self, data_chunks: list, batch_size: int = 100):

        for i in range(0, len(data_chunks), batch_size):
            batch = data_chunks[i: i + batch_size]
            result = self.collection.insert_many(
                [chunk.model_dump(by_alias=True, exclude_unset=True) for chunk in batch]
            )
            for j, inserted_id in enumerate(result.inserted_ids):
                batch[j].id = inserted_id

        return len(data_chunks)

    # get a chunk from collection
    def get_chunk_by_id(self, chunk_id: str):
        document = self.collection.find_one({
            "id": ObjectId(chunk_id)
        })

        if document is None:
            return None

        return DataChunk(**document)

    # get a specific number of a project chunks from collection
    def get_chunks_from_project(self, project_id: ObjectId, page_num: int = 1, page_size: int = 50):

        documents = list(
            self.collection.find({
                "chunk_project_id": project_id
            }).skip((page_num - 1) * page_size).limit(page_size)
        )

        return [DataChunk(**document) for document in documents]

    # delete chunks by project_id and return how many were deleted
    def delete_chunks_by_project_id(self, project_id: ObjectId):

        result = self.collection.delete_many({
            "chunk_project_id": project_id
        })

        return result.deleted_count

    # get all chunks belonging to a specific asset (file)
    def get_chunks_by_asset_id(self, asset_id: ObjectId):
        documents = list(self.collection.find({
            "chunk_asset_id": asset_id
        }))

        return [DataChunk(**document) for document in documents]

    # delete chunks by asset_id and return how many were deleted
    def delete_chunks_by_asset_id(self, asset_id: ObjectId):
        result = self.collection.delete_many({
            "chunk_asset_id": asset_id
        })

        return result.deleted_count