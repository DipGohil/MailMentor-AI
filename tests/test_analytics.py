def get_token(client):

    # Step 1: Register (safe)
    client.post(
        "/auth/register",
        json={"username": "testuser_analytics", "password": "1122"}
    )

    # Step 2: Login
    res = client.post(
        "/auth/login",
        json={"username": "testuser_analytics", "password": "1122"}
    )

    assert res.status_code == 200, res.json()  # DEBUG LINE

    return res.json()["access_token"]

def test_analytics_protected(test_client):

    token = get_token(test_client)

    response = test_client.get(
        "/analytics/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert "total" in response.json()