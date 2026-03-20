def get_token(client):

    client.post(
        "/auth/register",
        json={"username": "testuser_actions", "password": "1122"}
    )

    res = client.post(
        "/auth/login",
        json={"username": "testuser_actions", "password": "1122"}
    )

    assert res.status_code == 200, res.json()

    return res.json()["access_token"]


def test_get_actions(test_client):

    token = get_token(test_client)

    response = test_client.get(
        "/actions/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert "actions" in response.json()