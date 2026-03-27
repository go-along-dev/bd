import httpx
from decimal import Decimal
from app.config import settings

# ─── Shared HTTP Client ───────────────────────
_client: httpx.AsyncClient | None = None

def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            base_url="https://api.openrouteservice.org",
            timeout=10.0,
        )
    return _client

async def close_client() -> None:
    """Call on app shutdown."""
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None

async def get_route(
    src_lat: float,
    src_lng: float,
    dst_lat: float,
    dst_lng: float,
) -> dict:
    """Get route using OpenRouteService API"""
    if not settings.ORS_API_KEY:
        # Fallback to mock for local testing if API key is not set
        distance_km = round(abs(src_lat - dst_lat) * 111.32 + abs(src_lng - dst_lng) * 111.32, 2)
        return {
            "distance_km": max(distance_km, 1.0),
            "duration_minutes": max(int(distance_km * 1.5), 5),
            "geometry": "mock_encoded_polyline_xyz",
        }

    client = get_client()
    headers = {"Authorization": settings.ORS_API_KEY}
    
    # Note: ORS coordinates are in [longitude, latitude] format
    body = {
        "coordinates": [[src_lng, src_lat], [dst_lng, dst_lat]]
    }
    
    try:
        response = await client.post("/v2/directions/driving-car", json=body, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        feature = data["features"][0]
        summary = feature["properties"]["summary"]
        
        distance_meters = summary["distance"]
        duration_seconds = summary["duration"]
        
        return {
            "distance_km": round(distance_meters / 1000.0, 2),
            "duration_minutes": int(duration_seconds / 60.0),
            "geometry": feature["geometry"],
        }
    except Exception as e:
        # Fallback similarly if request fails
        distance_km = round(abs(src_lat - dst_lat) * 111.32 + abs(src_lng - dst_lng) * 111.32, 2)
        return {
            "distance_km": max(distance_km, 1.0),
            "duration_minutes": max(int(distance_km * 1.5), 5),
            "geometry": "mock_encoded_polyline_xyz",
        }

async def get_distance(
    src_lat: float,
    src_lng: float,
    dst_lat: float,
    dst_lng: float,
) -> float:
    """Get only distance from ORS"""
    route = await get_route(src_lat, src_lng, dst_lat, dst_lng)
    return route["distance_km"]

async def get_distance_matrix(
    origins: list[tuple[float, float]],
    destinations: list[tuple[float, float]],
) -> list[list[float]]:
    """
    Batch distance calculations setup via ORS matrix API
    """
    if not settings.ORS_API_KEY:
        return [[0.0] * len(destinations) for _ in origins]

    all_coords = origins + destinations
    src_indices = list(range(len(origins)))
    dst_indices = list(range(len(origins), len(origins) + len(destinations)))
    
    body = {
        "locations": [[lng, lat] for lat, lng in all_coords],
        "sources": src_indices,
        "destinations": dst_indices,
        "metrics": ["distance"],
        "units": "km"
    }

    client = get_client()
    headers = {"Authorization": settings.ORS_API_KEY}
    try:
        response = await client.post("/v2/matrix/driving-car", json=body, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        distances = data.get("distances", [])
        return [[round(d, 2) if d else 0 for d in row] for row in distances]
    except Exception:
        return [[0.0] * len(destinations) for _ in origins]
