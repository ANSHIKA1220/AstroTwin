import hashlib
from datetime import date

def stable_score(birth_date: date | str, category: str, current_date: date | str) -> int:
    seed = f"{birth_date}|{category.lower()}|{current_date}"
    digest = hashlib.sha256(seed.encode()).hexdigest()
    return 55 + (int(digest[:8], 16) % 40)

def daily_scores(birth_date: date | str, current_date: date | str) -> dict[str, int]:
    values = {k: stable_score(birth_date, k, current_date) for k in ["career", "relationship", "finance", "energy"]}
    values["overall"] = round(sum(values.values()) / 4)
    return values

def vedic_daily_scores(chart: dict) -> dict[str, int]:
    """Create transparent reflection scores from actual sidereal transit houses."""
    transits = {item["name"]: item for item in chart["transits"]}
    supportive = {1: 5, 2: 4, 3: 3, 5: 5, 7: 3, 9: 6, 10: 6, 11: 7}
    challenging = {6: -2, 8: -5, 12: -4}

    def category(names: list[str]) -> int:
        adjustments = [supportive.get(transits[name]["house"], challenging.get(transits[name]["house"], 0)) for name in names]
        retrograde_adjustment = sum(-1 for name in names if transits[name].get("retrograde"))
        return max(45, min(90, round(66 + sum(adjustments) / len(adjustments) * 3 + retrograde_adjustment)))

    values = {
        "career": category(["Sun", "Saturn", "Jupiter"]),
        "relationship": category(["Moon", "Venus", "Jupiter"]),
        "finance": category(["Mercury", "Venus", "Jupiter"]),
        "energy": category(["Sun", "Moon", "Mars"]),
    }
    values["overall"] = round(sum(values.values()) / 4)
    return values
