from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run():
    plan_req = {
        "horizon": {"start": "2026-09-10T00:00:00Z", "end": "2026-09-11T00:00:00Z"},
        "corridorId": "CORR-A",
        "strategy": "BALANCED"
    }
    res = client.post("/api/v1/planning/generate", json=plan_req)
    plan_id = res.json()["resultEndpoint"].split("/")[-1]
    
    rec = {
        "request": {
            "request_id": "req-r-1",
            "base_plan_id": plan_id,
            "requested_at": "2026-09-10T12:00:00Z",
            "disruption": {
                "disruption_id": "D-1",
                "disruption_type": "TRACK_FAULT",
                "status": "ACTIVE",
                "severity": "HIGH",
                "estimated_duration_minutes": 120,
                "section_id": "S1",
                "reported_at": "2026-09-10T11:00:00Z"
            }
        }
    }
    r = client.post("/api/v1/recovery/assess", json=rec)
    print("Recovery P18:", r.status_code)
    print(r.text)

if __name__ == "__main__":
    run()