from enum import Enum

class MyPDFLoaderEnum(Enum):
    OCR_MODEL = "google/gemini-3-flash-preview"
    BASE_URL = "https://openrouter.ai/api/v1"
    MAX_OUTPUT_TOKENS = 8192
    OCR_PROMPT = """
You are an advanced Arabic academic document parser.

Analyze the provided image or PDF page containing Arabic university-related content.

Your task:
Extract structured information and output STRICTLY valid JSON.
"""

