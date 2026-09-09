"""Railway operational dataset foundation tests (spec §20).

Covers the new operational endpoints, query filters, dataset validation,
and the dataset → E09 planning → E05 simulation chain on canonical
synthetic data (data/railway_demo/).

SYNTHETIC DATA: all IDs below are demonstration scenario data, not live
Indian Railways operations.
"""


def test_dataset_validation():
    from app.infrastructure.railway_demo.loader import get_demo_dataset
    from app.infrastructure.railway_demo.validate import check_counts, validate_dataset

    dataset = get_demo_dataset()
    assert validate_dataset(dataset) == []
    assert check_counts(dataset) == []


def test_dataset_counts(client):
    assert client.get("/api/v1/stations?page_size=50").json()["pagination"]["totalItems"] == 6
    assert client.get("/api/v1/sections?page_size=50").json()["pagination"]["totalItems"] == 8
    assert client.get("/api/v1/trains?page_size=50").json()["pagination"]["totalItems"] == 12
    assert client.get("/api/v1/train-movements?page_size=50").json()["pagination"]["totalItems"] == 3
    assert client.get("/api/v1/assets?page_size=50").json()["pagination"]["totalItems"] == 5
    assert client.get("/api/v1/maintenance/tasks?page_size=50").json()["pagination"]["totalItems"] == 5
    assert client.get("/api/v1/disruptions?page_size=50").json()["pagination"]["totalItems"] == 2


def test_stations_endpoint(client):
    response = client.get("/api/v1/stations/ANP")
    assert response.status_code == 404  # lookup is by station_id, not code
    response = client.get("/api/v1/stations/STN-A")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["code"] == "ANP"
    assert data["name"] == "Anandpur"
    assert data["is_junction"] is True


def test_sections_endpoint(client):
    response = client.get("/api/v1/sections/SEC-06")
    assert response.status_code == 200
    assert response.json()["data"]["section_type"] == "Freight_Bypass"
    response = client.get("/api/v1/sections/SEC-01")
    assert response.json()["data"]["headway_min"] == 8
    # Canonical alias agrees with the legacy track-sections route.
    legacy = client.get("/api/v1/track-sections?page_size=50").json()
    assert legacy["pagination"]["totalItems"] == 8


def test_train_detail_endpoint(client):
    response = client.get("/api/v1/trains/TRN-12001")
    assert response.status_code == 200
    service = response.json()["data"]["service"]
    assert service["train_number"] == "12001"
    assert response.json()["data"]["priority"] == 1


def test_train_filters(client):
    running = client.get("/api/v1/trains?status=RUNNING&page_size=50").json()
    assert running["pagination"]["totalItems"] == 2
    freight = client.get("/api/v1/trains?train_type=FREIGHT&page_size=50").json()
    assert freight["pagination"]["totalItems"] == 3
    premium = client.get("/api/v1/trains?priority=1&page_size=50").json()
    assert premium["pagination"]["totalItems"] == 2


def test_movements_endpoint(client):
    response = client.get("/api/v1/train-movements?section_id=SEC-02&page_size=50").json()
    assert response["pagination"]["totalItems"] == 2
    occupied = client.get("/api/v1/train-movements?status=OCCUPIED&page_size=50").json()
    assert occupied["pagination"]["totalItems"] == 2


def test_maintenance_filter(client):
    response = client.get("/api/v1/maintenance/tasks?section_id=SEC-03&page_size=50").json()
    assert response["pagination"]["totalItems"] == 1
    assert response["data"][0]["task_id"] == "TSK-001"


def test_disruptions_endpoint(client):
    response = client.get("/api/v1/disruptions/SCN-OVERRUN-01")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["section_id"] == "SEC-03"
    assert data["related_task_id"] == "TSK-001"
    high = client.get("/api/v1/disruptions?severity=HIGH").json()
    assert high["pagination"]["totalItems"] == 1


def test_dataset_to_planning_to_simulation_chain(client):
    """dataset → E09 planning → E05 simulation on canonical demo task IDs."""
    plan_req = {
        "horizon": {
            "start": "2026-09-10T00:00:00+05:30",
            "end": "2026-09-10T12:00:00+05:30",
        },
        "strategy": "MAINTENANCE_MAXIMIZED",
        "corridorId": "C-07",
        "taskIds": ["TSK-001", "TSK-002"],
    }
    plan_resp = client.post("/api/v1/planning/generate", json=plan_req)
    assert plan_resp.status_code == 202
    plan_id = plan_resp.json()["resultEndpoint"].split("/")[-1]

    sim_resp = client.post(
        "/api/v1/simulations",
        json={"plan_id": plan_id, "scenario_id": "SCN-OVERRUN-01", "data_state": "MOCKED"},
    )
    assert sim_resp.status_code == 202
    run_id = sim_resp.json()["resultEndpoint"].split("/")[-1]

    run = client.get(f"/api/v1/simulations/{run_id}").json()["data"]
    assert run["status"] == "COMPLETED"
    results = client.get(f"/api/v1/simulations/{run_id}/results").json()["data"]
    assert "total_delay_minutes" in results
