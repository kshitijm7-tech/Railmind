import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_simulation_workflow():
    # 1. We know P10/P11 generate PLAN-xxx, let's assume one is generated or use mock repo.
    # To be safe and deterministic, let's just trigger generate first to get a plan.
    req = {
        "horizon": {
            "start": "2026-09-09T00:00:00Z",
            "end": "2026-09-09T12:00:00Z"
        },
        "strategy": "MAINTENANCE_MAXIMIZED",
        "corridorId": "CORR-01",
        "taskIds": []
    }
    resp = client.post("/api/v1/planning/generate", json=req)
    assert resp.status_code == 202
    job = resp.json()
    
    # Extract plan_id from resultEndpoint: /api/v1/plans/PLAN-123456
    plan_id = job["resultEndpoint"].split("/")[-1]
    
    # 2. Run simulation
    sim_req = {
        "plan_id": plan_id,
        "scenario_id": "SCENARIO-TEST",
        "data_state": "MOCKED"
    }
    resp_sim = client.post("/api/v1/simulations", json=sim_req)
    assert resp_sim.status_code == 202
    sim_job = resp_sim.json()
    
    # Extract run_id
    run_id = sim_job["resultEndpoint"].split("/")[-1]
    
    # 3. Get run
    resp_run = client.get(f"/api/v1/simulations/{run_id}")
    assert resp_run.status_code == 200
    run_data = resp_run.json()["data"]
    assert run_data["status"] == "COMPLETED"
    
    # 4. Get events
    resp_events = client.get(f"/api/v1/simulations/{run_id}/events")
    assert resp_events.status_code == 200
    
    # 5. Get results
    resp_res = client.get(f"/api/v1/simulations/{run_id}/results")
    assert resp_res.status_code == 200
    assert "total_delay_minutes" in resp_res.json()["data"]

def test_simulation_not_found():
    resp = client.get("/api/v1/simulations/SIM-INVALID")
    assert resp.status_code == 404