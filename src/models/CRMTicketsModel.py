from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes.crm_ticket import CRMTicket



class CRMTicketsModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.CRM_TICKETS_COLLECTION_NAME.value]  # create "crm_tickets" collection

    @classmethod
    def create_instance(cls, db_client):
        instance = cls(db_client)
        instance.init_collection()
        return instance

    def init_collection(self):
        all_collections = self.db_client.list_collection_names()

        if DataBaseEnum.CRM_TICKETS_COLLECTION_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.CRM_TICKETS_COLLECTION_NAME.value]
            

    def save_ticket(self, ticket: CRMTicket):
        result = self.collection.insert_one(ticket.model_dump(by_alias=True, exclude_unset=True))
        ticket.id = str(result.inserted_id)

        return ticket
    
    def get_all_tickets(self):
        documents = list(self.collection.find())
        for doc in documents:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        return [CRMTicket(**document) for document in documents]