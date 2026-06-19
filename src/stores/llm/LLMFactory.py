from .llm_enums import LLMEnums
from .providers import OpenAIProvider, CoHereProvider

class LLMFactory:
    def __init__(self, settings: dict):
        self.settings = settings
    
    def create_provider_instance(self, provider_name: str):

        # open ai
        if provider_name == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key= self.settings.OPENAI_API_KEY,
                api_url= self.settings.OPENAI_API_URL,
                input_max_characters= self.settings.INPUT_MAX_CHARACTERS,
                generation_output_max_tokens= self.settings.GENERATION_OUTPUT_MAX_TOKENS,
                generation_temperature= self.settings.GENERATION_TEMPERATURE
            )
        
        # cohere
        if provider_name == LLMEnums.COHERE.value:
            return CoHereProvider(
                api_key= self.settings.COHERE_API_KEY,
                input_max_characters= self.settings.INPUT_MAX_CHARACTERS,
                generation_output_max_tokens= self.settings.GENERATION_OUTPUT_MAX_TOKENS,
                generation_temperature= self.settings.GENERATION_TEMPERATURE
            )

        return None
    