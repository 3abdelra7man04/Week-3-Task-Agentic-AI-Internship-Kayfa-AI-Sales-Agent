from ..llm_interface import LLMInterface
from openai import OpenAI
import logging
from ..llm_enums import OPENAIEnum

class OpenAIProvider(LLMInterface):
    # Constructor
    def __init__(self, api_key: str, api_url: str, input_max_characters: int = 1000,
                 generation_output_max_tokens: int = 1000, generation_temperature: float = 0.1):
        
        self.api_key = api_key
        self.api_url = api_url

        self.input_max_characters = input_max_characters
        
        self.generation_output_max_tokens = generation_output_max_tokens
        self.generation_temperature = generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(api_key= self.api_key, base_url = api_url)

        self.enums = OPENAIEnum
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
    
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
    
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
    
    def embed_text(self, text: str, document_type: str = None):
        
        # validate if there is an OpenAI client
        if not self.client:
            self.logger.error("OpenAI Client was not set")
            return None

        # validate if there is an embedding model id
        if not self.embedding_model_id:
            self.logger.error("OpenAI Embedding model was not set")
            return None

        # get response and validate it
        response = self.client.embeddings.create(input= self.process_prompt(text), model= self.embedding_model_id)

        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding :
            self.logger.error("error while embedding text using OpenAI provider")

        # return the embeddings from response
        return response.data[0].embedding
    
    
    def process_prompt(self, prompt: str):
        
        # enforce a maximumm input characters
        return prompt[:self.input_max_characters].strip()
    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_prompt(prompt)
        }

    def generate_text(self, prompt: str, chat_history: list = [],  max_output_tokens: int = None,
                     temperature: float = None):

        # validate if there is an OpenAI client
        if not self.client:
            self.logger.error("OpenAI Client was not set")
            return None

        # validate if there is a generation model id
        if not self.generation_model_id:
            self.logger.error("OpenAI generation model was not set")
            return None

        # validate the max output tokens and temperature
        max_output_tokens = max_output_tokens if max_output_tokens else self.generation_output_max_tokens
        temperature = temperature if temperature else self.generation_temperature

        # add the new user prompt to the chat history
        chat_history.append(
            self.construct_prompt(prompt=prompt, role = OPENAIEnum.USER.value)
        )

        # get response
        response = self.client.chat.completions.create(
            model= self.generation_model_id,
            messages= chat_history,
            max_tokens= max_output_tokens,
            temperature= temperature
        )

        # validate the response
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
             self.logger.error("error while generating text using OpenAI provider")
        
        generated_text = response.choices[0].message.content

        # handle usage tokens
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        
        # return the answer and tokens
        return generated_text, prompt_tokens, completion_tokens
