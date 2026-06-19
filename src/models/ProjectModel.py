from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes.project import Project


class ProjectModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[
            DataBaseEnum.PROJECT_COLLECTION_NAME.value
        ]  # create "prjects" collection

    # Async factory method to initialize the instance and its DB collection.
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    # Creates the DB collection and builds its indexes if it doesn't exist.
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.PROJECT_COLLECTION_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.PROJECT_COLLECTION_NAME.value]
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"], name=index["name"], unique=index["unique"]
                )

    # add a new project to collection
    async def add_project(self, project: Project):
        result = await self.collection.insert_one(
            project.dict(by_alias=True, exclude_unset=True)
        )
        project.id = result.inserted_id

        return project

    # get a specific project by id, if project isn't there create it
    async def get_project_or_create_one(self, project_id: str):

        # find the project document
        document = await self.collection.find_one({"project_id": project_id})

        # if the project document is None create it
        if document is None:
            project = Project(project_id=project_id)
            project = await self.add_project(project=project)

            return project

        return Project(
            **document
        )  # if there is a project convert it into Project object and return it

    # get all project documents from a specific page the collection and also return the number of the total documents in the colllection
    async def get_all_projects_in_page(self, page: int = 1, page_size: int = 1):

        # count the number of documents in collection
        total_documents = await self.collection.count_documents({})

        # count number of pages
        total_pages = total_documents / page_size
        if total_documents % page_size > 0:
            total_pages += 1

        # get the project documents in the determined page
        projects = []

        cursor = (
            await self.collection.find({}).skip((page - 1) * page_size).limit(page_size)
        )

        async for project in cursor:
            projects.append(Project(**project))

        return projects, total_pages
