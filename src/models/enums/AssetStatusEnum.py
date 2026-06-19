from enum import Enum


class AssetStatusEnum(Enum):
    PROCESSING = "processing"
    IDNEXING = "indexing"
    SUCCESS = "success"
    ERROR = "error"
