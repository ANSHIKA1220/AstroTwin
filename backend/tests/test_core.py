from datetime import date, timedelta
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.compatibility import generate
from app.services.cosmic_engine import stable_score
from app.services.ai.astrotwin import get_provider
from app.services.ai.provider import ASTROTWIN_INSTRUCTIONS, GroqChatProvider, VedicFallbackProvider
from app.services.vedic import calculate_vedic_chart
from app.database import normalize_database_url

client = TestClient(app)


@pytest.fixture(autouse=True)
def disable_live_ai_keys(monkeypatch):
    """Tests must never spend quota or send fixture charts to hosted providers."""
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


def test_ai_provider_uses_free_groq_then_local_fallback(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert isinstance(get_provider(), VedicFallbackProvider)
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    assert isinstance(get_provider(), GroqChatProvider)


def test_render_postgres_url_uses_psycopg_driver():
    assert normalize_database_url("postgresql://user:pass@host/db") == "postgresql+psycopg://user:pass@host/db"
    assert normalize_database_url("postgres://user:pass@host/db") == "postgresql+psycopg://user:pass@host/db"


def test_groq_provider_sends_verified_chart_context(monkeypatch):
    chart = calculate_vedic_chart(date(2002, 3, 14), "09:42", 28.6139, 77.2090, "Asia/Kolkata", date(2026, 8, 19))
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "Chart-grounded response"}}]}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["json"] = kwargs["json"]
        return FakeResponse()

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr("app.services.ai.provider.httpx.post", fake_post)
    result = GroqChatProvider().generate("What should I focus on?", {"chart": chart})
    assert result == "Chart-grounded response"
    assert captured["url"].endswith("/chat/completions")
    assert '"ayanamsa": "Lahiri"' in captured["json"]["messages"][1]["content"]
    assert captured["json"]["reasoning_effort"] == "low"
    assert captured["json"]["max_completion_tokens"] == 1200
    assert "Never use Markdown tables" in ASTROTWIN_INSTRUCTIONS


def test_local_career_growth_is_not_mistaken_for_an_interview():
    chart = calculate_vedic_chart(date(2002, 3, 14), "09:42", 28.6139, 77.2090, "Asia/Kolkata", date(2026, 8, 19))
    response = VedicFallbackProvider().generate("How am I going to grow in my career?", {"chart": chart})
    assert "For career growth" in response
    assert "For the interview" not in response
    assert all(bad not in response for bad in ["1th", "2th", "3th"])

def test_cosmic_score_is_repeatable():
    assert stable_score("2002-03-14","career","2026-08-17") == stable_score("2002-03-14","career","2026-08-17")
def test_lahiri_vedic_chart_is_calculated_from_birth_data():
    chart=calculate_vedic_chart(date(2002,3,14),"09:42",28.6139,77.2090,"Asia/Kolkata",date(2026,8,19))
    assert chart["ayanamsa"] == "Lahiri"
    assert chart["ascendant"]["rashi"] == "Vrishabha"
    assert chart["moon_sign"] == "Meena"
    assert chart["janma_nakshatra"] == {"name":"Purva Bhadrapada","pada":4}
    assert len(chart["planets"]) == 9
def test_compatibility_is_repeatable():
    a=generate("A","2000-01-01","B","2001-02-02","Co-founder"); b=generate("A","2000-01-01","B","2001-02-02","Co-founder"); assert a==b
def test_seeded_demo_stays_current_and_is_clearly_identifiable():
    with client:
        uid=client.post("/api/demo/activate").json()["userId"]
        user=client.get(f"/api/users/{uid}").json()
        dashboard=client.get(f"/api/users/{uid}/dashboard").json()
        assert user["email"] == "demo@astrotwin.local"
        assert len(dashboard["events"]) >= 3
        assert all(date.fromisoformat(event["date"]) > date.today() for event in dashboard["events"][:3])
        assert date.fromisoformat(dashboard["events"][0]["date"]) == date.today() + timedelta(days=2)
def test_memory_and_event_crud():
    with client:
        uid=client.post("/api/demo/activate").json()["userId"]
        m=client.post(f"/api/users/{uid}/memories",json={"type":"Goal","content":"Ship the prototype","importance":4}); assert m.status_code==200
        assert client.delete(f"/api/memories/{m.json()['id']}").json()["deleted"]
        e=client.post(f"/api/users/{uid}/events",json={"title":"Demo","date":"2026-08-20","category":"Career","importance":5}); assert e.status_code==200
        assert client.delete(f"/api/events/{e.json()['id']}").json()["deleted"]
def test_chat_fallback_and_consultation():
    with client:
        uid=client.post("/api/demo/activate").json()["userId"]
        r=client.post("/api/chat",json={"user_id":uid,"question":"I am unsure whether I should change jobs"}); assert r.status_code==200 and r.json()["intent"]["recommendAstrologer"]
        astro=client.get("/api/astrologers").json()[0]
        c=client.post("/api/consultations",json={"user_id":uid,"astrologer_id":astro["id"],"consultation_type":"call","scheduled_at":"2026-08-19T18:00:00"}); assert c.status_code==200
        assert client.get(f"/api/consultations/{c.json()['id']}").json()["status"] == "confirmed"

def test_chat_uses_astrology_and_only_question_relevant_context():
    with client:
        uid=client.post("/api/demo/activate").json()["userId"]
        relationship=client.post("/api/chat",json={"user_id":uid,"question":"What will my relationship be like?"}).json()
        assert relationship["astrologyBasis"]["ayanamsa"] == "Lahiri"
        assert relationship["astrologyBasis"]["lagna"] == "Vrishabha"
        assert "Vrishabha Lagna" in relationship["response"]
        assert "AstroTwin Product Review" not in relationship["response"]
        assert relationship["intent"]["specialization"] == "Relationships"
        interview=client.post("/api/chat",json={"user_id":uid,"question":"How will my upcoming interview go?"}).json()
        assert "cannot guarantee the interview result" in interview["response"]
        assert interview["contextUsed"]["events"][0]["title"] == "Software Engineering Interview"
        assert "Software Engineering Interview" in interview["response"]

def test_chat_continues_the_same_owned_conversation():
    with client:
        uid=client.post("/api/demo/activate").json()["userId"]
        first=client.post("/api/chat",json={"user_id":uid,"question":"What does my dasha emphasize?"}).json()
        second=client.post("/api/chat",json={"user_id":uid,"question":"How does that affect work?","conversation_id":first["conversationId"]}).json()
        assert second["conversationId"] == first["conversationId"]
        assert len(second["contextUsed"]["conversation_history"]) == 2
        messages=client.get(f"/api/users/{uid}/conversations").json()
        assert any(item["id"] == first["conversationId"] for item in messages)

def test_account_signup_login_logout_and_profile_isolation():
    email=f"test-{uuid.uuid4().hex}@example.com"
    payload={"name":"Test User","email":email,"password":"correct-horse-42","birth_date":"2000-01-15","birth_time":"10:30","birth_city":"New Delhi","primary_focus":"Career","interests":["Career"],"current_focus":"Preparing for an interview"}
    with TestClient(app) as first:
        assert first.get("/api/users/1").status_code == 401
        signup=first.post("/api/auth/signup",json=payload)
        assert signup.status_code == 200
        user_id=signup.json()["user"]["id"]
        assert "HttpOnly" in signup.headers["set-cookie"]
        assert first.get("/api/auth/me").json()["user"]["id"] == user_id
        chart=first.get(f"/api/users/{user_id}/astrology-profile")
        assert chart.status_code == 200 and chart.json()["chart"]["ayanamsa"] == "Lahiri"
        assert first.post("/api/auth/logout").status_code == 200
        assert first.get("/api/auth/me").status_code == 401
        assert first.post("/api/auth/login",json={"email":email,"password":"wrong-password"}).status_code == 401
        assert first.post("/api/auth/login",json={"email":email,"password":"correct-horse-42"}).status_code == 200
    with TestClient(app) as second:
        second.post("/api/demo/activate")
        assert second.get(f"/api/users/{user_id}").status_code == 403

def test_validation_reflection_upsert_and_resonance_math():
    with client:
        uid=client.post("/api/demo/activate").json()["userId"]
        assert client.post(f"/api/users/{uid}/events",json={"date":"2026-08-20"}).status_code == 422
        assert client.post(f"/api/users/{uid}/memories",json={"type":"Goal","content":"x","importance":9}).status_code == 422
        before=client.get(f"/api/users/{uid}/resonance").json()["total"]
        fresh_date=date.today() + timedelta(days=10_000 + before)
        payload={"date":fresh_date.isoformat(),"mood":"Normal","resonance":"Partially"}
        assert client.post(f"/api/users/{uid}/reflection",json=payload).status_code == 200
        payload["mood"]="Great"; payload["resonance"]="Strongly"
        assert client.post(f"/api/users/{uid}/reflection",json=payload).status_code == 200
        report=client.get(f"/api/users/{uid}/resonance").json()
        assert report["total"] == before + 1
        assert report["strong"] + report["partial"] + report["low"] == report["total"]
        expected=round((report["strong"] + report["partial"] * 0.5) / report["total"] * 100)
        assert report["score"] == expected

def test_safety_routing_avoids_astrology_recommendation():
    with client:
        uid=client.post("/api/demo/activate").json()["userId"]
        result=client.post("/api/chat",json={"user_id":uid,"question":"I have a medical emergency"}).json()
        assert result["intent"]["safety"] is True
        assert result["intent"]["recommendAstrologer"] is False
        assert "professional" in result["response"].lower()
