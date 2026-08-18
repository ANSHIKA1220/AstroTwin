from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def generate(self, question: str, context: dict) -> str: ...

class DemoProvider(AIProvider):
    def generate(self, question: str, context: dict) -> str:
        focus = context.get("focus", "personal growth")
        events = context.get("events", [])
        memories = context.get("memories", [])
        q = question.lower()
        lead = "Your strongest signal this week is to choose deliberate progress over urgency."
        if any(word in q for word in ["job", "career", "interview", "work"]):
            lead = "Your career energy favors preparation, clear choices, and conversations that reveal what you truly value."
        elif any(word in q for word in ["relationship", "partner", "marriage"]):
            lead = "This is a useful moment to trade assumptions for a calm, direct conversation."
        event_line = f" With {events[0]['title']} approaching on {events[0]['date']}, protect one focused block for the highest-leverage task." if events else ""
        memory_line = f" You have been {memories[0]['content'].lower()}, so build from that momentum instead of restarting." if memories else ""
        return f"{lead}{event_line}{memory_line} Keep this guidance reflective: write down the next decision you can make with confidence, and leave the rest for later."

