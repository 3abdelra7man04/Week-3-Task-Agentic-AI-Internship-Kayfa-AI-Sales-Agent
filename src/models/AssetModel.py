from .BaseDataModel import BaseDataModel
from .db_schemes.asset import Asset
from .enums.DataBaseEnum import DataBaseEnum
from bson import ObjectId

class AssetModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.ASSET_COLLECTION_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.ASSET_COLLECTION_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.ASSET_COLLECTION_NAME.value]
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(asset.model_dump(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id

        return asset

    async def get_all_project_assets(self, asset_project_id: str):
        records = await self.collection.find({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
        }).to_list(length=None)


        return [
            Asset(**record)
            for record in records
        ]
    
    async def get_asset_record(self, asset_project_id: str, asset_name: str):

        record = await self.collection.find_one({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_name": asset_name,
        })

        if record:
            return Asset(**record)

        return None
    
    async def update_asset_status(self, asset_id: str, new_status: str):

        result = await self.db_client.assets.update_one(
        {"_id": ObjectId(asset_id)},
        {"$set": {"asset_status": new_status}})

        return result

    async def delete_asset_by_id(self, asset_id: str):

        result = await self.collection.delete_one({
            "_id": ObjectId(asset_id) if isinstance(asset_id, str) else asset_id
        })

        return result
    