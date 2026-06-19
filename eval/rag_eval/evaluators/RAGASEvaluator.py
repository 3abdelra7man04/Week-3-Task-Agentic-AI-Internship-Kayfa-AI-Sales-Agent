from ..rag_evaluator_interface import RAGEvaluatorInterface
from ragas.metrics.collections import context_recall
from ragas.llms.base import llm_factory
from ragas.embeddings.base import embedding_factory
from ragas.metrics.collections import (
    AnswerCorrectness,
    AnswerRelevancy,
    Faithfulness,
    ContextPrecision,
    ContextRecall,
)

class RAGASEvaluator(RAGEvaluatorInterface):

    def __init__(self, client_instance, evaluator_llm_model: str, evaluator_embedding_model: str):

        self.evaluator_llm = llm_factory(model= evaluator_llm_model, 
                                         client = client_instance, max_tokens = 8192)

        self.evaluator_embedder = embedding_factory(model= evaluator_embedding_model,
                                                    client = client_instance)
    
    async def context_precision_score(self, user_input, reference, retrieved_contexts):
        
        
        context_precision = ContextPrecision(llm=self.evaluator_llm) 
        

        result = await context_precision.ascore(user_input= user_input,
                                        reference= reference,
                                        retrieved_contexts= retrieved_contexts)
        
        return result.value
    
    async def context_recall_score(self, user_input, reference, retrieved_contexts):
        
        context_recall = ContextRecall(llm=self.evaluator_llm) 
        

        result = await context_recall.ascore(user_input= user_input,
                                        reference= reference,
                                        retrieved_contexts= retrieved_contexts)
        
        return result.value
    
    async def faithfulness_score(self, user_input, response, retrieved_contexts):
        
        context_recall = Faithfulness(llm=self.evaluator_llm) 
        

        result = await context_recall.ascore(user_input= user_input,
                                        response= response,
                                        retrieved_contexts= retrieved_contexts)
        
        return result.value
    
    async def answer_relevancy_score(self, user_input, response):
        
        answer_relevancy = AnswerRelevancy(llm=self.evaluator_llm, embeddings=self.evaluator_embedder) 
        

        result = await answer_relevancy.ascore(user_input= user_input,
                                        response = response)
        
        return result.value
    
    async def answer_correctness_score(self, user_input, response, reference):
        
        answer_correctness = AnswerCorrectness(llm=self.evaluator_llm, embeddings=self.evaluator_embedder) 
        

        result = await answer_correctness.ascore(user_input= user_input,
                                        response = response,
                                        reference= reference)
        
        return result.value