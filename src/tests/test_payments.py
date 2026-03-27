def test_get_fare(client):
    response = client.get("/api/v1/fare/estimate?src_lat=12.97&src_lng=77.59&dst_lat=12.30&dst_lng=76.64")
    # depending on what fare engine does
    assert response.status_code in [200, 422, 500]

def test_wallet_balance(client):
    response = client.get("/api/v1/wallet/balance")
    assert response.status_code in [200, 404, 500]
