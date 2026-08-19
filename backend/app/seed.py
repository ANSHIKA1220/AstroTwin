from datetime import date, datetime, timedelta
from .database import Base, SessionLocal, engine
from .models import *
from .services.cosmic_engine import daily_scores
from .services.profiles import ensure_astrology_profile

ASTROLOGERS = [
 ("Mira Vashisht", "Career", 4.9, 842, 12, 35, "English, Hindi", "online", "A practical Vedic astrologer known for grounded career reflection."),
 ("Kabir Sen", "Relationships", 4.8, 611, 9, 28, "English, Hindi, Bengali", "online", "Helps clients explore communication patterns with warmth and clarity."),
 ("Tara Mehra", "Tarot", 4.9, 455, 7, 32, "English, Hindi", "offline", "Combines symbolic tarot reflection with actionable journaling prompts."),
 ("Dev Arora", "Finance", 4.7, 376, 11, 30, "English, Hindi, Punjabi", "online", "Offers reflective guidance around money habits and major decisions."),
 ("Naina Rao", "Numerology", 4.8, 529, 10, 26, "English, Hindi, Marathi", "online", "Makes numerology approachable, thoughtful, and practical."),
 ("Rohan Iyer", "Vedic Astrology", 4.9, 918, 15, 42, "English, Hindi, Tamil", "offline", "An experienced practitioner focused on long-range life themes."),
]

DEMO_EVENT_SCHEDULE = [
    ("AstroTwin Product Review", 2, "Career"),
    ("Software Engineering Interview", 5, "Career"),
    ("Project Showcase", 8, "Education"),
]

def refresh_demo_data(db, user):
    """Keep the fictional judge profile useful without touching real user data."""
    today = date.today()
    demo_titles = {title for title, _, _ in DEMO_EVENT_SCHEDULE}
    legacy_titles = {"AstroHack Submission", "Project Review"}
    demo_events = db.query(LifeEvent).filter(
        LifeEvent.user_id == user.id,
        LifeEvent.title.in_(demo_titles | legacy_titles),
    ).all()
    events_by_title = {event.title: event for event in demo_events}

    # Migrate the original fixed-date demo records without creating duplicates.
    if "AstroHack Submission" in events_by_title and "AstroTwin Product Review" not in events_by_title:
        events_by_title["AstroHack Submission"].title = "AstroTwin Product Review"
        events_by_title["AstroTwin Product Review"] = events_by_title["AstroHack Submission"]
    if "Project Review" in events_by_title and "Project Showcase" not in events_by_title:
        events_by_title["Project Review"].title = "Project Showcase"
        events_by_title["Project Showcase"] = events_by_title["Project Review"]

    for title, offset, category in DEMO_EVENT_SCHEDULE:
        event = events_by_title.get(title)
        if event:
            event.date = today + timedelta(days=offset)
            event.category = category
        else:
            db.add(LifeEvent(
                user_id=user.id,
                title=title,
                description="A fictional demo milestone used to show date-aware guidance.",
                date=today + timedelta(days=offset),
                category=category,
                importance=5,
            ))

    resonances = ["Strongly", "Partially", "Strongly", "Strongly", "Partially", "Not really"]
    for offset in range(7):
        day = today - timedelta(days=offset)
        guidance = db.query(DailyGuidance).filter_by(user_id=user.id, date=day).first()
        if not guidance:
            scores = daily_scores(user.birth_date, day)
            db.add(DailyGuidance(
                user_id=user.id,
                date=day,
                overall_score=scores["overall"],
                career_score=scores["career"],
                relationship_score=scores["relationship"],
                finance_score=scores["finance"],
                energy_score=scores["energy"],
                insight="Your momentum grows when you turn ambition into one calm, visible step.",
                recommended_action="Complete one focused 45-minute block on your most important milestone.",
            ))
        if offset > 0 and not db.query(DailyReflection).filter_by(user_id=user.id, date=day).first():
            db.add(DailyReflection(
                user_id=user.id,
                date=day,
                mood="Great" if offset % 2 == 0 else "Normal",
                resonance=resonances[offset - 1],
                notes="",
            ))

def seed_database(reset: bool = False):
    if reset:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@astrotwin.local").first()
        if not user:
            user = User(name="Anshika", email="demo@astrotwin.local", birth_date=date(2002, 3, 14), birth_time="09:42", birth_city="New Delhi", primary_focus="Career", interests="Career, Personal Growth, Education")
            db.add(user); db.flush()
            for typ, content, imp in [
                ("Goal", "Preparing for software engineering placements", 5),
                ("Event", "Working on AstroHack submission", 5),
                ("Goal", "Wants to improve interview confidence", 4),
                ("Profile", "Interested in AI product development", 4),
            ]: db.add(Memory(user_id=user.id, type=typ, content=content, importance=imp))
        refresh_demo_data(db, user)
        ensure_astrology_profile(db, user)
        if db.query(Astrologer).count() == 0:
            for row in ASTROLOGERS: db.add(Astrologer(name=row[0], specialization=row[1], rating=row[2], review_count=row[3], experience_years=row[4], price_per_minute=row[5], languages=row[6], availability=row[7], bio=row[8]))
        db.commit()
        if db.query(AnalyticsEvent).count() == 0:
            names = ["dashboard_viewed"]*24 + ["daily_reflection_completed"]*18 + ["astrotwin_question_asked"]*31 + ["compatibility_generated"]*14 + ["compatibility_shared"]*9 + ["compatibility_link_opened"]*17 + ["astrologer_recommended"]*11 + ["astrologer_profile_viewed"]*8 + ["consultation_booked"]*4
            for name in names: db.add(AnalyticsEvent(user_id=user.id, event_name=name))
            db.commit()
        return user.id
    finally: db.close()

if __name__ == "__main__":
    print(f"Seeded AstroTwin demo user #{seed_database()}")
