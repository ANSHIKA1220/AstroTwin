import logging
import os
from .provider import GroqChatProvider, OpenAIResponsesProvider, VedicFallbackProvider

TOPICS = {
    "Career": ["job", "career", "interview", "work", "placement", "promotion", "project"],
    "Relationships": ["relationship", "partner", "marriage", "love", "dating", "break up"],
    "Finance": ["money", "finance", "financial", "investment", "salary"],
}
logger = logging.getLogger(__name__)

def question_topic(question: str) -> str | None:
    q = question.lower()
    for topic, terms in TOPICS.items():
        if any(term in q for term in terms):
            return topic
    return None

def prepare_context(question: str, context: dict) -> dict:
    topic = question_topic(question)
    if not topic:
        return context
    q = question.lower()
    keywords = {term for term in TOPICS[topic]}
    keywords.add(topic.lower().rstrip("s"))
    direct_terms = {term for term in keywords if term in q}
    memories = [item for item in context.get("memories", []) if any(word in item["content"].lower() or word in item["type"].lower() for word in keywords)]
    events = [item for item in context.get("events", []) if item["category"].lower().startswith(topic.lower().rstrip("s")) or any(word in item["title"].lower() for word in keywords)]
    memories.sort(key=lambda item: sum(4 for term in direct_terms if term in item["content"].lower()) + item.get("importance", 0), reverse=True)
    events.sort(key=lambda item: sum(4 for term in direct_terms if term in item["title"].lower()) + sum(1 for term in keywords if term in item["title"].lower()), reverse=True)
    return {**context, "topic": topic, "memories": memories, "events": events}

def get_provider():
    if os.getenv("GROQ_API_KEY"):
        return GroqChatProvider()
    if os.getenv("OPENAI_API_KEY"):
        return OpenAIResponsesProvider()
    return VedicFallbackProvider()

def generate_guidance(question: str, context: dict) -> tuple[str, str]:
    provider=get_provider()
    try:
        response = provider.generate(question, context)
        if isinstance(provider, GroqChatProvider):
            return response, f"groq:{os.getenv('GROQ_MODEL') or 'openai/gpt-oss-120b'}"
        if isinstance(provider, OpenAIResponsesProvider):
            return response, f"openai:{os.getenv('OPENAI_MODEL') or 'gpt-5.6-luna'}"
        return response, "local-vedic"
    except Exception as exc:
        if isinstance(provider,VedicFallbackProvider):
            raise
        logger.warning("Hosted AstroTwin provider failed; using local Vedic fallback: %s", exc)
        return VedicFallbackProvider().generate(question,context), "local-fallback"

def astrology_basis(context: dict) -> dict:
    chart=context["chart"]
    return {"system":chart["system"],"ayanamsa":chart["ayanamsa"],"lagna":chart["ascendant"]["rashi"],"moon_sign":chart["moon_sign"],"sun_sign":chart["sun_sign"],"nakshatra":chart["janma_nakshatra"]["name"],"mahadasha":chart["current_mahadasha"]["lord"]}

def detect_intent(question: str) -> dict:
    q = question.lower()
    unsafe = ["self-harm", "suicide", "medical emergency", "lawsuit", "guaranteed return"]
    if any(term in q for term in unsafe):
        return {"recommendAstrologer": False, "specialization": None, "safety": True}
    mappings = {
        "Career": ["change jobs", "switch jobs", "career decision", "interview", "quit my job"],
        "Relationships": ["marriage", "relationship", "break up", "partner", "love", "dating"],
        "Finance": ["financial", "investment", "money", "salary"],
    }
    for specialization, terms in mappings.items():
        if any(term in q for term in terms):
            return {"recommendAstrologer": True, "specialization": specialization, "safety": False}
    return {"recommendAstrologer": False, "specialization": None, "safety": False}
