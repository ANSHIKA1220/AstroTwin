import json, os, uuid
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import *
from .seed import refresh_demo_data, seed_database
from .services.ai.astrotwin import astrology_basis, detect_intent, generate_guidance, prepare_context
from .services.auth import clear_session_cookie, hash_password, require_owner, require_user, set_session_cookie, verify_password
from .services.compatibility import generate as generate_match
from .services.cosmic_engine import daily_scores, vedic_daily_scores
from .services.profiles import ensure_astrology_profile, serialize_astrology_profile
from .schemas import AnalyticsCreate, ChatRequest, CompatibilityCreate, ConsultationCreate, EventWrite, LoginRequest, MemoryWrite, ReflectionWrite, SignupRequest, UserCreate, UserUpdate

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    seed_database()
    yield

app = FastAPI(title="AstroTwin API", version="1.0.0", lifespan=lifespan)
frontend_origin = os.getenv("FRONTEND_URL", "http://localhost:3000")
allowed_origins = list(dict.fromkeys([frontend_origin, "http://localhost:3000", "http://127.0.0.1:3000"]))
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def serialize(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

def track(db, name, user_id=None, metadata=None):
    db.add(AnalyticsEvent(user_id=user_id, event_name=name, metadata_json=json.dumps(metadata or {})))

def user_or_404(db: Session, user_id: int):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@app.get("/api/health")
def health():
    provider = "groq" if os.getenv("GROQ_API_KEY") else "openai" if os.getenv("OPENAI_API_KEY") else "local-vedic"
    model = os.getenv("GROQ_MODEL") if provider == "groq" else os.getenv("OPENAI_MODEL") if provider == "openai" else None
    return {"status": "ok", "mode": "hosted-ai" if provider != "local-vedic" else "local", "provider": provider, "model": model}

@app.post("/api/demo/activate")
def demo(response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == "demo@astrotwin.local").first(); refresh_demo_data(db, user); track(db, "dashboard_viewed", user.id); db.commit()
    set_session_cookie(response, user.id)
    return {"userId": user.id, "name": user.name}

@app.post("/api/auth/signup")
def signup(p: SignupRequest, response: Response, db: Session = Depends(get_db)):
    if db.query(Account).filter(func.lower(Account.email) == p.email).first():
        raise HTTPException(409, "An account with this email already exists")
    data = p.model_dump(exclude={"password"})
    user = User(
        name=data["name"], email=data["email"], birth_date=data["birth_date"], birth_time=data["birth_time"],
        birth_city=data["birth_city"], primary_focus=data["primary_focus"],
        interests=", ".join(data["interests"]) if isinstance(data["interests"], list) else data["interests"],
    )
    db.add(user); db.flush()
    db.add(Account(user_id=user.id, email=p.email, password_hash=hash_password(p.password)))
    if data.get("current_focus"):
        db.add(Memory(user_id=user.id, type="Goal", content=data["current_focus"], importance=5))
    try:
        profile = ensure_astrology_profile(db, user)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    track(db, "account_created", user.id); track(db, "onboarding_completed", user.id); db.commit()
    set_session_cookie(response, user.id)
    return {"user": serialize(user), "astrologyProfile": serialize_astrology_profile(profile)}

@app.post("/api/auth/login")
def login(p: LoginRequest, response: Response, db: Session = Depends(get_db)):
    account = db.query(Account).filter(func.lower(Account.email) == p.email).first()
    if not account or not verify_password(p.password, account.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    user = user_or_404(db, account.user_id)
    set_session_cookie(response, user.id); track(db, "signed_in", user.id); db.commit()
    return {"user": serialize(user)}

@app.post("/api/auth/logout")
def logout(response: Response):
    clear_session_cookie(response)
    return {"signedOut": True}

@app.get("/api/auth/me")
def auth_me(current_user: User = Depends(require_user), db: Session = Depends(get_db)):
    profile = db.query(AstrologyProfile).filter_by(user_id=current_user.id).first()
    return {"user": serialize(current_user), "isDemo": current_user.email == "demo@astrotwin.local", "hasAstrologyProfile": bool(profile)}

@app.post("/api/users")
def create_user(p: UserCreate, db: Session = Depends(get_db)):
    raise HTTPException(410, "Account creation moved to /api/auth/signup")

@app.get("/api/users/{user_id}")
def get_user(user_id:int, db:Session=Depends(get_db), current_user:User=Depends(require_user)):
    require_owner(user_id, current_user)
    user=db.get(User,user_id)
    if not user: raise HTTPException(404,"User not found")
    return serialize(user)

@app.put("/api/users/{user_id}")
def update_user(user_id:int,p:UserUpdate,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    require_owner(user_id, current_user)
    user=user_or_404(db,user_id)
    birth_changed=any(key in p.model_fields_set for key in {"birth_date","birth_time","birth_city"})
    for k,v in p.model_dump(exclude_unset=True).items():
        if v is not None: setattr(user,k,v)
    if birth_changed:
        try: ensure_astrology_profile(db,user,force=True)
        except ValueError as exc: raise HTTPException(422,str(exc)) from exc
    db.commit(); return serialize(user)

@app.get("/api/users/{user_id}/astrology-profile")
def astrology_profile(user_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    require_owner(user_id,current_user)
    profile=ensure_astrology_profile(db,current_user); db.commit()
    return serialize_astrology_profile(profile)

@app.get("/api/users/{user_id}/dashboard")
def dashboard(user_id:int, db:Session=Depends(get_db), current_user:User=Depends(require_user)):
    require_owner(user_id,current_user)
    user=user_or_404(db,user_id)
    profile=ensure_astrology_profile(db,user); chart=json.loads(profile.chart_json); scores=vedic_daily_scores(chart); dasha=chart["current_mahadasha"]["lord"]
    target=date.today(); guidance=db.query(DailyGuidance).filter_by(user_id=user_id,date=target).first()
    if not guidance:
        guidance=DailyGuidance(user_id=user_id,date=target,overall_score=scores["overall"],career_score=scores["career"],relationship_score=scores["relationship"],finance_score=scores["finance"],energy_score=scores["energy"],insight=f"Your Lahiri chart places today inside {dasha} mahadasha; current graha houses favor deliberate {user.primary_focus.lower()} choices over prediction.",recommended_action="Choose one action supported by evidence, then use the chart as a reflection prompt rather than a guarantee."); db.add(guidance)
    else:
        guidance.overall_score=scores["overall"]; guidance.career_score=scores["career"]; guidance.relationship_score=scores["relationship"]; guidance.finance_score=scores["finance"]; guidance.energy_score=scores["energy"]; guidance.insight=f"Your Lahiri chart places today inside {dasha} mahadasha; current graha houses favor deliberate {user.primary_focus.lower()} choices over prediction."; guidance.recommended_action="Choose one action supported by evidence, then use the chart as a reflection prompt rather than a guarantee."
    db.commit()
    focus_specialization = user.primary_focus if user.primary_focus in {"Career", "Relationships", "Finance"} else "Vedic Astrology"
    recommended = db.query(Astrologer).filter(Astrologer.specialization == focus_specialization).order_by(Astrologer.availability.desc()).first() or db.query(Astrologer).first()
    reflection = db.query(DailyReflection).filter_by(user_id=user_id, date=target).first()
    upcoming = db.query(LifeEvent).filter(LifeEvent.user_id==user_id, LifeEvent.date>=target).order_by(LifeEvent.date).limit(5).all()
    return {"user":serialize(user),"guidance":serialize(guidance),"memories":[serialize(x) for x in db.query(Memory).filter_by(user_id=user_id).order_by(Memory.importance.desc()).limit(5)],"events":[serialize(x) for x in upcoming],"reflection":serialize(reflection) if reflection else None,"recommended_astrologer":serialize(recommended) if recommended else None}

@app.get("/api/users/{user_id}/memories")
def memories(user_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    require_owner(user_id,current_user); return [serialize(x) for x in db.query(Memory).filter_by(user_id=user_id).order_by(Memory.importance.desc()).all()]
@app.post("/api/users/{user_id}/memories")
def add_memory(user_id:int,p:MemoryWrite,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    require_owner(user_id,current_user)
    user_or_404(db,user_id); x=Memory(user_id=user_id,**p.model_dump()); db.add(x); db.commit(); db.refresh(x); return serialize(x)
@app.put("/api/memories/{item_id}")
def edit_memory(item_id:int,p:MemoryWrite,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    x=db.get(Memory,item_id)
    if not x: raise HTTPException(404,"Memory not found")
    require_owner(x.user_id,current_user)
    for k,v in p.model_dump(exclude_unset=True).items(): setattr(x,k,v)
    db.commit(); return serialize(x)
@app.delete("/api/memories/{item_id}")
def delete_memory(item_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    x=db.get(Memory,item_id)
    if not x: raise HTTPException(404,"Memory not found")
    require_owner(x.user_id,current_user)
    db.delete(x); db.commit(); return {"deleted":True}

@app.get("/api/users/{user_id}/events")
def events(user_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    require_owner(user_id,current_user); return [serialize(x) for x in db.query(LifeEvent).filter_by(user_id=user_id).order_by(LifeEvent.date).all()]
@app.post("/api/users/{user_id}/events")
def add_event(user_id:int,p:EventWrite,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    require_owner(user_id,current_user)
    user_or_404(db,user_id); x=LifeEvent(user_id=user_id,**p.model_dump()); db.add(x); track(db,"life_event_created",user_id); db.commit(); db.refresh(x); return serialize(x)
@app.put("/api/events/{item_id}")
def edit_event(item_id:int,p:EventWrite,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    x=db.get(LifeEvent,item_id)
    if not x: raise HTTPException(404,"Event not found")
    require_owner(x.user_id,current_user)
    for k,v in p.model_dump().items(): setattr(x,k,v)
    db.commit(); return serialize(x)
@app.delete("/api/events/{item_id}")
def delete_event(item_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    x=db.get(LifeEvent,item_id)
    if not x: raise HTTPException(404,"Event not found")
    require_owner(x.user_id,current_user)
    db.delete(x); db.commit(); return {"deleted":True}

@app.post("/api/chat")
def chat(p:ChatRequest,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    require_owner(p.user_id,current_user)
    user=user_or_404(db,p.user_id)
    memories=db.query(Memory).filter_by(user_id=user.id).order_by(Memory.importance.desc()).limit(6).all(); upcoming=db.query(LifeEvent).filter(LifeEvent.user_id==user.id,LifeEvent.date>=date.today()).order_by(LifeEvent.date).limit(4).all()
    vedic_profile=ensure_astrology_profile(db,user)
    conversation = None
    history = []
    if p.conversation_id:
        conversation = db.get(ChatConversation, p.conversation_id)
        if not conversation: raise HTTPException(404, "Conversation not found")
        require_owner(conversation.user_id, current_user)
        prior = db.query(ChatMessage).filter_by(conversation_id=conversation.id).order_by(ChatMessage.created_at.desc()).limit(8).all()
        history = [{"role": item.role, "content": item.content} for item in reversed(prior)]
    context=prepare_context(p.question,{"focus":user.primary_focus,"profile":{"birth_date":str(user.birth_date),"birth_time":user.birth_time,"birth_city":user.birth_city},"chart":json.loads(vedic_profile.chart_json),"memories":[serialize(x) for x in memories],"events":[serialize(x) for x in upcoming],"conversation_history":history}); intent=detect_intent(p.question)
    if intent["safety"]:
        response="This question may need qualified, immediate support rather than astrology-based guidance. Please contact the appropriate medical, legal, financial, emergency, or mental-health professional. If anyone is in immediate danger, contact local emergency services now."
        provider="safety-routing"
    else:
        response, provider = generate_guidance(p.question,context)
    if not conversation:
        conversation=ChatConversation(user_id=user.id,title=p.question[:80]); db.add(conversation); db.flush()
    db.add_all([ChatMessage(conversation_id=conversation.id,role="user",content=p.question),ChatMessage(conversation_id=conversation.id,role="assistant",content=response)]); track(db,"astrotwin_question_asked",user.id,{"provider":provider})
    if intent["recommendAstrologer"]: track(db,"astrologer_recommended",user.id,{"specialization":intent["specialization"]})
    db.commit(); return {"conversationId":conversation.id,"response":response,"provider":provider,"memoryCount":len(context["memories"]),"contextUsed":context,"astrologyBasis":astrology_basis(context),"intent":intent}

@app.get("/api/users/{user_id}/conversations")
def conversations(user_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    require_owner(user_id,current_user); return [serialize(x) for x in db.query(ChatConversation).filter_by(user_id=user_id).order_by(ChatConversation.created_at.desc()).all()]
@app.get("/api/users/{user_id}/daily")
def daily(user_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    board=dashboard(user_id,db,current_user); history=db.query(DailyGuidance).filter_by(user_id=user_id).order_by(DailyGuidance.date.desc()).limit(7).all(); return {**board,"history":[serialize(x) for x in reversed(history)]}
@app.post("/api/users/{user_id}/reflection")
def reflection(user_id:int,p:ReflectionWrite,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    require_owner(user_id,current_user)
    user_or_404(db,user_id); target=p.date; x=db.query(DailyReflection).filter_by(user_id=user_id,date=target).first()
    if x: x.mood=p.mood; x.resonance=p.resonance; x.notes=p.notes
    else: x=DailyReflection(user_id=user_id,date=target,mood=p.mood,resonance=p.resonance,notes=p.notes); db.add(x)
    track(db,"daily_reflection_completed",user_id); db.commit(); return serialize(x)
@app.get("/api/users/{user_id}/resonance")
def resonance(user_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    require_owner(user_id,current_user)
    rows=db.query(DailyReflection).filter_by(user_id=user_id).order_by(DailyReflection.date).all(); counts={k:sum(1 for x in rows if x.resonance==k) for k in ["Strongly","Partially","Not really"]}; total=len(rows); score=round((counts["Strongly"]+counts["Partially"]*.5)/total*100) if total else 0
    guidance_by_date={g.date:g for g in db.query(DailyGuidance).filter_by(user_id=user_id).all()}; weights={"Strongly":1.0,"Partially":0.5,"Not really":0.0}; fields={"Career":"career_score","Relationships":"relationship_score","Finance":"finance_score","Energy":"energy_score"}; categories={}
    for label, field in fields.items():
        values=[getattr(guidance_by_date[x.date],field)*weights[x.resonance] for x in rows if x.date in guidance_by_date]
        categories[label]=round(sum(values)/len(values)) if values else 0
    return {"total":total,"strong":counts["Strongly"],"partial":counts["Partially"],"low":counts["Not really"],"score":score,"trend":[{"date":x.date,"value":100 if x.resonance=="Strongly" else 50 if x.resonance=="Partially" else 0} for x in rows[-30:]],"categories":categories,"category_basis":"Guidance scores weighted by stored reflection resonance"}

@app.post("/api/compatibility")
def compatibility(p:CompatibilityCreate,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    require_owner(p.user_id,current_user)
    user=user_or_404(db,p.user_id); result=generate_match(user.name,str(user.birth_date),p.person_b_name,str(p.person_b_birth_date),p.compatibility_type); share=uuid.uuid4().hex[:10]
    x=CompatibilityReport(user_id=user.id,compatibility_type=p.compatibility_type,person_a_name=user.name,person_b_name=p.person_b_name,person_b_birth_date=p.person_b_birth_date,share_id=share,strengths=json.dumps(result.pop("strengths")),friction_points=json.dumps(result.pop("friction_points")),recommendation=result.pop("recommendation"),**result); db.add(x); track(db,"compatibility_generated",user.id); db.commit(); db.refresh(x); return {**serialize(x),"strengths":json.loads(x.strengths),"friction_points":json.loads(x.friction_points)}
def report_payload(x): return {**serialize(x),"strengths":json.loads(x.strengths),"friction_points":json.loads(x.friction_points)}
@app.get("/api/compatibility/{item_id}")
def get_compatibility(item_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    x=db.get(CompatibilityReport,item_id)
    if not x: raise HTTPException(404,"Report not found")
    require_owner(x.user_id,current_user)
    return report_payload(x)
@app.get("/api/compatibility/share/{share_id}")
def shared_compatibility(share_id:str,db:Session=Depends(get_db)):
    x=db.query(CompatibilityReport).filter_by(share_id=share_id).first()
    if not x: raise HTTPException(404,"Report not found")
    track(db,"compatibility_link_opened",x.user_id); db.commit(); return report_payload(x)
@app.post("/api/compatibility/{item_id}/shared")
def shared(item_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    x=db.get(CompatibilityReport,item_id)
    if not x: raise HTTPException(404,"Report not found")
    require_owner(x.user_id,current_user)
    track(db,"compatibility_shared",x.user_id); db.commit(); return {"tracked":True}

@app.get("/api/astrologers")
def astrologers(specialization:str|None=None,language:str|None=None,availability:str|None=None,db:Session=Depends(get_db)):
    q=db.query(Astrologer)
    if specialization: q=q.filter(Astrologer.specialization==specialization)
    if availability: q=q.filter(Astrologer.availability==availability)
    rows=q.all(); return [serialize(x) for x in rows if not language or language.lower() in x.languages.lower()]
@app.get("/api/astrologers/{item_id}")
def astrologer(item_id:int,db:Session=Depends(get_db)):
    x=db.get(Astrologer,item_id)
    if not x: raise HTTPException(404,"Astrologer not found")
    return serialize(x)
@app.post("/api/consultations")
def consultation(p:ConsultationCreate,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    require_owner(p.user_id,current_user)
    user_or_404(db,p.user_id)
    if not db.get(Astrologer,p.astrologer_id): raise HTTPException(404,"Astrologer not found")
    x=Consultation(user_id=p.user_id,astrologer_id=p.astrologer_id,consultation_type=p.consultation_type,scheduled_at=p.scheduled_at,status="confirmed"); db.add(x); track(db,"consultation_booked",p.user_id); db.commit(); db.refresh(x); return serialize(x)
@app.get("/api/consultations/{item_id}")
def get_consultation(item_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    x=db.get(Consultation,item_id)
    if not x: raise HTTPException(404,"Consultation not found")
    require_owner(x.user_id,current_user)
    return serialize(x)
@app.get("/api/users/{user_id}/consultations")
def consultations(user_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    require_owner(user_id,current_user); return [serialize(x) for x in db.query(Consultation).filter_by(user_id=user_id).all()]
@app.post("/api/analytics/event")
def analytics_event(p:AnalyticsCreate,db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    if p.user_id is not None: require_owner(p.user_id,current_user)
    track(db,p.event_name,p.user_id,p.metadata); db.commit(); return {"tracked":True}
@app.get("/api/admin/analytics")
def analytics(db:Session=Depends(get_db),current_user:User=Depends(require_user)):
    counts=dict(db.query(AnalyticsEvent.event_name,func.count()).group_by(AnalyticsEvent.event_name).all()); users=db.query(User).count(); rec=counts.get("astrologer_recommended",0); booked=counts.get("consultation_booked",0)
    stored_reflections=db.query(DailyReflection).count()
    return {"total_users":users,"daily_reflections":stored_reflections,"questions":counts.get("astrotwin_question_asked",0),"compatibility_reports":counts.get("compatibility_generated",0),"shares":counts.get("compatibility_shared",0),"recommendations":rec,"bookings":booked,"conversion_rate":round(booked/rec*100) if rec else 0,"events":counts,"data_mode":"Illustrative seeded assumptions + live prototype events","metrics":{"d1_retention":68,"d7_retention":41,"daily_opens":124,"questions_per_user":3.4,"memories_per_user":5.2,"invites_per_user":1.6,"invite_conversion":0.28,"viral_coefficient":0.45}}
