from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.services.compatibility import generate
from app.services.cosmic_engine import stable_score

client = TestClient(app)

def test_cosmic_score_is_repeatable():
    assert stable_score("2002-03-14","career","2026-08-17") == stable_score("2002-03-14","career","2026-08-17")
def test_compatibility_is_repeatable():
    a=generate("A","2000-01-01","B","2001-02-02","Co-founder"); b=generate("A","2000-01-01","B","2001-02-02","Co-founder"); assert a==b
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

def test_validation_reflection_upsert_and_resonance_math():
    with client:
        uid=client.post("/api/demo/activate").json()["userId"]
        assert client.post(f"/api/users/{uid}/events",json={"date":"2026-08-20"}).status_code == 422
        assert client.post(f"/api/users/{uid}/memories",json={"type":"Goal","content":"x","importance":9}).status_code == 422
        before=client.get(f"/api/users/{uid}/resonance").json()["total"]
        payload={"date":"2099-01-01","mood":"Normal","resonance":"Partially"}
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
