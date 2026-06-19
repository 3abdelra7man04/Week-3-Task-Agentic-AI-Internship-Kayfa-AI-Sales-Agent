from langchain.document_loaders.base import BaseLoader
from langchain.schema import Document
from .data import extract_pages

class MyPDFLoader(BaseLoader):
    # the constructor takes the pdf and covert it into images
    def __init__(self, file_path: str, output_base_dir: str, max_width: int, dpi: int):
        super().__init__()
        self.pages = extract_pages(file_path, output_base_dir, max_width, dpi) # convert pdf to a directory of JPEGs
        
        
    def load(self):
        documents = []


        for page in self.pages:
            documents.append(
                Document(
                    page_content= page["content"],
                    metadata = page["metadata"]
                )
            )

        return documents
    