from abc import ABC, abstractmethod
import json
import os

import httpx

RASHIS = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]
RASHI_GUIDANCE = {
    "Mesha": ("direct initiative", "acting before the situation is fully understood"),
    "Vrishabha": ("steadiness and practical follow-through", "staying fixed after circumstances change"),
    "Mithuna": ("curiosity and communication", "scattering attention across too many possibilities"),
    "Karka": ("emotional intelligence and protection", "withdrawing instead of naming a need"),
    "Simha": ("confident self-expression", "depending too heavily on recognition"),
    "Kanya": ("discernment and preparation", "turning care into perfectionism"),
    "Tula": ("balance and relational awareness", "delaying a necessary preference"),
    "Vrishchika": ("depth and commitment", "testing trust indirectly"),
    "Dhanu": ("optimism and meaning-making", "promising beyond present capacity"),
    "Makara": ("patience and responsibility", "carrying every burden alone"),
    "Kumbha": ("independent perspective", "intellectualizing vulnerable feelings"),
    "Meena": ("intuition and empathy", "absorbing expectations that are not yours"),
}
RASHI_LORDS = {
    "Mesha": "Mars", "Vrishabha": "Venus", "Mithuna": "Mercury", "Karka": "Moon",
    "Simha": "Sun", "Kanya": "Mercury", "Tula": "Venus", "Vrishchika": "Mars",
    "Dhanu": "Jupiter", "Makara": "Saturn", "Kumbha": "Saturn", "Meena": "Jupiter",
}
HOUSE_AREAS = {
    1: "identity and self-direction", 2: "speech, values and accumulated resources",
    3: "initiative, skills and communication", 4: "home and emotional foundations",
    5: "learning, creativity and discernment", 6: "work routines, service and obstacles",
    7: "partnerships and agreements", 8: "change, vulnerability and shared resources",
    9: "beliefs, mentors and higher learning", 10: "career, responsibility and public contribution",
    11: "networks, gains and long-range aims", 12: "rest, release and life behind the scenes",
}
PERIOD_THEMES = {
    "Ketu": "simplification, detachment and a search for what still feels meaningful",
    "Venus": "relationships, values, enjoyment and creative or material refinement",
    "Sun": "visibility, authority, purpose and a clearer sense of direction",
    "Moon": "emotional needs, belonging, care and changing circumstances",
    "Mars": "initiative, competition, courage and the need to direct impatience well",
    "Rahu": "ambition, experimentation and unfamiliar experiences that can become consuming",
    "Jupiter": "learning, expansion, mentors and decisions guided by principle",
    "Saturn": "discipline, boundaries, responsibility and results built gradually",
    "Mercury": "learning, analysis, trade, communication and adaptable problem-solving",
}

ASTROTWIN_INSTRUCTIONS = (
    "You are AstroTwin, a warm Vedic astrology reflection assistant. Treat the supplied "
    "Swiss-Ephemeris Lahiri chart JSON as authoritative: never invent or alter placements. "
    "Answer the exact question using only the three to five chart factors most relevant to it; "
    "do not dump every placement. Lead with the interpretation, connect the factors into one "
    "coherent reading, and finish with two or three concrete reflection or preparation steps. "
    "Write 250 to 400 words in natural conversational plain text. Use short paragraphs and, "
    "only when useful, a short numbered list. Never use Markdown tables, headings, asterisks, "
    "pipe characters, raw JSON, or an exhaustive chart summary. Never promise outcomes or "
    "replace medical, legal, financial, emergency or mental-health professionals. State "
    "uncertainty and astrology's belief-based nature naturally, without repeating a generic disclaimer."
)


def chart_prompt(question: str, context: dict) -> str:
    chart_context = {
        "chart": context["chart"],
        "relevant_memories": context.get("memories", []),
        "relevant_events": context.get("events", []),
        "primary_focus": context.get("focus"),
        "recent_conversation": context.get("conversation_history", []),
    }
    return f"Question: {question}\n\nVerified chart and user context:\n{json.dumps(chart_context, default=str)}"

class AIProvider(ABC):
    @abstractmethod
    def generate(self, question: str, context: dict) -> str: ...

class VedicFallbackProvider(AIProvider):
    def generate(self, question: str, context: dict) -> str:
        chart = context["chart"]
        q = question.lower()
        lagna = chart["ascendant"]
        moon = next(item for item in chart["planets"] if item["name"] == "Moon")
        sun = next(item for item in chart["planets"] if item["name"] == "Sun")
        venus = next(item for item in chart["planets"] if item["name"] == "Venus")
        dasha = chart["current_mahadasha"]
        strength, watch = RASHI_GUIDANCE[lagna["rashi"]]
        dasha_planet = next(item for item in chart["planets"] if item["name"] == dasha["lord"])
        lagna_index = RASHIS.index(lagna["rashi"])

        def house_sign(number: int) -> str:
            return RASHIS[(lagna_index + number - 1) % 12]

        def placement(name: str) -> dict:
            return next(item for item in chart["planets"] if item["name"] == name)

        def ordinal(number: int) -> str:
            if 10 <= number % 100 <= 20:
                suffix = "th"
            else:
                suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
            return f"{number}{suffix}"

        anchor = (
            f"With a {lagna['rashi']} Lagna, a {moon['rashi']} Moon in {moon['nakshatra']} pada {moon['pada']}, "
            f"and a {sun['rashi']} Sun, the chart combines {strength} with a tendency toward {watch}."
        )
        if any(word in q for word in ["job", "career", "interview", "work", "placement"]):
            tenth_sign = house_sign(10)
            tenth_lord_name = RASHI_LORDS[tenth_sign]
            tenth_lord = placement(tenth_lord_name)
            interview_question = any(word in q for word in ["interview", "selection", "recruiter"])
            practical_guidance = (
                "For the interview, prepare two specific examples that show how you think, keep answers structured, and listen carefully before responding. "
                "The chart cannot guarantee the interview result, but it can identify the style of preparation worth leaning into."
                if interview_question else
                "For career growth, deepen one marketable communication or analytical skill, document visible evidence of your work, and build relationships around shared craft rather than recognition alone. "
                "Review progress through responsibilities, feedback and opportunities gained—not through astrology as a promise of promotion."
            )
            reading = (
                f" Career is read through your {tenth_sign} 10th house. Its lord {tenth_lord_name} sits in the "
                f"{ordinal(tenth_lord['house'])} house in {tenth_lord['rashi']}, connecting public contribution with "
                f"{HOUSE_AREAS[tenth_lord['house']]}. Your {dasha['lord']} mahadasha adds a period of "
                f"{PERIOD_THEMES[dasha['lord']]}; because natal {dasha['lord']} occupies the {ordinal(dasha_planet['house'])} house, "
                f"that process is especially tied to {HOUSE_AREAS[dasha_planet['house']]}. {practical_guidance}"
            )
        elif any(word in q for word in ["relationship", "partner", "marriage", "love", "dating"]):
            seventh_sign = house_sign(7)
            seventh_lord_name = RASHI_LORDS[seventh_sign]
            seventh_lord = placement(seventh_lord_name)
            reading = (
                f" Your whole-sign 7th house is {seventh_sign}, ruled by {seventh_lord_name}. That ruler sits in your "
                f"{ordinal(seventh_lord['house'])} house in {seventh_lord['rashi']}, so partnership themes become intertwined with "
                f"{HOUSE_AREAS[seventh_lord['house']]}. The Moon in {moon['nakshatra']} in the {ordinal(moon['house'])} house can seek "
                f"emotional safety through {HOUSE_AREAS[moon['house']]}, while Venus in the {ordinal(venus['house'])} house shows where "
                "affection and compromise need room. The useful pattern to test is whether you communicate a need directly or "
                "wait for the other person to infer it. Look for reciprocity and consistent behavior rather than treating the chart as a prediction about a partner."
            )
        elif any(word in q for word in ["money", "finance", "investment", "salary"]):
            second_sign, eleventh_sign = house_sign(2), house_sign(11)
            second_lord, eleventh_lord = placement(RASHI_LORDS[second_sign]), placement(RASHI_LORDS[eleventh_sign])
            reading = (
                f" Your 2nd house of savings is {second_sign}; its lord {RASHI_LORDS[second_sign]} sits in the {ordinal(second_lord['house'])} house. "
                f"Your 11th house of gains is {eleventh_sign}; its lord {RASHI_LORDS[eleventh_sign]} sits in the {ordinal(eleventh_lord['house'])} house. "
                f"During {dasha['lord']} mahadasha, favor a simple system: define a savings floor, review recurring costs and separate "
                "long-term decisions from emotional urgency. Astrology cannot predict returns or replace qualified financial advice."
            )
        elif any(word in q for word in ["mahadasha", "dasha", "current period", "this period"]):
            reading = (
                f" You are in {dasha['lord']} mahadasha, approximately {dasha['start']} to {dasha['end']}. In Vedic interpretation, "
                f"this emphasizes {PERIOD_THEMES[dasha['lord']]}. Natal {dasha['lord']} is in {dasha_planet['rashi']} in your "
                f"{ordinal(dasha_planet['house'])} house, locating the strongest lessons around {HOUSE_AREAS[dasha_planet['house']]}. "
                f"This does not mean abandoning that area; it often asks you to remove noise and become more deliberate. The constructive "
                f"expression is {strength}. The shadow expression is {watch}. Ask which commitment remains meaningful even without immediate validation."
            )
        else:
            reading = (
                f" Your current {dasha['lord']} period emphasizes {PERIOD_THEMES[dasha['lord']]}, particularly through "
                f"{HOUSE_AREAS[dasha_planet['house']]}. Use {strength} on the part you can influence now, and notice whether {watch} "
                "is shaping the question."
            )
        event_line = f" Your upcoming milestone, {context['events'][0]['title']} on {context['events'][0]['date']}, gives this reading a concrete time horizon." if context.get("events") else ""
        memory_line = f" Your saved reflection about “{context['memories'][0]['content']}” makes this less abstract: choose one action in that area and review what actually changes." if context.get("memories") else ""
        return f"{anchor} {reading}{event_line}{memory_line}"

class OpenAIResponsesProvider(AIProvider):
    def generate(self, question: str, context: dict) -> str:
        model = os.getenv("OPENAI_MODEL") or "gpt-5.6-luna"
        base_url = (os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        response = httpx.post(
            f"{base_url}/responses",
            headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"},
            json={"model": model, "instructions": ASTROTWIN_INSTRUCTIONS, "input": chart_prompt(question, context), "text": {"verbosity": "medium"}},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("output_text"):
            return payload["output_text"]
        for item in payload.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    return content["text"]
        raise RuntimeError("OpenAI response contained no text")


class GroqChatProvider(AIProvider):
    """Free-tier-friendly hosted interpretation through Groq's OpenAI-compatible API."""

    def generate(self, question: str, context: dict) -> str:
        model = os.getenv("GROQ_MODEL") or "openai/gpt-oss-120b"
        base_url = (os.getenv("GROQ_BASE_URL") or "https://api.groq.com/openai/v1").rstrip("/")
        response = httpx.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": ASTROTWIN_INSTRUCTIONS},
                    {"role": "user", "content": chart_prompt(question, context)},
                ],
                "temperature": 0.35,
                "reasoning_effort": "low",
                "reasoning_format": "hidden",
                "max_completion_tokens": 1200,
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        choices = payload.get("choices", [])
        if choices and choices[0].get("message", {}).get("content"):
            return choices[0]["message"]["content"]
        raise RuntimeError("Groq response contained no text")
