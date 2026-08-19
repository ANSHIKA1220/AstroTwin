import httpx

KNOWN_LOCATIONS = {
    "new delhi": (28.6139, 77.2090, "Asia/Kolkata", "New Delhi, India"),
    "delhi": (28.6139, 77.2090, "Asia/Kolkata", "Delhi, India"),
    "mumbai": (19.0760, 72.8777, "Asia/Kolkata", "Mumbai, India"),
    "bengaluru": (12.9716, 77.5946, "Asia/Kolkata", "Bengaluru, India"),
    "bangalore": (12.9716, 77.5946, "Asia/Kolkata", "Bengaluru, India"),
    "kolkata": (22.5726, 88.3639, "Asia/Kolkata", "Kolkata, India"),
    "chennai": (13.0827, 80.2707, "Asia/Kolkata", "Chennai, India"),
    "hyderabad": (17.3850, 78.4867, "Asia/Kolkata", "Hyderabad, India"),
    "pune": (18.5204, 73.8567, "Asia/Kolkata", "Pune, India"),
}

def resolve_birthplace(query: str) -> dict:
    normalized = query.strip().lower().split(",")[0]
    if normalized in KNOWN_LOCATIONS:
        latitude, longitude, timezone, name = KNOWN_LOCATIONS[normalized]
        return {"latitude": latitude, "longitude": longitude, "timezone": timezone, "name": name, "source": "built-in demo-safe location index"}
    try:
        response = httpx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": query, "count": 1, "language": "en", "format": "json"},
            timeout=8,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        if results:
            item = results[0]
            label = ", ".join(x for x in [item.get("name"), item.get("admin1"), item.get("country")] if x)
            return {"latitude": item["latitude"], "longitude": item["longitude"], "timezone": item["timezone"], "name": label, "source": "Open-Meteo geocoding"}
    except (httpx.HTTPError, KeyError, ValueError):
        pass
    raise ValueError("Birthplace could not be resolved. Enter a city with state or country, for example: Jaipur, India.")
