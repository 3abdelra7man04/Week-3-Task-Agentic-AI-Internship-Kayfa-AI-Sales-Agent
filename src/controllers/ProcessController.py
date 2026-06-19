from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader
from .utils.MyPDFLoader import MyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models.enums.ProcesingEnums import ProcessingEnum

# process controller
class ProcessController(BaseController):
    
    # constructor
    def __init__(self, project_id: str):
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)
    
    # get file extension to determine which data loader you'll use
    def get_file_extension(self, file_id: str):
        return os.path.splitext(file_id)[-1]
    
    # get file loader
    def get_file_loader(self, file_id: str):
        file_ext = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(
            self.project_path,
            file_id
        )

        if not os.path.exists(file_path):
            return None
        
        if file_ext == ProcessingEnum.TEXT.value :
            return TextLoader(file_path, encoding = "utf-8")
        
        if file_ext == ProcessingEnum.PDF.value :
            return MyPDFLoader(file_path, self.project_path, self.app_settings.FILE_IMAGES_MAX_WIDTH, self.app_settings.FILE_IMAGES_DPI)
        
        return None
    
    # get file content
    def get_file_content(self, file_id: str):
        loader = self.get_file_loader(file_id=file_id)
        if loader : 
            return loader.load()
        return None
    
    # parse file content
    def process_file_content(self, file_id: str, file_content: list,
                             chunk_size: int, chunk_overlap: int):

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap,
            length_function = len,
        )

        # extract files content test and metadata
        file_content_texts = [p.page_content for p in file_content]
        file_content_metadata = [p.metadata for p in file_content]

        chunks = text_splitter.create_documents(file_content_texts, file_content_metadata)

        return chunks
    