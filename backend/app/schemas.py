import datetime as dt
from typing import Literal
from pydantic import BaseModel, Field, field_validator

Focus = Literal["Career", "Relationships", "Finance", "Personal Growth", "Education", "Family"]
MemoryType = Literal["Profile", "Goal", "Event", "Reflection", "Conversation Insight"]
EventCategory = Literal["Career", "Education", "Relationship", "Finance", "Personal", "Family"]
Mood = Literal["Great", "Normal", "Difficult"]
ResonanceValue = Literal["Strongly", "Partially", "Not really"]
CompatibilityType = Literal["Friendship", "Relationship", "Co-founder", "Roommate", "Team"]
ConsultationType = Literal["call", "chat"]

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str | None = Field(default=None, max_length=200)
    birth_date: dt.date
    birth_time: str = Field(default="12:00", max_length=20)
    birth_city: str = Field(default="", max_length=120)
    primary_focus: Focus = "Personal Growth"
    interests: list[Focus] | str = Field(default_factory=list)
    current_focus: str = Field(default="", max_length=1000)

class SignupRequest(UserCreate):
    email: str = Field(min_length=5, max_length=200)
    password: str = Field(min_length=8, max_length=200)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("Enter a valid email address")
        return normalized

class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=200)
    password: str = Field(min_length=1, max_length=200)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    email: str | None = Field(default=None, max_length=200)
    birth_date: dt.date | None = None
    birth_time: str | None = Field(default=None, max_length=20)
    birth_city: str | None = Field(default=None, max_length=120)
    primary_focus: Focus | None = None
    interests: str | None = Field(default=None, max_length=500)
    notifications: Literal["daily", "events", "none"] | None = None

class MemoryWrite(BaseModel):
    type: MemoryType
    content: str = Field(min_length=1, max_length=2000)
    importance: int = Field(default=3, ge=1, le=5)

class EventWrite(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    description: str = Field(default="", max_length=2000)
    date: dt.date
    category: EventCategory = "Personal"
    importance: int = Field(default=3, ge=1, le=5)

class ChatRequest(BaseModel):
    user_id: int = Field(gt=0)
    question: str = Field(min_length=1, max_length=5000)
    conversation_id: int | None = Field(default=None, gt=0)

class ReflectionWrite(BaseModel):
    date: dt.date = Field(default_factory=dt.date.today)
    mood: Mood
    resonance: ResonanceValue
    notes: str = Field(default="", max_length=2000)

class CompatibilityCreate(BaseModel):
    user_id: int = Field(gt=0)
    compatibility_type: CompatibilityType
    person_b_name: str = Field(min_length=1, max_length=120)
    person_b_birth_date: dt.date
    person_b_birth_time: str = Field(default="", max_length=20)
    person_b_birth_city: str = Field(default="", max_length=120)

class ConsultationCreate(BaseModel):
    user_id: int = Field(gt=0)
    astrologer_id: int = Field(gt=0)
    consultation_type: ConsultationType
    scheduled_at: dt.datetime

class AnalyticsCreate(BaseModel):
    event_name: str = Field(min_length=1, max_length=100)
    user_id: int | None = Field(default=None, gt=0)
    metadata: dict = Field(default_factory=dict)
