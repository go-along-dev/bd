import httpx
import math
from app.config import settings

_client: httpx.AsyncClient | None = None

def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=10.0)
    return _client

async def close_client() -> None:
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None

def _straight_line_distance(lat1, lng1, lat2, lng2) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlng/2)**2)
    return R * 2 * math.asin(math.sqrt(a))

async def get_route(
    src_lat: float, src_lng: float,
    dst_lat: float, dst_lng: float,
) -> dict:
    if not settings.ORS_API_KEY:
        distance_km = _straight_line_distance(
            src_lat, src_lng, dst_lat, dst_lng)
        return {
            "distance_km": round(distance_km, 2),
            "duration_minutes": round(distance_km * 1.5),
            "geometry": None,
        }
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        "Authorization": settings.ORS_API_KEY,
        "Content-Type": "application/json",
    }
    body = {
        "coordinates": [
            [src_lng, src_lat],
            [dst_lng, dst_lat],
        ]
    }
    try:
        client = get_client()
        response = await client.post(url, json=body, headers=headers)
        response.raise_for_status()
        data = response.json()
        route = data["routes"][0]
        summary = route["summary"]
        return {
            "distance_km": round(summary["distance"] / 1000, 2),
            "duration_minutes": round(summary["duration"] / 60),
            "geometry": route.get("geometry"),
        }
    except Exception:
        distance_km = _straight_line_distance(
            src_lat, src_lng, dst_lat, dst_lng)
        return {
            "distance_km": round(distance_km, 2),
            "duration_minutes": round(distance_km * 1.5),
            "geometry": None,
        }

async def get_distance(
    src_lat: float, src_lng: float,
    dst_lat: float, dst_lng: float,
) -> float:
    route = await get_route(src_lat, src_lng, dst_lat, dst_lng)
    return route["distance_km"]
