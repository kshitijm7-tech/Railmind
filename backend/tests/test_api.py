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

def test_get_plan_detail(client):
    response = client.get("/api/v1/plans/PLAN-001")
    assert response.status_code == 200
    assert response.json()["data"]["plan_id"] == "PLAN-001"

def test_get_plan_versions(client):
    response = client.get("/api/v1/plans/PLAN-001/versions")
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_plan_metrics(client):
    response = client.get("/api/v1/plans/PLAN-001/metrics")
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_planning_candidates(client):
    response = client.get("/api/v1/planning/candidates")
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_planning_blocks(client):
    response = client.get("/api/v1/planning/blocks")
    assert response.status_code == 200
    assert "data" in response.json()

def test_generate_plan(client):
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    payload = {
        "horizon": {
            "start": now.isoformat(),
            "end": (now + timedelta(days=1)).isoformat()
        },
        "corridorId": "CORR-A",
        "strategy": "BALANCED"
    }
    response = client.post("/api/v1/planning/generate", json=payload)
    assert response.status_code == 202
    assert response.json()["status"] == "COMPLETED"
    assert "jobId" in response.json()

def test_compare_plans(client):
    payload = {
        "planIds": ["PLAN-001"]
    }
    response = client.post("/api/v1/plans/compare", json=payload)
    assert response.status_code == 200
    assert "candidates" in response.json()
