import json
from datetime import date

from sqlalchemy.orm import Session

from ..models import AstrologyProfile, User
from .location import resolve_birthplace
from .vedic import calculate_vedic_chart, chart_json

def ensure_astrology_profile(db: Session, user: User, force: bool = False) -> AstrologyProfile:
    profile = db.query(AstrologyProfile).filter_by(user_id=user.id).first()
    if profile and not force:
        stored = json.loads(profile.chart_json)
        if stored.get("calculated_for") == date.today().isoformat():
            return profile
        force = True
    location = resolve_birthplace(user.birth_city)
    chart = calculate_vedic_chart(
        user.birth_date,
        user.birth_time,
        location["latitude"],
        location["longitude"],
        location["timezone"],
    )
    if not profile:
        profile = AstrologyProfile(user_id=user.id)
        db.add(profile)
    profile.system = "Vedic sidereal (Lahiri)"
    profile.resolved_place = location["name"]
    profile.latitude = location["latitude"]
    profile.longitude = location["longitude"]
    profile.timezone = location["timezone"]
    profile.chart_json = chart_json(chart)
    db.flush()
    return profile

def serialize_astrology_profile(profile: AstrologyProfile) -> dict:
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "system": profile.system,
        "resolved_place": profile.resolved_place,
        "latitude": profile.latitude,
        "longitude": profile.longitude,
        "timezone": profile.timezone,
        "chart": json.loads(profile.chart_json),
        "calculated_at": profile.calculated_at,
    }
