import os
import pandas as pd
import requests
from rag_eval.RAGEvaluatorFactory import RAGEvaluatorFactory
from openai import AsyncOpenAI
from datasets import load_dataset
import asyncio
import time
from tqdm import tqdm


start_time = time.perf_counter()

datasets_entries = os.listdir("datasets")

TEST_DATA = []

for entry in datasets_entries:

    dataset = load_dataset("csv", data_files = "datasets/" + entry)
    
    for i in range(len(dataset["train"])):
        TEST_DATA.append(
            {"question": dataset["train"]["question"][i],
            "expected": dataset["train"]["expected"][i]}
    )

test_results = pd.DataFrame(TEST_DATA)

print("Dataset is created")

os.environ["OPENAI_API_KEY"] = "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"



# 2. Wrap them for Ragas
# This is the step that fixes your "AttributeError"
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENAI_API_KEY"]
)

factory = RAGEvaluatorFactory(client, "anthropic/claude-3-haiku", "openai/text-embedding-3-large")
evaluator = factory.create_evalautor_instance("ragas")


async def test_rag_api(data):
    # 2. Call your actual API route
    search_response = requests.post(
        "http://localhost:5000/api/v1/nlp/index/search/0", 
        json = {
                    "query": data["question"],
                    "limit": 10
               }
    ).json()
    
    answer_start_time = time.perf_counter()
    answer_response = requests.post(
        "http://localhost:5000/api/v1/nlp/index/answer/0", 
        json = {
                    "query": data["question"],
                    "limit": 10
               }
    ).json()

    # time to answer
    time_to_answer = time.perf_counter() - answer_start_time

    # 3. Extract the components
    
    actual_output = answer_response["answer"]
    retrieval_context = [res["text"] for res in search_response["response"][0]]

    # 4. Use RAGASEvaluator to compute metrics
    context_precision_val = await evaluator.context_precision_score(
        user_input=data["question"],
        reference=data["expected"],
        retrieved_contexts=retrieval_context
    )
    
    context_recall_val = await evaluator.context_recall_score(
        user_input=data["question"],
        reference=data["expected"],
        retrieved_contexts=retrieval_context
    )

    faithfulness_val = await evaluator.faithfulness_score(
        user_input=data["question"],
        response=actual_output,
        retrieved_contexts=retrieval_context
    )
    
    answer_relevancy_val = await evaluator.answer_relevancy_score(
        user_input=data["question"],
        response=actual_output
    )
    
    answer_correctness_val = await evaluator.answer_correctness_score(
        user_input=data["question"],
        response=actual_output,
        reference=data["expected"]
    )

    # 5. Output and Error Accumulation
    return {
        "question": data["question"],
        "expected": data["expected"],
        "retrieval context": retrieval_context,
        "answer": actual_output,
        "time to answer": time_to_answer,
        "prompt tokens": answer_response["prompt tokens"],
        "completion tokens": answer_response["completion tokens"],
        "context precision": context_precision_val,
        "context recall": context_recall_val,
        "Faithfulness": faithfulness_val,
        "Answer Relevancy": answer_relevancy_val,
        "Answer Correctness": answer_correctness_val
    }

# 5. Entry Point (Fixes the 'await' outside function error)
async def main():
    if not TEST_DATA:
        print("No data to evaluate.")
        return
        
    results_list = []
    
    # Optional: To run them one by one but correctly
    for data in tqdm(TEST_DATA):
        result = await test_rag_api(data)
        results_list.append(result)

    # Convert the list of dicts to a DataFrame all at once
    final_df = pd.DataFrame(results_list)

    # Use select_dtypes to automatically isolate numeric columns (float, int)
    numeric_df = final_df.select_dtypes(include=['number'])

    print("--- RAG Metric Averages ---")
    if not numeric_df.empty:
        for col in numeric_df.columns:

            avg = numeric_df[col].mean()
            print(f"{col} AVG = {avg}")
    
    # save test results as csv
    test_version = 5
    final_df.to_csv(f"tests/test_results_v{test_version}.csv", encoding="utf-8-sig", index=False)
    print(f"Test duration = {time.perf_counter() - start_time}")

if __name__ == "__main__":
    asyncio.run(main())
    