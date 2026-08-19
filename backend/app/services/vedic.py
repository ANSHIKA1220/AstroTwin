import json
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import swisseph as swe

RASHIS = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]
WESTERN_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
DASHA_LORDS = [("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7), ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17)]
PLANETS = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS), ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER), ("Venus", swe.VENUS), ("Saturn", swe.SATURN), ("Rahu", swe.TRUE_NODE)]

def _julian_day(local_date: date, birth_time: str, timezone: str) -> tuple[float, datetime]:
    hour, minute = [int(x) for x in (birth_time or "12:00").split(":")[:2]]
    try:
        local = datetime(local_date.year, local_date.month, local_date.day, hour, minute, tzinfo=ZoneInfo(timezone))
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unsupported timezone: {timezone}") from exc
    utc = local.astimezone(UTC)
    decimal_hour = utc.hour + utc.minute / 60 + utc.second / 3600
    return swe.julday(utc.year, utc.month, utc.day, decimal_hour, swe.GREG_CAL), utc

def _placement(name: str, longitude: float, speed: float, asc_sign: int) -> dict:
    longitude %= 360
    sign_index = int(longitude // 30)
    degree = longitude % 30
    nak_index = int(longitude // (360 / 27))
    pada = int((longitude % (360 / 27)) // (360 / 108)) + 1
    return {
        "name": name,
        "longitude": round(longitude, 4),
        "rashi": RASHIS[sign_index],
        "western_sign": WESTERN_NAMES[sign_index],
        "degree": round(degree, 2),
        "house": ((sign_index - asc_sign) % 12) + 1,
        "nakshatra": NAKSHATRAS[nak_index],
        "pada": pada,
        "retrograde": speed < 0 if name not in {"Rahu", "Ketu"} else True,
    }

def _current_mahadasha(birth_date: date, moon_longitude: float, today: date) -> dict:
    segment = 360 / 27
    nak_index = int(moon_longitude // segment)
    lord_index = nak_index % 9
    lord, years = DASHA_LORDS[lord_index]
    fraction_remaining = 1 - ((moon_longitude % segment) / segment)
    cursor = datetime.combine(birth_date, datetime.min.time())
    end = cursor + timedelta(days=years * 365.2425 * fraction_remaining)
    if datetime.combine(today, datetime.min.time()) < end:
        return {"lord": lord, "start": birth_date.isoformat(), "end": end.date().isoformat(), "note": "Birth balance of Vimshottari mahadasha"}
    cursor = end
    index = (lord_index + 1) % 9
    target = datetime.combine(today, datetime.min.time())
    while True:
        current_lord, current_years = DASHA_LORDS[index]
        end = cursor + timedelta(days=current_years * 365.2425)
        if target < end:
            return {"lord": current_lord, "start": cursor.date().isoformat(), "end": end.date().isoformat(), "note": "Approximate Vimshottari mahadasha boundary"}
        cursor = end
        index = (index + 1) % 9

def calculate_vedic_chart(birth_date: date, birth_time: str, latitude: float, longitude: float, timezone: str, today: date | None = None) -> dict:
    today = today or date.today()
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd, utc_birth = _julian_day(birth_date, birth_time, timezone)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    _, ascmc = swe.houses_ex(jd, latitude, longitude, b"P", swe.FLG_SIDEREAL)
    asc_longitude = ascmc[0] % 360
    asc_sign = int(asc_longitude // 30)
    placements = []
    for name, planet_id in PLANETS:
        values, _ = swe.calc_ut(jd, planet_id, flags)
        placements.append(_placement(name, values[0], values[3], asc_sign))
    rahu = next(item for item in placements if item["name"] == "Rahu")
    placements.append(_placement("Ketu", rahu["longitude"] + 180, -1, asc_sign))
    moon = next(item for item in placements if item["name"] == "Moon")

    now = datetime(today.year, today.month, today.day, 12, tzinfo=UTC)
    transit_jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60, swe.GREG_CAL)
    transits = []
    for name, planet_id in PLANETS:
        values, _ = swe.calc_ut(transit_jd, planet_id, flags)
        transits.append(_placement(name, values[0], values[3], asc_sign))

    return {
        "system": "Vedic sidereal astrology",
        "ayanamsa": "Lahiri",
        "house_system": "Whole-sign houses from sidereal ascendant",
        "birth_utc": utc_birth.isoformat(),
        "ascendant": _placement("Lagna", asc_longitude, 0, asc_sign),
        "moon_sign": moon["rashi"],
        "sun_sign": next(item for item in placements if item["name"] == "Sun")["rashi"],
        "janma_nakshatra": {"name": moon["nakshatra"], "pada": moon["pada"]},
        "planets": placements,
        "current_mahadasha": _current_mahadasha(birth_date, moon["longitude"], today),
        "transits": transits,
        "calculated_for": today.isoformat(),
        "calculation_notice": "Planetary longitudes and ascendant are computed with Swiss Ephemeris in Lahiri sidereal mode; interpretations remain belief-based and are not scientifically validated predictions.",
    }

def chart_json(chart: dict) -> str:
    return json.dumps(chart, separators=(",", ":"))
