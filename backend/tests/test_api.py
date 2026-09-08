def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == "OK"

def test_version(client):
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data["data"]

def test_get_maintenance_tasks(client):
    response = client.get("/api/v1/maintenance/tasks?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) <= 2
    assert "pagination" in data

def test_get_plans(client):
    response = client.get("/api/v1/plans?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) <= 2
    assert "pagination" in data

def test_domain_error_handler(client):
    # To test this, we need an endpoint that raises a DomainError.
    # We can dynamically add one for testing.
    from app.main import app
    from app.core.errors import DomainError, ErrorCategory

    @app.get("/test-error")
    def trigger_error():
        raise DomainError(
            message="Test error",
            category=ErrorCategory.NOT_FOUND,
            code="TEST_NOT_FOUND"
        )
    
    response = client.get("/test-error")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "TEST_NOT_FOUND"
    assert data["error"]["message"] == "Test error"
    assert data["error"]["httpStatus"] == 404
