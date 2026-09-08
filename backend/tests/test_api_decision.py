import pytest

def test_get_decisions(client):
    response = client.get("/api/v1/decisions")
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_decision_by_id(client):
    response = client.get("/api/v1/decisions/DEC-001")
    assert response.status_code == 200
    assert response.json()["data"]["decision_id"] == "DEC-001"

def test_approve_decision(client):
    payload = {
        "approver": "user1",
        "role": "ADMIN",
        "justification": "Looks good",
        "comments": "Approved after review"
    }
    response = client.post("/api/v1/decisions/DEC-001/approve", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "APPROVED"
    assert len(data["approvals"]) == 1
    assert data["approvals"][0]["approver"] == "user1"
    assert len(data["audit_history"]) == 1

def test_reject_decision(client):
    # Need a fresh PENDING decision for rejection since DEC-001 is now APPROVED
    from app.api.dependencies import _decision_repo
    from app.domain.models.decision import Decision
    from app.domain.enums import DecisionStatus
    from datetime import datetime, timezone
    
    _decision_repo.save(Decision(
        decision_id="DEC-002",
        recommendation_id="REC-001",
        target_plan_id="PLAN-001",
        target_plan_version="1",
        status=DecisionStatus.PENDING,
        action_taken="None",
        recorded_at=datetime.now(timezone.utc)
    ))

    payload = {
        "approver": "user2",
        "role": "MANAGER",
        "reason": "Not enough budget"
    }
    response = client.post("/api/v1/decisions/DEC-002/reject", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "REJECTED"
    assert data["justification"] == "Not enough budget"
    assert len(data["audit_history"]) == 1

def test_defer_decision(client):
    from app.api.dependencies import _decision_repo
    from app.domain.models.decision import Decision
    from app.domain.enums import DecisionStatus
    from datetime import datetime, timezone
    
    _decision_repo.save(Decision(
        decision_id="DEC-003",
        recommendation_id="REC-001",
        target_plan_id="PLAN-001",
        target_plan_version="1",
        status=DecisionStatus.PENDING,
        action_taken="None",
        recorded_at=datetime.now(timezone.utc)
    ))

    payload = {
        "approver": "user3",
        "role": "ENGINEER",
        "reason": "Need more data",
        "deferUntil": "2026-10-01T00:00:00Z"
    }
    response = client.post("/api/v1/decisions/DEC-003/defer", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "DEFERRED"
    assert data["justification"] == "Need more data"
    assert len(data["audit_history"]) == 1

def test_decision_missing_plan(client):
    from app.api.dependencies import _decision_repo
    from app.domain.models.decision import Decision
    from app.domain.enums import DecisionStatus
    from datetime import datetime, timezone
    
    _decision_repo.save(Decision(
        decision_id="DEC-004",
        recommendation_id="REC-001",
        target_plan_id="PLAN-999", # Invalid plan
        target_plan_version="1",
        status=DecisionStatus.PENDING,
        action_taken="None",
        recorded_at=datetime.now(timezone.utc)
    ))

    payload = {
        "approver": "user1",
        "role": "ADMIN",
        "justification": "Looks good"
    }
    response = client.post("/api/v1/decisions/DEC-004/approve", json=payload)
    # The API returns 200 with an error object because we catch HTTPException and return ApiResponse with error
    assert response.status_code == 200
    assert "error" in response.json()
    assert response.json()["error"]["httpStatus"] == 404
    assert response.json()["error"]["message"] == "Target plan not found"
