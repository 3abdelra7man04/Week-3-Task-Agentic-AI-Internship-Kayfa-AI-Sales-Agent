from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes.asset import Asset
from bson.objectid import ObjectId
from pymongo import InsertOne


class AssetModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.ASSETS_COLLECTION_NAME.value]  # create "chunks" collection

    @classmethod
    def create_instance(cls, db_client):
        instance = cls(db_client)
        instance.init_collection()
        return instance

    def init_collection(self):
        all_collections = self.db_client.list_collection_names()

        if DataBaseEnum.ASSETS_COLLECTION_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.ASSETS_COLLECTION_NAME.value]

    # add a chunk document to collection
    def add_asset(self, asset: Asset):
        result = self.collection.insert_one(asset.model_dump(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id

        return asset

    # get an asset by name
    def get_an_asset(self, asset_name: str):
        return self.collection.find_one({"asset_name": {"$regex": asset_name, "$options": "i"}})