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

