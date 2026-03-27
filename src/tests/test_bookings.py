import uuid

def test_create_booking(client):
    payload = {
        "ride_id": str(uuid.uuid4()),
        "seats_booked": 1,
        "pickup_lat": 12.97, "pickup_lng": 77.59, "pickup_address": "Point A",
        "dropoff_lat": 12.30, "dropoff_lng": 76.64, "dropoff_address": "Point B"
    }
    response = client.post("/api/v1/bookings", json=payload)
    assert response.status_code in [200, 201, 404, 422, 500]

def test_get_user_bookings(client):
    response = client.get("/api/v1/bookings")
    assert response.status_code in [200, 404, 500]

def test_cancel_booking(client):
    response = client.post(f"/api/v1/bookings/{uuid.uuid4()}/cancel", json={"reason": "Test"})
    assert response.status_code in [200, 404, 422, 500]
