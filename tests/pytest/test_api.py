from api.python.app import app


def test_health_route():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "healthy"}  # Checking the JSON response
