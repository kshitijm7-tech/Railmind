def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200

def test_get_maintenance_tasks(client):
    response = client.get("/api/v1/maintenance/tasks?page=1&page_size=2")
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_maintenance_task_detail(client):
    response = client.get("/api/v1/maintenance/tasks/TASK-001")
    assert response.status_code == 200
    assert response.json()["data"]["task_id"] == "TASK-001"

def test_get_maintenance_defects(client):
    response = client.get("/api/v1/maintenance/defects")
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_maintenance_defect_detail(client):
    response = client.get("/api/v1/maintenance/defects/DEF-001")
    assert response.status_code == 200
    assert response.json()["data"]["defect_id"] == "DEF-001"

def test_get_infrastructure_assets(client):
    response = client.get("/api/v1/assets")
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_infrastructure_asset_detail(client):
    response = client.get("/api/v1/assets/AST-100")
    assert response.status_code == 200
    assert response.json()["data"]["asset_id"] == "AST-100"

def test_get_infrastructure_track_sections(client):
    response = client.get("/api/v1/track-sections")
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_infrastructure_corridors(client):
    response = client.get("/api/v1/corridors")
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_operations_trains(client):
    response = client.get("/api/v1/trains")
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_operations_train_paths(client):
    response = client.get("/api/v1/train-paths")
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_operations_operational_windows(client):
    response = client.get("/api/v1/operational-windows")
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_operations_train_impacts(client):
    response = client.get("/api/v1/train-impacts")
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_plans(client):
    response = client.get("/api/v1/plans?page=1&page_size=2")
    assert response.status_code == 200
    assert "data" in response.json()
