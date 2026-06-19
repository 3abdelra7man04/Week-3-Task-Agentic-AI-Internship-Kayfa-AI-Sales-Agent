from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponseSignal
import re
import os


class DataController(BaseController):
    # Controller for file-related operations
    def __init__(self):
        super().__init__()
        # Used to convert MB to bytes
        self.size_scale = 1048576

    def validate_uploaded_file(self, file: UploadFile):
        # Check allowed file type
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        # Check maximum file size
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        # File passed all validation rules
        return True, ResponseSignal.FILE_VALIDATED_SUCCESS.value

    def generate_unique_filepath(self, orig_file_name: str, project_id: str):
        # Generate random prefix to avoid name collisions
        random_key = self.generate_random_string()

        # Get project directory path
        project_path = ProjectController().get_project_path(project_id=project_id)

        # Sanitize original file name
        cleaned_file_name = self.get_clean_file_name(orig_file_name=orig_file_name)

        # Build initial file path
        new_file_path = os.path.join(project_path, random_key + "_" + cleaned_file_name)

        # Ensure file path is unique
        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path, random_key + "_" + cleaned_file_name
            )

        return new_file_path, random_key + "_" + cleaned_file_name

    def get_clean_file_name(self, orig_file_name: str):
        # Remove special characters except letters, numbers, underscore, and dot
        cleaned_file_name = re.sub(r"[^\w.]", "", orig_file_name.strip())

        # Replace spaces with underscores
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name
