from datetime import date, datetime, timedelta
from .database import Base, SessionLocal, engine
from .models import *
from .services.cosmic_engine import daily_scores

ASTROLOGERS = [
 ("Mira Vashisht", "Career", 4.9, 842, 12, 35, "English, Hindi", "online", "A practical Vedic astrologer known for grounded career reflection."),
 ("Kabir Sen", "Relationships", 4.8, 611, 9, 28, "English, Hindi, Bengali", "online", "Helps clients explore communication patterns with warmth and clarity."),
 ("Tara Mehra", "Tarot", 4.9, 455, 7, 32, "English, Hindi", "offline", "Combines symbolic tarot reflection with actionable journaling prompts."),
 ("Dev Arora", "Finance", 4.7, 376, 11, 30, "English, Hindi, Punjabi", "online", "Offers reflective guidance around money habits and major decisions."),
 ("Naina Rao", "Numerology", 4.8, 529, 10, 26, "English, Hindi, Marathi", "online", "Makes numerology approachable, thoughtful, and practical."),
 ("Rohan Iyer", "Vedic Astrology", 4.9, 918, 15, 42, "English, Hindi, Tamil", "offline", "An experienced practitioner focused on long-range life themes."),
]

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
            for title, d, category in [
                ("AstroHack Submission", date(2026, 8, 20), "Career"),
                ("Software Engineering Interview", date(2026, 8, 24), "Career"),
                ("Project Review", date(2026, 8, 27), "Education"),
            ]: db.add(LifeEvent(user_id=user.id, title=title, description="A meaningful milestone worth preparing for with intention.", date=d, category=category, importance=5))
            resonances = ["Strongly", "Partially", "Strongly", "Strongly", "Partially", "Not really"]
            for offset in range(7):
                day = date(2026, 8, 17) - timedelta(days=offset)
                s = daily_scores(user.birth_date, day)
                db.add(DailyGuidance(user_id=user.id, date=day, overall_score=s["overall"], career_score=s["career"], relationship_score=s["relationship"], finance_score=s["finance"], energy_score=s["energy"], insight="Your momentum grows when you turn ambition into one calm, visible step.", recommended_action="Complete one focused 45-minute block on your most important milestone."))
                if offset > 0:
                    resonance = resonances[offset - 1]
                    db.add(DailyReflection(user_id=user.id, date=day, mood="Great" if offset % 2 == 0 else "Normal", resonance=resonance, notes=""))
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
