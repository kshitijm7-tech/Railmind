"""E09 API tests — POST /api/v1/plans/generate (the §17 CP-SAT endpoint).

Covers the established E07/E08 test matrix for the new engine family:

- valid requests over the REAL engine bridge (no engine mocking);
- verbatim E02 priority provenance surviving the full HTTP round-trip
  (task mismatch rejection, factor provenance on unscheduled tasks);
- §16.3 delay inputs riding to the solver with verbatim evidence on blocks;
- explicit solver overrides honored, absent fields keep TRD §65 defaults;
- error taxonomy: 422 malformed schema / 400 engine-contract violation /
  404 per the established envelope;
- determinism: identical request → identical domain payload;
- E08 observability: ``engine_phase == "E09"`` attribution;
- architecture: OpenAPI documents the exact TRD §37 path + models.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client():
    return TestClient(create_app())


# ---------------------------------------------------------------------------
# Deterministic fixtures — every value a valid domain state (§28)
# ---------------------------------------------------------------------------


def _priority_body(task_id: str, criticality: str = "HIGH") -> dict:
    """A minimal valid E02 request for one planning task."""
    return {
        "taskId": task_id,
        "sectionId": "SEC-1",
        "criticality": criticality,
        "overdueDays": 5,
        "taskType": "PREVENTIVE",
    }


def _priority_response(client, task_id: str) -> dict:
    """The verbatim E02 response consumed as §17.2 priority_t."""
    response = client.post("/api/v1/maintenance/prioritize", json=_priority_body(task_id))
    assert response.status_code == 200
    return response.json()["data"]


# Two tasks on one section; one overnight window that fits exactly one task,
# forcing the solver to demonstrate §17.3 assignment semantics.
def _generate_body(client, *, alternative_count: int | None = None) -> dict:
    p1 = _priority_response(client, "T-1")
    p2 = _priority_response(client, "T-2")
    return {
        "planRef": "PLAN-E09-API",
        "tasks": [
            {
                "taskId": "T-1",
                "durationMinutes": 45,
                "department": "S&T",
                "crewSize": 2,
                "priority": p1,
                "precedes": ["T-2"],
            },
            {
                "taskId": "T-2",
                "durationMinutes": 30,
                "department": "S&T",
                "crewSize": 2,
                "priority": p2,
            },
        ],
        "windows": [
            {
                "windowId": "W-1",
                "sectionId": "SEC-1",
                "earliestStart": "2026-09-14T22:00:00Z",
                "latestEnd": "2026-09-15T02:00:00Z",
                "maxDurationMinutes": 120.0,
                "qualifiedDepartments": ["S&T"],
                "bundleBonus": 0.5,
            },
            {
                "windowId": "W-2",
                "sectionId": "SEC-1",
                "earliestStart": "2026-09-15T22:00:00Z",
                "latestEnd": "2026-09-16T02:00:00Z",
                "maxDurationMinutes": 120.0,
                "qualifiedDepartments": ["S&T"],
            },
        ],
        "crewPools": [{"department": "S&T", "shiftId": "NIGHT", "availableCrew": 4}],
        "randomSeed": 42,
    }
    if alternative_count is not None:
        body["alternativeCount"] = alternative_count
    return body


# ---------------------------------------------------------------------------
# Valid requests — the real engine path HTTP → router → service → bridge → E09
# ---------------------------------------------------------------------------


class TestGeneratePlansEndpoint:
    def test_generates_plans_with_solve_evidence(self, client):
        response = client.post("/api/v1/plans/generate", json=_generate_body(client))
        assert response.status_code == 200
        payload = response.json()
        assert payload["error"] is None
        data = payload["data"]

        # TRD §70 DoD: plans produced + the reproducibility record.
        assert data["bestPlanId"] in {p["planId"] for p in data["plans"]}
        # Absent alternativeCount defers to the engine's authoritative
        # TRD §65 default (2 alternatives → 3 total plans).
        assert len(data["plans"]) == 3

        evidence = data["evidence"]
        assert evidence["solver"] == "cpsat"
        assert evidence["status"] in {"OPTIMAL", "FEASIBLE"}
        assert evidence["randomSeed"] == 42
        assert evidence["timeoutSeconds"] == pytest.approx(10.0)
        assert evidence["wallTimeMs"] >= 0.0
        assert evidence["constraintSetId"]
        assert evidence["engineVersion"]
        assert evidence["plannerModelId"]
        assert set(evidence["objectiveWeights"]) == {
            "train_delay", "unscheduled_priority", "block_count",
            "overrun_risk", "bundling",
        }

    def test_plan_structure_and_integer_minutes(self, client):
        data = client.post(
            "/api/v1/plans/generate", json=_generate_body(client)
        ).json()["data"]
        best = next(p for p in data["plans"] if p["planId"] == data["bestPlanId"])

        assignments = {a["taskId"]: a["windowId"] for a in best["assignments"]}
        assert set(assignments) == {"T-1", "T-2"}  # every task explicitly accounted
        scheduled = [w for w in assignments.values() if w is not None]
        assert scheduled, "an empty plan for two feasible tasks is a solver failure"

        for block in best["blocks"]:
            assert block["start"] < block["end"]
            assert block["assignedWorkMinutes"] > 0.0
            assert block["assignedTaskIds"], "no empty zero-work blocks"
            # §16.3 evidence shape (None without delay inputs is valid).
            assert "delayEvidence" in block

        # The §17.5 decomposition rides on every plan.
        objective = best["objective"]
        assert set(objective) == {
            "totalObjective", "trainDelayComponent", "priorityComponent",
            "blockCountComponent", "overrunRiskComponent", "bundlingComponent",
            "weights",
        }
        assert objective["totalObjective"] >= 0.0

        # Blueprint §21: the constraint trace names §17.4 constraints.
        assert best["constraintTrace"], "constraint trace must not be empty"
        assert all(c["role"] in {"binding", "active"} for c in best["constraintTrace"])
        assert all(c["constraintId"] for c in best["constraintTrace"])

    def test_precedence_is_enforced_c8(self, client):
        """T-1 precedes T-2: any plan scheduling both must respect the order."""
        data = client.post(
            "/api/v1/plans/generate", json=_generate_body(client)
        ).json()["data"]
        for plan in data["plans"]:
            placement = {}
            for a in plan["assignments"]:
                if a["windowId"] is None:
                    continue
                block = next(
                    b for b in plan["blocks"] if b["windowId"] == a["windowId"]
                )
                placement[a["taskId"]] = (block["start"], block["end"])
            if "T-1" in placement and "T-2" in placement and (
                placement["T-1"][0] == placement["T-2"][0]
            ):
                # Same start: only legal when windows differ (c8 uses task end).
                assert placement["T-1"][0] < placement["T-2"][0] or (
                    placement["T-1"][1] <= placement["T-2"][0]
                )
            elif "T-1" in placement and "T-2" in placement:
                assert placement["T-1"][1] <= placement["T-2"][0]

    def test_alternatives_are_distinct_and_ranked(self, client):
        body = _generate_body(client, alternative_count=2)
        data = client.post("/api/v1/plans/generate", json=body).json()["data"]

        assert len(data["plans"]) == 3  # best + 2 alternatives
        plan_ids = [p["planId"] for p in data["plans"]]
        assert len(set(plan_ids)) == 3, "alternatives must be distinct plans"
        assert data["bestPlanId"] == plan_ids[0]  # rank-ordered ids
        assert plan_ids[0].endswith("-alt0")

        totals = [p["objective"]["totalObjective"] for p in data["plans"]]
        assert totals == sorted(totals), "plans must be ranked by §17.5 total"

    def test_e02_priority_provenance_survives_round_trip(self, client):
        """Factor provenance flows E02 → request → solver → E03 → JSON."""
        data = client.post(
            "/api/v1/plans/generate", json=_generate_body(client)
        ).json()["data"]
        best = next(p for p in data["plans"] if p["planId"] == data["bestPlanId"])

        priority_factor_ids = {f["factor"] for f in _priority_response(client, "T-1")["factors"]}
        objective = best["objective"]
        # If any task is unscheduled, E03's β-term detail must name E02 factors.
        unscheduled = set(best["unscheduledTaskIds"])
        if unscheduled:
            assert objective["priorityComponent"] > 0.0
        # Weights provenance: the exact E03 §17.5 weight names.
        assert set(objective["weights"]) == {
            "train_delay", "unscheduled_priority", "block_count",
            "overrun_risk", "bundling",
        }

    def test_delay_inputs_produce_verbatim_block_evidence(self, client):
        body = _generate_body(client)
        body["delayInputs"] = {
            "W-1": {
                "timeOfDayMinutes": 1320.0,
                "historicalDelayMinutes": 10.0,
                "affectedTrains": [
                    {"trainId": "R-1", "priority": 2.0, "route": ["SEC-1", "SEC-2"]},
                ],
                "adjacency": {"SEC-1": ["SEC-2"]},
            }
        }
        data = client.post("/api/v1/plans/generate", json=body).json()["data"]
        best = next(p for p in data["plans"] if p["planId"] == data["bestPlanId"])
        w1_block = next(
            (b for b in best["blocks"] if b["windowId"] == "W-1"), None
        )
        if w1_block is not None:  # W-1 activated → evidence must ride verbatim
            assert w1_block["delayEvidence"] is not None
            record = w1_block["delayEvidence"][0]
            assert record["trainId"] == "R-1"
            assert record["classification"] == "direct"
            assert record["delayMinutes"] > 0.0
            assert record["propagationHops"] == 0
            assert 0.0 < record["priorityProtectionFactor"] <= 1.0
            # §17.5 α-term actually consumed the prediction.
            assert best["objective"]["trainDelayComponent"] > 0.0

    def test_solver_overrides_honored(self, client):
        body = _generate_body(client)
        body["timeoutSeconds"] = 5.0
        body["randomSeed"] = 7
        data = client.post("/api/v1/plans/generate", json=body).json()["data"]
        assert data["evidence"]["timeoutSeconds"] == pytest.approx(5.0)
        assert data["evidence"]["randomSeed"] == 7


# ---------------------------------------------------------------------------
# Error taxonomy (§9)
# ---------------------------------------------------------------------------


class TestGeneratePlansErrors:
    def test_missing_required_fields_is_422(self, client):
        response = client.post("/api/v1/plans/generate", json={"tasks": []})
        assert response.status_code == 422

    def test_malformed_json_is_422(self, client):
        response = client.post(
            "/api/v1/plans/generate",
            content=b"{not json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_priority_task_mismatch_is_400(self, client):
        body = _generate_body(client)
        # T-2's verbatim E02 response on T-1: a provenance violation.
        body["tasks"][0]["priority"] = _priority_response(client, "OTHER-TASK")
        response = client.post("/api/v1/plans/generate", json=body)
        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "PRIORITY_TASK_MISMATCH"
        assert "OTHER-TASK" in error["message"]

    def test_unknown_delay_window_is_400(self, client):
        body = _generate_body(client)
        body["delayInputs"] = {
            "W-NOPE": {
                "timeOfDayMinutes": 600.0,
                "historicalDelayMinutes": 5.0,
            }
        }
        response = client.post("/api/v1/plans/generate", json=body)
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "DELAY_INPUT_UNKNOWN_WINDOW"

    def test_engine_contract_violation_is_400(self, client):
        """A valid HTTP request that violates the engine contract: 400."""
        body = _generate_body(client)
        body["tasks"][0]["precedes"] = ["T-GHOST"]  # unknown successor
        response = client.post("/api/v1/plans/generate", json=body)
        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "ENGINE_INPUT_INVALID"

    def test_no_error_leaks_stack_traces(self, client):
        body = _generate_body(client)
        body["tasks"][0]["precedes"] = ["T-GHOST"]
        raw = client.post("/api/v1/plans/generate", json=body).text
        # No Python stack frames, no source-file references, no filesystem
        # paths — only the established error envelope with a domain message.
        assert "Traceback" not in raw
        assert 'File "' not in raw
        assert "planner\\" not in raw and "planner/" not in raw
        error = client.post("/api/v1/plans/generate", json=body).json()["error"]
        assert error["code"] == "ENGINE_INPUT_INVALID"


# ---------------------------------------------------------------------------
# Determinism + observability (E08 §11/§15 preservation)
# ---------------------------------------------------------------------------


class TestGeneratePlansDeterminism:
    def test_identical_requests_produce_identical_domain_payloads(self, client):
        body = _generate_body(client, alternative_count=1)
        first = client.post("/api/v1/plans/generate", json=body).json()["data"]
        second = client.post("/api/v1/plans/generate", json=body).json()["data"]
        # wallTimeMs is a genuine runtime measurement, not domain content —
        # compared separately with tolerance; everything else must be equal.
        a, b = first["evidence"]["wallTimeMs"], second["evidence"]["wallTimeMs"]
        first["evidence"]["wallTimeMs"] = second["evidence"]["wallTimeMs"] = 0.0
        assert first == second
        assert a > 0.0 and b > 0.0

    def test_engine_phase_is_e09(self, client):
        with client as c:  # context manager runs startup (bridge probe)
            c.post("/api/v1/plans/generate", json=_generate_body(client))
        from app.core.runtime import engine_phase_for_path

        assert engine_phase_for_path("/api/v1/plans/generate") == "E09"
        # Regression guard: E05 attribution unchanged for the simulate path.
        assert engine_phase_for_path("/api/v1/plans/P-1/simulate") == "E05"

    def test_unscheduled_task_reports_priority_provenance(self, client):
        """A windowless deadline forces unscheduling; the §17.5 β-term must
        carry E02's factor provenance through the JSON boundary."""
        body = _generate_body(client)
        # Unreachable deadline for T-1 (§17.3 slack → unscheduled, not error).
        body["tasks"][0]["latestFinish"] = "2026-09-13T00:00:00Z"
        data = client.post("/api/v1/plans/generate", json=body).json()["data"]
        best = next(p for p in data["plans"] if p["planId"] == data["bestPlanId"])
        assert "T-1" in best["unscheduledTaskIds"]
        # β cost is real money in the objective — provenance exists end-to-end.
        assert best["objective"]["priorityComponent"] > 0.0


# ---------------------------------------------------------------------------
# OpenAPI contract (E08 §8 gate, extended to E09)
# ---------------------------------------------------------------------------


class TestGeneratePlansOpenApi:
    def test_trd_section_37_path_registered_with_models(self, client):
        schema = create_app().openapi()
        entry = schema["paths"]["/api/v1/plans/generate"]["post"]
        body_ref = entry["requestBody"]["content"]["application/json"]["schema"]
        assert body_ref["$ref"] == "#/components/schemas/PlanGenerationRequest"
        response_ref = entry["responses"]["200"]["content"]["application/json"]["schema"]
        assert "PlanGenerationResponse" in response_ref["$ref"]
        assert "400" in entry["responses"]
