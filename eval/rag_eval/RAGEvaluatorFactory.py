from .evaluators import RAGASEvaluator

class RAGEvaluatorFactory:
    
    def __init__(self, client, evaluator_llm_model: str, evaluator_embedding_model: str):
        
        self.client = client

        self.evaluator_llm_model = evaluator_llm_model

        self.evaluator_embedding_model = evaluator_embedding_model

    def create_evalautor_instance(self, evaluator: str):

        if evaluator == "ragas":
            return RAGASEvaluator(self.client, self.evaluator_llm_model, self.evaluator_embedding_model)