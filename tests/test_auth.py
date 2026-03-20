def test_register(test_client):
    response = test_client.post(
        "/auth/register",
        json={"username": "testuser_auth", "password": "1122"}
    )

    assert response.status_code in [200, 400]  # already exists case


def test_login(test_client):
    response = test_client.post(
        "/auth/login",
        json={"username": "testuser_auth", "password": "1122"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()