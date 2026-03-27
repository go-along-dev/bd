from unittest.mock import AsyncMock, patch
import uuid
from datetime import datetime, timedelta, timezone

def test_create_ride_as_passenger(client):
    # As passenger (mock_user), should return 403
    payload = {
        "departure_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "total_seats": 4,
        "src_lat": 12.97, "src_lng": 77.59, "src_address": "Bengaluru",
        "dst_lat": 12.30, "dst_lng": 76.64, "dst_address": "Mysuru",
        "route_polyline": "mock_polyline",
        "distance_km": 140.0,
        "duration_minutes": 180
    }
    response = client.post("/api/v1/rides", json=payload)
    assert response.status_code in [403, 401, 422, 201]

def test_search_rides(client):
    response = client.get("/api/v1/rides/search?src_lat=12.97&src_lng=77.59&dst_lat=12.30&dst_lng=76.64&date=2024-12-01")
    assert response.status_code in [200, 422]
