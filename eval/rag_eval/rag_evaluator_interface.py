from abc import ABC, abstractmethod

class RAGEvaluatorInterface(ABC):

    @abstractmethod
    async def context_precision_score(self, user_input, reference, retrieved_contexts):
        pass

    @abstractmethod
    async def context_recall_score(self, user_input, reference, retrieved_contexts):
        pass

    @abstractmethod
    async def faithfulness_score(self, user_input, response, retrieved_contexts):
        pass

    @abstractmethod
    async def answer_relevancy_score(self, user_input, response):
        pass

    @abstractmethod
    async def answer_correctness_score(self, user_input, response, reference):
        pass