import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_smoke_test():
    print("=== LIVE HTTP SMOKE TEST ===")
    
    # 1. Health
    r = client.get("/health")
    print(f"Health: {r.status_code}")
    
    # 2. Operations (Trains)
    r = client.get("/api/v1/trains")
    print(f"Trains: {r.status_code}")
    
    # 3. Planning
    r = client.get("/api/v1/plans")
    print(f"Plans: {r.status_code}")
    
    # 4. Maintenance
    r = client.get("/api/v1/maintenance/tasks")
    print(f"Maintenance: {r.status_code}")
    
    # 5. Engine E02
    payload = {
        "taskId": "TSK-001",
        "taskType": "REPAIR",
        "assetType": "TRACK",
        "criticality": "HIGH",
        "overdueDays": 5,
        "sectionId": "SEC-01",
        "defectSeverity": "MODERATE",
        "safetyCritical": True,
        "trainImpacts": 12,
        "durationHours": 4
    }
    r = client.post("/api/v1/maintenance/prioritize", json=payload)
    print(f"Engine E02 (Prioritize): {r.status_code}")
    
    # 6. Intelligence P17
    r = client.get("/api/v1/intelligence/recommendations")
    print(f"Decision Intelligence: {r.status_code}")
    
    # 7. Recovery P18
    disruption_payload = {
        "request": {
            "request_id": "REQ-123",
            "base_plan_id": "PLAN-A",
            "requested_at": "2026-09-09T10:00:00Z",
            "disruption": {
                "disruption_id": "DIS-001",
                "type": "TRACK_FAILURE",
                "severity": "MAJOR",
                "status": "ACTIVE",
                "affected_resource": "SEC-100",
                "affected_resource_type": "SECTION",
                "start_time": "2026-09-09T09:00:00Z",
                "expected_end_time": "2026-09-09T15:00:00Z",
                "description": "Failure",
                "state_mode": "LIVE",
                "reported_at": "2026-09-09T09:05:00Z",
                "source": "SCADA",
                "provenance": {
                    "state": "LIVE",
                    "source": "SYSTEM",
                    "generatedAt": "2026-09-09T09:05:00Z",
                    "generatorVersion": "1.0"
                }
            }
        },
        "raw_context": {
            "blocks": [],
            "train_paths": []
        }
    }
    r = client.post("/api/v1/recovery/assess", json=disruption_payload)
    print(f"Recovery (P18): {r.status_code}")
    if r.status_code != 200:
        print(r.text)
        
    print("=== SMOKE TEST COMPLETE ===")

if __name__ == "__main__":
    run_smoke_test()