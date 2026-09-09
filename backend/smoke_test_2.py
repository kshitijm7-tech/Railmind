import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_smoke_test():
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
    print(f"Engine E02 (Prioritize) status: {r.status_code}")
    print(f"Engine E02 (Prioritize) response: {r.text}")
    
    intel_payload = {
        "request_id": "REQ-001",
        "candidates": [],
        "context_horizon": {"start": "2026-09-09T00:00:00Z", "end": "2026-09-10T00:00:00Z"},
        "state_mode": "LIVE",
        "requested_at": "2026-09-09T00:00:00Z"
    }
    r2 = client.post("/api/v1/intelligence/evaluate", json=intel_payload)
    print(f"Engine P17 (Intelligence) status: {r2.status_code}")
    print(f"Engine P17 (Intelligence) response: {r2.text}")
    
run_smoke_test()