from datetime import UTC, date, datetime
from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def now(): return datetime.now(UTC).replace(tzinfo=None)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    birth_date: Mapped[date] = mapped_column(Date)
    birth_time: Mapped[str] = mapped_column(String(20), default="12:00")
    birth_city: Mapped[str] = mapped_column(String(120), default="")
    primary_focus: Mapped[str] = mapped_column(String(80), default="Personal Growth")
    interests: Mapped[str] = mapped_column(Text, default="Personal Growth")
    notifications: Mapped[str] = mapped_column(String(20), default="daily")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

class Memory(Base):
    __tablename__ = "memories"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(40))
    content: Mapped[str] = mapped_column(Text)
    importance: Mapped[int] = mapped_column(Integer, default=3)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

class LifeEvent(Base):
    __tablename__ = "life_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text, default="")
    date: Mapped[date] = mapped_column(Date)
    category: Mapped[str] = mapped_column(String(50), default="Personal")
    importance: Mapped[int] = mapped_column(Integer, default=3)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

class ChatConversation(Base):
    __tablename__ = "chat_conversations"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(180), default="AstroTwin guidance")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    messages: Mapped[list["ChatMessage"]] = relationship(cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("chat_conversations.id"))
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

class DailyGuidance(Base):
    __tablename__ = "daily_guidance"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[date] = mapped_column(Date)
    overall_score: Mapped[int] = mapped_column(Integer)
    career_score: Mapped[int] = mapped_column(Integer)
    relationship_score: Mapped[int] = mapped_column(Integer)
    finance_score: Mapped[int] = mapped_column(Integer)
    energy_score: Mapped[int] = mapped_column(Integer)
    insight: Mapped[str] = mapped_column(Text)
    recommended_action: Mapped[str] = mapped_column(Text)

class DailyReflection(Base):
    __tablename__ = "daily_reflections"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[date] = mapped_column(Date)
    mood: Mapped[str] = mapped_column(String(20))
    resonance: Mapped[str] = mapped_column(String(20))
    notes: Mapped[str] = mapped_column(Text, default="")

class CompatibilityReport(Base):
    __tablename__ = "compatibility_reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    compatibility_type: Mapped[str] = mapped_column(String(30))
    person_a_name: Mapped[str] = mapped_column(String(120))
    person_b_name: Mapped[str] = mapped_column(String(120))
    person_b_birth_date: Mapped[date] = mapped_column(Date)
    overall_score: Mapped[int] = mapped_column(Integer)
    communication_score: Mapped[int] = mapped_column(Integer)
    emotional_score: Mapped[int] = mapped_column(Integer)
    ambition_score: Mapped[int] = mapped_column(Integer)
    decision_score: Mapped[int] = mapped_column(Integer)
    trust_score: Mapped[int] = mapped_column(Integer)
    strengths: Mapped[str] = mapped_column(Text)
    friction_points: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text)
    share_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

class Astrologer(Base):
    __tablename__ = "astrologers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    specialization: Mapped[str] = mapped_column(String(80))
    rating: Mapped[float] = mapped_column(Float)
    review_count: Mapped[int] = mapped_column(Integer)
    experience_years: Mapped[int] = mapped_column(Integer)
    price_per_minute: Mapped[int] = mapped_column(Integer)
    languages: Mapped[str] = mapped_column(String(160))
    availability: Mapped[str] = mapped_column(String(30))
    bio: Mapped[str] = mapped_column(Text)

class Consultation(Base):
    __tablename__ = "consultations"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    astrologer_id: Mapped[int] = mapped_column(ForeignKey("astrologers.id"))
    consultation_type: Mapped[str] = mapped_column(String(20))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(30), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    event_name: Mapped[str] = mapped_column(String(100), index=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
