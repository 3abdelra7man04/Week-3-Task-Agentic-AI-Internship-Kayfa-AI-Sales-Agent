from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
import os


class ProjectController(BaseController):
    # Controller for project directory management
    def __init__(self):
        super().__init__()

    def get_project_path(self, project_id: str):
        # Build project directory path
        project_dir = os.path.join(self.files_dir, project_id)

        # Create project directory if it does not exist
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        # Return absolute project path
        return project_dir
