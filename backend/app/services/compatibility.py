import hashlib

def _score(seed: str, label: str) -> int:
    return 62 + int(hashlib.sha256(f"{seed}|{label}".encode()).hexdigest()[:8], 16) % 33

def generate(person_a: str, birth_a: str, person_b: str, birth_b: str, kind: str) -> dict:
    seed = "|".join([person_a.strip().lower(), birth_a, person_b.strip().lower(), birth_b, kind.lower()])
    metrics = {k: _score(seed, k) for k in ["communication", "emotional", "ambition", "decision", "trust"]}
    overall = round(sum(metrics.values()) / len(metrics))
    return {"overall_score": overall, **{f"{k}_score": v for k, v in metrics.items()},
      "strengths": ["You energize each other's ideas", "Mutual respect creates room for honesty", "Shared momentum makes collaboration feel natural"],
      "friction_points": ["Different processing speeds may cause crossed signals", "Stress can make both of you protect your own priorities"],
      "recommendation": "Use this as a reflection prompt: name one shared intention and one boundary before your next important decision."}

