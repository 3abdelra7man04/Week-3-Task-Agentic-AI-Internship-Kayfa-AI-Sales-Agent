from ..llm_interface import LLMInterface
from ..llm_enums import CoHereEnum, DocumentTypeEnum
import cohere
import logging

class CoHereProvider(LLMInterface):

    # constructor
    def __init__(self, api_key: str, input_max_characters: int = 1000,
                 generation_output_max_tokens: int = 1000, generation_temperature: float = 0.1):
        
        self.api_key = api_key

        self.input_max_characters = input_max_characters
        
        self.generation_output_max_tokens = generation_output_max_tokens
        self.generation_temperature = generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(api_key= self.api_key)

        self.enums = CoHereEnum
        
        self.logger = logging.getLogger(__name__)
    
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
    
    def set_reranking_model(self, model_id: str):
        self.reranking_model_id = model_id
    
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
    
    def embed_text(self, text: str, document_type: str = None):
        
        # validate if there is an OpenAI client
        if not self.client:
            self.logger.error("CoHere Client was not set")
            return None

        # validate if there is an embedding model id
        if not self.embedding_model_id:
            self.logger.error("CoHere Embedding model was not set")
            return None

        # set input type
        input_type = CoHereEnum.DOCUMENT.value
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = CoHereEnum.QUERY.value

        # get response and validate it
        response = self.client.embed(
            model = self.embedding_model_id,
            texts = [self.process_prompt(text)],
            input_type = input_type,
            embedding_types=['float'],
        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text with CoHere")
            return None
        
        # return the response after validation
        return response.embeddings.float[0]
    
    def rerank(self, query: str, documents: list, limit: int):
        # validate if there is an cohere client
        if not self.client:
            self.logger.error("CoHere Client was not set")
            return None

        # validate if there is a reranking model id
        if not self.reranking_model_id:
            self.logger.error("CoHere Reranking model was not set")
            return None

        # get response and validate it
        response = self.client.rerank(
            model = self.reranking_model_id,
            documents = documents,
            query = query,
            top_n= limit
        )

        if not response or not response.results:
            self.logger.error("Error while reranking documents with CoHere")
            return None
        
        ranked_results = []
        for res in response.results:
            ranked_results.append({
                "text": documents[res.index],  # Use index to find the text
                "score": res.relevance_score   
            })
        
        # return the reranked documents
        return ranked_results
    
    def process_prompt(self, prompt: str):
        
        # enforce a maximumm input characters
        return prompt[:self.input_max_characters].strip()
    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": self.process_prompt(prompt)
        }

    def generate_text(self, prompt: str, chat_history: list = [],  max_output_tokens: int = None,
                     temperature: float = None):

        # validate if there is an OpenAI client
        if not self.client:
            self.logger.error("CoHere Client was not set")
            return None

        # validate if there is a generation model id
        if not self.generation_model_id:
            self.logger.error("CoHere generation model was not set")
            return None
        
        # validate the max output tokens and temperature
        max_output_tokens = max_output_tokens if max_output_tokens else self.generation_output_max_tokens
        temperature = temperature if temperature else self.generation_temperature

        # get response
        response = self.client.chat(
            model= self.generation_model_id,
            chat_history = chat_history,
            message= self.process_prompt(prompt),
            max_tokens= max_output_tokens,
            temperature= temperature
        )

        # validate the response
        if not response or not response.text:
             self.logger.error("error while generating text using CoHere provider")
        
        # handle usage tokens
        prompt_tokens = response.meta.tokens.input_tokens
        completion_tokens = response.meta.tokens.output_tokens

        # return the resposne
        return response.text, prompt_tokens, completion_tokens
