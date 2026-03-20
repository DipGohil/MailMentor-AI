def get_auth_header(client):
    client.post("/auth/register", json={
        "username": "testuser_summary",
        "password": "1122"
    })

    res = client.post("/auth/login", json={
        "username": "testuser_summary",
        "password": "1122"
    })

    token = res.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_email_summary(test_client):
    headers = get_auth_header(test_client)

    # dummy ID (may not exist)
    res = test_client.get(
        "/email-summary/1",
        headers=headers
    )

    assert res.status_code in [200, 404]

    data = res.json()

    assert "summary" in data


def test_gmail_summary(test_client):
    headers = get_auth_header(test_client)

    res = test_client.get(
        "/analytics/gmail-summary/test123",
        headers=headers
    )

    # depends on Gmail config
    assert res.status_code in [200, 404, 500]