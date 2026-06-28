import streamlit as st
# from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes import DataChunk, Asset
from bson.objectid import ObjectId
from controllers.NLPController import NLPController
from utils.components import page_header, get_base64_image, page_footer

# ─── resources ──────────────────────────────────────

resources = st.session_state.resources
settings = resources["settings"]
db = resources["db"]
agent = resources["agent_client"]
template_parser = resources["template_parser"]
generation_client = resources["generation_client"]
embedding_client = resources["embedding_client"]
vectordb_client = resources["vectordb_client"]
reranking_client = resources["reranking_client"]

logo_base64 = get_base64_image("kayfa logo.svg")

page_header(logo_base64, "Upload File Knowledge Base")

st.title("📄 Upload File Knowledge Base")


# Create the file uploader widget
uploaded_file = st.file_uploader(
    label="Upload your Markdown file",
    type=["md", "txt"] # Restrict allowed file extensions
)

if uploaded_file is not None:
    # Read the file content as bytes, then decode to string
    file_content = uploaded_file.read().decode("utf-8")

    asset_model = AssetModel.create_instance(db_client=db)

    asset = Asset(
        asset_name=uploaded_file.name,
        asset_content=file_content
    )

    asset_model.add_asset(asset)
    st.success(f"Successfully uploaded: {uploaded_file.name}")
    # Optional: Preview the uploaded content in an expander box

    with st.expander("Preview File Content"):

        st.code(file_content, language="markdown")

    # ─── chunk the file ──────────────────────────────────────
    headers_to_split_on = [
    ("#", "Title"),    # Top level titles
    ("##", "Section"),   # Section titles
    ("###", "Sub-section"),  # Sub-sections
    ]

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False  # Keep the actual header text inside the chunk content
    )

    file_chunks = splitter.split_text(file_content)

    # ─── upload chunks in db ──────────────────────────────────────
    chunk_model = ChunkModel.create_instance(db_client=db)

    file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i + 1,
                chunk_project_id= ObjectId("69a43aa4981750e5e930a456"),
                chunk_asset_id= ObjectId("69a43aa4981750e5e930a456"),
            )
            for i, chunk in enumerate(file_chunks)
        ]

    _ =  chunk_model.add_many_chunks(data_chunks=file_chunks_records)

    # ─── index chunks in vector db ──────────────────────────────────────
    nlp_controller = NLPController(generation_client= generation_client,
                                    embedding_client= embedding_client,
                                    vectordb_client= vectordb_client,
                                    template_parser=template_parser,
                                    reranking_client=reranking_client)
    
    is_inserted = nlp_controller.index_into_vectordb(collection_id = "Kayfa_Sales_Agent_" + uploaded_file.name.split(".")[0], chunks = file_chunks_records)
    
    if is_inserted:
        st.success(f"Successfully indexed: {uploaded_file.name}")

    

page_footer(logo_base64)