def get_auth_header(client):
    client.post("/auth/register", json={
        "username": "testuser_search",
        "password": "1122"
    })

    res = client.post("/auth/login", json={
        "username": "testuser_search",
        "password": "1122"
    })

    token = res.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_search_emails(test_client):
    headers = get_auth_header(test_client)

    res = test_client.get(
        "/search/?q=job",
        headers=headers
    )

    assert res.status_code == 200

    data = res.json()

    assert "answer" in data
    assert "results" in data


def test_search_empty_query(test_client):
    headers = get_auth_header(test_client)

    res = test_client.get(
        "/search/?q=",
        headers=headers
    )

    assert res.status_code == 200