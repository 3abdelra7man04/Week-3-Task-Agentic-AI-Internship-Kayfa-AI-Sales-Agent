from .BaseController import BaseController
from models.db_schemes import Project
from models.db_schemes import DataChunk
from stores.llm.llm_enums import DocumentTypeEnum

class NLPController(BaseController):
    def __init__(self, generation_client, embedding_client, vectordb_client, template_parser,
                 reranking_client = None):
        super().__init__()

        self.generation_client = generation_client

        self.embedding_client = embedding_client

        self.reranking_client = reranking_client

        self.vectordb_client = vectordb_client

        self.template_parser = template_parser

    # function to create collection name
    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    
    # reset vectordb collection
    def reset_vectordb_collection(self, Project: Project):
        collection_name = self.create_collection_name(project_id=Project.project_id)

        try:
            result = self.vectordb_client.delete_collection(collection_name=collection_name)

            return result
        except Exception as e:
            print("Error Ocurred when deleting index: {e}")
            return False

       
    
    # vectordb collection info
    def get_vector_db_collection_info(self, Project: Project):
        collection_name = self.create_collection_name(project_id=Project.project_id)

        try:
            result = self.vectordb_client.get_collection_info(collection_name=collection_name)

            return result
        except Exception as e:
            print("Error Ocurred when getting index info: {e}")
            return False
    
    # vectordb indexing
    def index_into_vectordb(self, Project: Project, chunks: list[DataChunk], do_reset: bool = False):
        
        # get collcetion name
        collection_name = self.create_collection_name(project_id=Project.project_id)

        # create collection
        _ = self.vectordb_client.create_collection(collection_name = collection_name, 
                                                   embedding_size = self.embedding_client.embedding_size, do_reset = do_reset)

        # index vextors
        texts = [chunk.chunk_text for chunk in chunks]
        metadatas = [chunk.chunk_metadata for chunk in chunks]
        chunk_ids = [str(chunk.id) for chunk in chunks]

        vectors = [self.embedding_client.embed_text(text = text, document_type = DocumentTypeEnum.DOCUMENT.value)
                   for text in texts] 

        is_inserted = self.vectordb_client.insert_vectors(collection_name = collection_name, embedding_texts = texts, 
                                                embedding_vectors = vectors, metadatas = metadatas, chunk_ids = chunk_ids)

        return is_inserted

    # delete a certain file indices from vectordb
    async def delete_file_from_vectordb(self, Project: Project, file_chunks: list[DataChunk]):
        
        # get collection name
        collection_name = self.create_collection_name(project_id=Project.project_id)
        
        if not file_chunks:
            return False

        # extract chunk IDs as strings
        chunk_ids = [str(chunk.id) for chunk in file_chunks]

        # 1. delete vectors from Qdrant
        qdrant_deleted = self.vectordb_client.delete_file_indices(
            collection_name=collection_name, 
            chunk_ids=chunk_ids
        )

        return qdrant_deleted
    
    # generate an HyDE
    def generate_hypothetical_document(self, query: str):

        system_prompt = self.generation_client.construct_prompt(
                                prompt = self.template_parser.get("HyDE", "system_prompt"),
                                role = self.generation_client.enums.SYSTEM.value 
                            )
        
        document_prompt = self.template_parser.get("HyDE", "document_prompt")

        footer_prompt = self.template_parser.get("HyDE", "footer_prompt", {"query": query})

        "".join([document_prompt, footer_prompt])

        HyDE_prompt = "".join([document_prompt, footer_prompt])
        
        HyDE, HyDE_prompt_tokens, HyDE_completion_tokens = self.generation_client.generate_text(
            prompt = HyDE_prompt, chat_history = [system_prompt], 
        )

        return HyDE, HyDE_prompt_tokens, HyDE_completion_tokens

    
    def search_in_vectordb(self, Project: Project, query: str, limit: int):

        # get collection name
        collection_name = self.create_collection_name(project_id=Project.project_id)

        # embed query
        query_vector = self.embedding_client.embed_text(text = query, document_type = DocumentTypeEnum.QUERY.value)

        # get HyDE
        HyDE, HyDE_prompt_tokens, HyDE_completion_tokens = self.generate_hypothetical_document(query=query)

        # embed HyDE
        HyDE_vector = self.embedding_client.embed_text(text = query, document_type = DocumentTypeEnum.DOCUMENT.value)

        # search in vectordb
        retrieved_documents = self.vectordb_client.search_vectors(collection_name = collection_name,
                                                                  query_text = query, HyDE = HyDE,
                                                                  query_vector = query_vector, HyDE_vector = HyDE_vector,
                                                                  limit= 5*limit)

        # rerank
        reranked_documents = self.reranking_client.rerank(query = query,
                                                          documents = [document.text for document
                                                                      in retrieved_documents],
                                                          limit = limit)
        
        # return documents and tokens used while searching
        return reranked_documents, HyDE_prompt_tokens, HyDE_completion_tokens
    
    def answer_rag_questions(self, Project: Project, query: str, limit: int, chat_history: list[dict] = None):

        # retrieve documents
        retrieved_documents, search_prompt_tokens, search_completion_tokens = self.search_in_vectordb(Project=Project,
                                                                                                      query=query, limit=limit)

        if not retrieved_documents:
            return None, None, None, None, None
        
        # construct llm prompt
        ## check chat_history
        if chat_history is None or len(chat_history) == 0:
            system_prompt = self.template_parser.get("rag", "system_prompt")
            chat_history = [
                            self.generation_client.construct_prompt(
                                prompt = system_prompt,
                                role = self.generation_client.enums.SYSTEM.value 
                            )
                        ]
        
        ## add user query to chat history
        document_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                "doc_num": i+1,
                "chunk_text": document["text"]
            })
            for i, document in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt", {"query": query})

    

        full_prompt = "".join([document_prompts, footer_prompt])

        # get answer
        answer, answer_prompt_tokens, answer_completion_tokens = self.generation_client.generate_text(
            prompt = full_prompt, chat_history = chat_history, 
        )

        # update the chat history with the answer of assistant
        chat_history.append(
            self.generation_client.construct_prompt(
                prompt = answer,
                role = self.generation_client.enums.ASSISTANT.value 
            )
        )

        total_prompt_tokens = search_prompt_tokens + answer_prompt_tokens
        total_completion_tokens = search_completion_tokens + answer_completion_tokens

        return answer, full_prompt, chat_history, total_prompt_tokens, total_completion_tokens
