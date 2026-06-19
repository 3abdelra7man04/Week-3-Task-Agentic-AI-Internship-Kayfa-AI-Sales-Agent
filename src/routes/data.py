from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request, BackgroundTasks, Form
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController, NLPController
import aiofiles
from models import ResponseSignal
import logging
from .schemes.data import ProcessRequest, UploadRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes.data_chunk import DataChunk
from models.db_schemes.asset import Asset
from models.enums.AssetTypeEnum import AssetTypeEnum
from models.enums.AssetStatusEnum import AssetStatusEnum
from models.enums.ProcesingEnums import ProcessingEnum
import traceback
from bson.objectid import ObjectId
from datetime import datetime, timezone

# Uvicorn logger instance
logger = logging.getLogger("uvicorn.error")

# Data API router
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

# process and index background task
async def process_and_index_pipeline(
    request: Request,  # the reqeust object has the app and its data
    project_id: str,
    asset_id: str,
    file_id: str,
    db_client,
    process_request: ProcessRequest,
):

    try:
        project_model = await ProjectModel.create_instance(
            db_client=db_client
        )  # create the ProjectModel instance

        project = await project_model.get_project_or_create_one(project_id=project_id)

        chunk_size = process_request.chunk_size
        chunk_overlap = process_request.chunk_overlap
        do_reset = process_request.do_reset

        asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

        # STEP 1: Update status to PROCESSING
        _ = await asset_model.update_asset_status(asset_id, new_status= AssetStatusEnum.PROCESSING.value)

        # create Process Controller object
        process_cotroller = ProcessController(project_id=project_id)

        chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

        if do_reset == True:
            _ = await chunk_model.delete_chunks_by_project_id(project_id=project.id)

        # get file content
        file_content = process_cotroller.get_file_content(file_id)


        # get file chunks
        file_chunks = process_cotroller.process_file_content(
            file_id=file_id,
            file_content=file_content,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i + 1,
                chunk_project_id=project.id,
                chunk_asset_id=ObjectId(asset_id),
            )
            for i, chunk in enumerate(file_chunks)
        ]
        
        _ =  await chunk_model.add_many_chunks(data_chunks=file_chunks_records)

        # STEP 2: Save chunks to DB (Indexing Phase)
        await asset_model.update_asset_status(asset_id, AssetStatusEnum.IDNEXING.value)

        # nlp_controller instance

        nlp_controller = NLPController(generation_client= request.app.generation_client,
                                    embedding_client=request.app.embedding_client,
                                    vectordb_client= request.app.vectordb_client,
                                    template_parser=request.app.template_parser)
        
        # index chunks into vector db
        _ = nlp_controller.index_into_vectordb(Project=project, chunks= file_chunks_records)

        # STEP 3: Update status to SUCCESS / COMPLETED
        await asset_model.update_asset_status(asset_id, AssetStatusEnum.SUCCESS.value)

    except Exception as e:
        traceback.print_exc()
        print(f"{e}")
        # Mark as error so the UI can show the error
        await asset_model.update_asset_status(asset_id, AssetStatusEnum.ERROR.value)


# upload endpoint
@data_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,  # the reqeust object has the app and its data
    project_id: str,
    file: UploadFile,
    process_request: str = Form(...),   # received as a JSON string from multipart form
    upload_request: str = Form(...),    # received as a JSON string from multipart form
    background_tasks: BackgroundTasks = BackgroundTasks(),
    app_settings: Settings = Depends(get_settings),
):
    # Parse the JSON strings into the Pydantic models
    process_request: ProcessRequest = ProcessRequest.model_validate_json(process_request)
    upload_request: UploadRequest   = UploadRequest.model_validate_json(upload_request)

    # get projects collection or create it
    db_client = request.app.db_client  # get the db_client

    project_model = await ProjectModel.create_instance(
        db_client=db_client
    )  # create the ProjectModel instance

    project = await project_model.get_project_or_create_one(project_id=project_id)

    # Initialize data controller
    data_controller = DataController()

    # Validate uploaded file
    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": result_signal},
        )

    # Resolve project directory and file path
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path, file_id = data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id,
    )

    try:
        # Write file asynchronously in chunks
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)

    except Exception as e:
        # Log upload failure
        logger.error(f"Error while uploading file: {e}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.FILE_UPLOAD_FAILED.value},
        )

    

    # find asset type
    process_cotroller = ProcessController(project_id=project_id)
    asset_ext = process_cotroller.get_file_extension(file_id=file_id)
    asset_type = ""

    if asset_ext == ProcessingEnum.PDF.value:
        asset_type = AssetTypeEnum.PDF.value
    
    if asset_ext == ProcessingEnum.TEXT.value:
        asset_type = AssetTypeEnum.TEXT.value
    
    # create asset resource
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type= asset_type,
        asset_name=file.filename,
        asset_size=os.path.getsize(file_path),
        asset_pushed_at = datetime.now(timezone.utc),
        asset_status="",
        asset_uploader_admin_id = ObjectId(upload_request.uploader_admin_id),
        asset_uploader_admin_name = upload_request.uploader_admin_name
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)

    # 2. Trigger the background pipeline
    background_tasks.add_task(
        process_and_index_pipeline,
        request= request,
        project_id=str(project.project_id),
        asset_id=str(asset_record.id),
        file_id=file_id,
        db_client=request.app.db_client,
        process_request= process_request,
    )

    # Upload completed successfully
    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id": str(asset_record.id),
            "file_size": asset_record.asset_size,
            "file_type": asset_record.asset_type,
            "file_uploading_time": str(asset_record.asset_pushed_at)
        }
    )

@data_router.delete("/delete/{project_id}/{asset_id}")
async def delete_uploaded_file(request: Request, project_id: str, asset_id: str):
    import shutil
    import glob

    # get projects collection or create it
    db_client = request.app.db_client  # get the db_client

    project_model = await ProjectModel.create_instance(
        db_client=db_client
    )  # create the ProjectModel instance

    project = await project_model.get_project_or_create_one(project_id=project_id)

    # project not found
    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
        )
    
    # chat model instance
    asset_model = await AssetModel.create_instance(db_client)

    # get asset record first to get its info
    asset_record = await asset_model.collection.find_one({"_id": ObjectId(asset_id)})
    
    if not asset_record:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.FILE_ID_ERROR.value},
        )

    # chunk model instance
    chunk_model = await ChunkModel.create_instance(db_client)

    # get all chunks belonging to this file/asset first (to extract file path from metadata if needed)
    file_chunks = await chunk_model.get_chunks_by_asset_id(asset_id=ObjectId(asset_id))

    # delete indices of the file from Qdrant vector DB
    nlp_controller = NLPController(
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        vectordb_client=request.app.vectordb_client,
        template_parser=request.app.template_parser
    )
    
    try:
        await nlp_controller.delete_file_from_vectordb(
            Project=project,
            file_chunks=file_chunks
        )
    except Exception as e:
        logger.error(f"Error while deleting file indices from vector DB: {e}")

    # delete chunks from chunks collection
    try:
        await chunk_model.delete_chunks_by_asset_id(asset_id=ObjectId(asset_id))
    except Exception as e:
        logger.error(f"Error while deleting chunks from database: {e}")

    # delete file from filesystem
    asset_name = asset_record.get("asset_name")
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    
    file_path = None
    if file_chunks:
        first_chunk = file_chunks[0]
        file_path = first_chunk.chunk_metadata.get("file_path") or first_chunk.chunk_metadata.get("source")

    # fallback: search by name pattern in project directory if chunk metadata wasn't available
    if (not file_path or not os.path.exists(file_path)) and asset_name:
        cleaned_file_name = DataController().get_clean_file_name(orig_file_name=asset_name)
        matching_files = glob.glob(os.path.join(project_dir_path, f"*_{cleaned_file_name}"))
        if matching_files:
            file_path = matching_files[0]

    # delete the file and any associated images folder
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            # if PDF, check and remove corresponding converted images directory
            if asset_record.get("asset_type") == "pdf" or file_path.lower().endswith(".pdf"):
                pdf_dir_name = os.path.splitext(os.path.basename(file_path))[0]
                pdf_images_dir = os.path.join(project_dir_path, pdf_dir_name)
                if os.path.exists(pdf_images_dir) and os.path.isdir(pdf_images_dir):
                    shutil.rmtree(pdf_images_dir)
        except Exception as e:
            logger.error(f"Error while deleting file {file_path} from filesystem: {e}")

    # delete asset from db
    result = await asset_model.delete_asset_by_id(asset_id=asset_id)

    if not result:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.DELETE_CHAT_ERROR.value}
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"signal": ResponseSignal.DELETE_CHAT_SUCCESS.value}
    )

@data_router.get("/list/{project_id}")
async def list_uploaded_files(request: Request, project_id: str):
    
     # get projects collection or create it
    db_client = request.app.db_client  # get the db_client

    project_model = await ProjectModel.create_instance(
        db_client=db_client
    )  # create the ProjectModel instance

    project = await project_model.get_project_or_create_one(project_id=project_id)

    # project not found
    if not project:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
            )
    
    # chat model instance
    asset_model = await AssetModel.create_instance(db_client)

    # get all chats
    all_files = await asset_model.get_all_project_assets(asset_project_id = project.id)
    
    all_files = [file.model_dump() for file in all_files]

    for file in all_files:
        file["id"] = str(file["id"])
        file["asset_pushed_at"] = str(file["asset_pushed_at"])
        file["asset_uploader_admin_id"] = str(file["asset_uploader_admin_id"])
        file["asset_project_id"] = str(file["asset_project_id"])

    # return response
    if not all_files:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.LIST_CHATS_ERROR.value}
        )
    
    return JSONResponse(
        status_code= status.HTTP_200_OK,
        content={"signal": ResponseSignal.LIST_CHATS_SUCCESS.value,
                 "all_files": all_files}
    )