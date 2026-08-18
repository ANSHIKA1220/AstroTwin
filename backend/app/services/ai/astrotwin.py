import os
from .provider import DemoProvider

def get_provider():
    # Provider boundary is intentionally ready for Gemini/OpenAI integration.
    # DemoProvider keeps the product complete when no API key is configured.
    return DemoProvider()

def generate_guidance(question: str, context: dict) -> str:
    return get_provider().generate(question, context)

def detect_intent(question: str) -> dict:
    q = question.lower()
    unsafe = ["self-harm", "suicide", "medical emergency", "lawsuit", "guaranteed return"]
    if any(term in q for term in unsafe):
        return {"recommendAstrologer": False, "specialization": None, "safety": True}
    mappings = {
        "Career": ["change jobs", "switch jobs", "career decision", "interview", "quit my job"],
        "Relationships": ["marriage", "relationship uncertainty", "break up", "partner"],
        "Finance": ["major financial", "investment decision", "money decision"],
    }
    for specialization, terms in mappings.items():
        if any(term in q for term in terms):
            return {"recommendAstrologer": True, "specialization": specialization, "safety": False}
    return {"recommendAstrologer": False, "specialization": None, "safety": False}

