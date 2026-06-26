from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    file_id: str = None
    chunk_size: Optional[int] = 500
    chunk_overlap: Optional[int] = 50
    do_reset: Optional[bool] = False

class UploadRequest(BaseModel):
    uploader_admin_id: Optional[str] = "123456789123456789aaaaaa"
    uploader_admin_name: Optional[str] = "Abanoub Wagih"