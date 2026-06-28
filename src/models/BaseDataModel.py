from helpers.config import get_settings

class BaseDataModel:
    def __init__(self, db_client: object):
        self.db_client = db_client         # get db client
        self.app_settings = get_settings() # get app settings
