"""E07 API tests — the engine intelligence endpoints (TRD §37 families).

Covers the prompt §19 matrix: valid requests, malformed requests, error
mapping (400/404/422), provenance preservation (E02/E05/E06 identity through
JSON), E05 seed/iteration pass-through, E06 honest algorithm labeling, and
determinism across repeated calls.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# Request payloads (deterministic fixtures)
# ---------------------------------------------------------------------------

PRIORITY_BODY = {
    "taskId": "T-100",
    "sectionId": "SEC-002",
    "criticality": "CRITICAL",
    "overdueDays": 10,
    "taskType": "EMERGENCY",
}

SIMULATE_BODY = {
    "windows": [
        {
            "windowId": "W1",
            "sectionId": "SEC-A",
            "earliestStart": "2026-09-14T22:00:00Z",
            "latestEnd": "2026-09-15T02:00:00Z",
            "maxDurationMinutes": 78.0,
            "taskBands": [
                {"taskId": "T1", "p10Minutes": 30.0, "p90Minutes": 50.0},
                {"taskId": "T2", "p10Minutes": 5.0, "p90Minutes": 15.0},
            ],
        }
    ],
    "iterations": 50,
    "seed": 7,
}

DURATION_BODY = {
    "taskId": "T-9",
    "taskType": "CORRECTIVE",
    "department": "S&T",
    "assetType": "SIGNAL",
    "sectionCriticality": "HIGH",
    "crewSize": 2,
    "historicalDurationMinutes": 90.0,
    "timeOfDayMinutes": 120.0,
    "daysSinceLastSimilarTask": 30.0,
}

FAILURE_BODY = {
    "assetId": "A-1",
    "assetAgeDays": 4000.0,
    "assetType": "SWITCH",
    "maintenanceHistory": 6,
    "failureHistory": 3,
    "criticality": "HIGH",
    "daysSinceLastService": 200.0,
    "taskBacklog": 4,
    "conditionScore": 55.0,
}


# ---------------------------------------------------------------------------
# POST /api/v1/maintenance/prioritize (E02)
# ---------------------------------------------------------------------------


class TestPrioritizeEndpoint:
    def test_valid_request_returns_full_explainability(self, client):
        response = client.post("/api/v1/maintenance/prioritize", json=PRIORITY_BODY)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["taskId"] == "T-100"
        assert 0.0 <= data["priorityScore"] <= 1.0
        assert data["priorityClass"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        # Full E02 explainability survives the boundary (prompt §9).
        assert len(data["factors"]) == 3  # criticality + overdue + safety
        assert {f["factor"] for f in data["factors"]} == {
            "criticality", "overdue", "safety",
        }
        for factor in data["factors"]:
            assert factor["contribution"] == pytest.approx(
                factor["normalizedScore"] * factor["weight"]
            )
        assert data["explanation"]
        assert data["missingFactors"] == ["failure_risk", "downstream_impact"]
        assert data["missingDataPolicy"] == "EXCLUDE_FACTOR"

    def test_provenance_preserved_through_json(self, client):
        response = client.post("/api/v1/maintenance/prioritize", json=PRIORITY_BODY)
        data = response.json()["data"]
        assert data["priorityModelId"] == "railmind-deterministic-priority"
        assert data["priorityModelVersion"] == "1.0.0"
        assert data["engineVersion"] == "0.1.0"

    def test_optional_failure_risk_factor_included_when_supplied(self, client):
        body = {
            **PRIORITY_BODY,
            "failureRisk": {
                "probabilityOfFailure": 0.9,
                "timeHorizonHours": 720.0,
                "modelId": "some-risk-model",
                "modelVersion": "2.0.0",
            },
        }
        response = client.post("/api/v1/maintenance/prioritize", json=body)
        assert response.status_code == 200
        factors = response.json()["data"]["factors"]
        assert {f["factor"] for f in factors} == {
            "criticality", "overdue", "safety", "failure_risk",
        }

    def test_invalid_criticality_is_400_not_silent(self, client):
        response = client.post(
            "/api/v1/maintenance/prioritize",
            json={**PRIORITY_BODY, "criticality": "URGENT"},
        )
        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "INVALID_CRITICALITY"
        assert "LOW|MEDIUM|HIGH|CRITICAL" in error["message"]

    def test_negative_overdue_days_is_422(self, client):
        """Shape violation (ge=0) rejects at the schema boundary (422) —
        the taxonomy: 422 = request shape, 400 = engine contract semantics."""
        response = client.post(
            "/api/v1/maintenance/prioritize",
            json={**PRIORITY_BODY, "overdueDays": -5},
        )
        assert response.status_code == 422

    def test_probability_out_of_range_is_422_not_clamped(self, client):
        """§11: probability > 1 is rejected loudly at the schema boundary
        (range constraint → 422), never clamped to 1."""
        response = client.post(
            "/api/v1/maintenance/prioritize",
            json={
                **PRIORITY_BODY,
                "failureRisk": {"probabilityOfFailure": 1.5},
            },
        )
        assert response.status_code == 422

    def test_missing_required_field_is_422(self, client):
        response = client.post(
            "/api/v1/maintenance/prioritize",
            json={"taskId": "T-1", "criticality": "HIGH"},
        )
        assert response.status_code == 422

    def test_score_matches_the_engine_exactly(self, client):
        """Delegation proof: the API result equals a direct E02 evaluation."""
        from app.engine_adapter.service import EngineIntegrationService
        from engine import PriorityEngine, PriorityInput

        response = client.post("/api/v1/maintenance/prioritize", json=PRIORITY_BODY)
        api_score = response.json()["data"]["priorityScore"]

        direct = PriorityEngine().evaluate(
            PriorityInput(
                task_id="T-100",
                section_id="SEC-002",
                criticality="CRITICAL",
                overdue_days=10,
                task_type="EMERGENCY",
            )
        )
        assert api_score == pytest.approx(direct.score)

    def test_repeated_calls_are_deterministic(self, client):
        a = client.post("/api/v1/maintenance/prioritize", json=PRIORITY_BODY).json()["data"]
        b = client.post("/api/v1/maintenance/prioritize", json=PRIORITY_BODY).json()["data"]
        # meta differs (timestamps); the domain payload is byte-identical.
        a.pop("explanation")  # explanation is deterministic too — keep it simple
        b.pop("explanation")
        assert a == b


# ---------------------------------------------------------------------------
# POST /api/v1/plans/{plan_id}/simulate + /scenarios/{id}/simulate (E05)
# ---------------------------------------------------------------------------


class TestSimulateEndpoints:
    def test_plan_simulate_returns_full_evidence(self, client):
        response = client.post("/api/v1/plans/PLAN-042/simulate", json=SIMULATE_BODY)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["candidateId"] == "PLAN-042"  # §14 candidate association
        assert data["iterations"] == 50
        assert data["seed"] == 7
        assert data["distribution"] == "UNIFORM"
        assert 0.0 <= data["planViolationProbability"] <= 1.0
        assert set(data["constraintExceedances"]) == {
            "c6_duration_feasibility", "c7_window_bounds",
        }
        block = data["blocks"][0]
        assert block["windowId"] == "W1"
        assert block["sectionId"] == "SEC-A"
        assert 0.0 <= block["probabilityOverrun"] <= 1.0
        assert block["p10TotalDuration"] <= block["expectedTotalDuration"] <= block["p90TotalDuration"]
        assert set(block["violationDraws"]) <= set(range(50))

    def test_seed_and_iterations_preserved_exactly(self, client):
        """§13: the caller's seed/iterations pass through untouched."""
        body = {**SIMULATE_BODY, "iterations": 13, "seed": 999}
        response = client.post("/api/v1/plans/P/simulate", json=body)
        data = response.json()["data"]
        assert data["seed"] == 999
        assert data["iterations"] == 13

    def test_defaults_pass_through_when_omitted(self, client):
        body = {"windows": SIMULATE_BODY["windows"]}
        response = client.post("/api/v1/plans/P/simulate", json=body)
        data = response.json()["data"]
        assert data["iterations"] == 200  # authoritative E05 default
        assert data["seed"] == 0

    def test_same_seed_is_reproducible(self, client):
        a = client.post("/api/v1/plans/P/simulate", json=SIMULATE_BODY).json()["data"]
        b = client.post("/api/v1/plans/P/simulate", json=SIMULATE_BODY).json()["data"]
        assert a == b

    def test_scenario_id_becomes_candidate_id(self, client):
        response = client.post(
            "/api/v1/scenarios/SC-77/simulate", json=SIMULATE_BODY
        )
        assert response.status_code == 200
        assert response.json()["data"]["candidateId"] == "SC-77"

    def test_scenario_without_windows_is_422(self, client):
        """min_length=1 on windows rejects at the schema boundary (422)."""
        response = client.post(
            "/api/v1/scenarios/SC-1/simulate", json={"windows": []}
        )
        assert response.status_code == 422

    def test_inverted_bands_are_400_not_reordered(self, client):
        """§24: the engine refuses p10 > p90; the backend surfaces it as 400."""
        body = {
            "windows": [
                {
                    **SIMULATE_BODY["windows"][0],
                    "taskBands": [
                        {"taskId": "T1", "p10Minutes": 50.0, "p90Minutes": 30.0}
                    ],
                }
            ]
        }
        response = client.post("/api/v1/plans/P/simulate", json=body)
        assert response.status_code == 400
        assert "p10" in response.json()["error"]["message"].lower()

    def test_missing_task_bands_is_400_never_fabricated(self, client):
        body = {
            "windows": [
                {**SIMULATE_BODY["windows"][0], "taskBands": []}
            ]
        }
        response = client.post("/api/v1/plans/P/simulate", json=body)
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "MISSING_TASK_BANDS"

    def test_provenance_preserved_through_json(self, client):
        response = client.post("/api/v1/plans/P/simulate", json=SIMULATE_BODY)
        data = response.json()["data"]
        assert data["simulationModelId"] == "railmind-monte-carlo-robustness"
        assert data["simulationModelVersion"] == "1.0.0"
        assert data["engineVersion"] == "0.1.0"


# ---------------------------------------------------------------------------
# POST /api/v1/scenarios (stateless identity pass-through)
# ---------------------------------------------------------------------------


class TestScenarioRegistration:
    def test_valid_scenario_id_accepted(self, client):
        response = client.post(
            "/api/v1/scenarios", json={"scenarioId": "SC-1"}
        )
        assert response.status_code == 200
        assert response.json()["data"] == {
            "scenarioId": "SC-1", "status": "REGISTERED",
        }

    def test_missing_scenario_id_is_400(self, client):
        response = client.post("/api/v1/scenarios", json={})
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "INVALID_SCENARIO_ID"


# ---------------------------------------------------------------------------
# POST /api/v1/predictions/* (E06)
# ---------------------------------------------------------------------------


class TestPredictionEndpoints:
    def test_duration_prediction_exact_and_honest(self, client):
        response = client.post("/api/v1/predictions/duration", json=DURATION_BODY)
        assert response.status_code == 200
        data = response.json()["data"]
        # Exact deterministic baseline: 90 × 1.10 (HIGH) × 1.15 (CORRECTIVE).
        assert data["predictedDurationMinutes"] == pytest.approx(113.85)
        assert data["overrunProbability"] in (0.0, 1.0)
        assert data["algorithm"] == "deterministic-rules"  # §14: no ML claim
        assert data["modelId"] == "railmind-duration-prediction"
        assert data["modelVersion"] == "1.0.0"

    def test_duration_overrun_threshold_explicit(self, client):
        body = {**DURATION_BODY, "overrunThresholdMinutes": 100.0}
        response = client.post("/api/v1/predictions/duration", json=body)
        data = response.json()["data"]
        assert data["thresholdMinutes"] == 100.0
        assert data["overrunProbability"] == 1.0  # 113.85 > 100

    def test_duration_deadline_without_start_is_400(self, client):
        body = {
            **DURATION_BODY,
            "latestFinish": "2026-09-14T20:00:00Z",
        }
        response = client.post("/api/v1/predictions/duration", json=body)
        assert response.status_code == 400
        assert "start" in response.json()["error"]["message"].lower()

    def test_failure_risk_prediction_exact_class_and_provenance(self, client):
        response = client.post("/api/v1/predictions/failure-risk", json=FAILURE_BODY)
        assert response.status_code == 200
        data = response.json()["data"]
        assert 0.0 <= data["probabilityOfFailure"] <= 1.0
        assert data["riskClass"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        assert data["algorithm"] == "deterministic-rules"
        assert data["modelId"] == "railmind-failure-risk-prediction"
        assert data["timeHorizonHours"] == 720.0

    def test_failure_risk_matches_the_engine_exactly(self, client):
        from engine import FailureRiskFeatures, FailureRiskPredictor

        response = client.post("/api/v1/predictions/failure-risk", json=FAILURE_BODY)
        api_prob = response.json()["data"]["probabilityOfFailure"]
        direct = FailureRiskPredictor().predict(
            FailureRiskFeatures(
                asset_id="A-1", asset_age_days=4000.0, asset_type="SWITCH",
                maintenance_history=6, failure_history=3, criticality="HIGH",
                days_since_last_service=200.0, task_backlog=4,
                condition_score=55.0,
            )
        )
        assert api_prob == pytest.approx(direct.probability_of_failure)

    def test_condition_score_out_of_range_rejected(self, client):
        response = client.post(
            "/api/v1/predictions/failure-risk",
            json={**FAILURE_BODY, "conditionScore": 150.0},
        )
        assert response.status_code == 422  # schema boundary (ge=0 le=100)

    def test_unknown_asset_type_is_400(self, client):
        response = client.post(
            "/api/v1/predictions/failure-risk",
            json={**FAILURE_BODY, "assetType": "HOVERCRAFT"},
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "ENGINE_INPUT_INVALID"

    def test_unknown_task_type_is_400(self, client):
        response = client.post(
            "/api/v1/predictions/duration",
            json={**DURATION_BODY, "taskType": "TELEPORT"},
        )
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# HTTP semantics / envelope integrity
# ---------------------------------------------------------------------------


class TestEnvelopeAndErrors:
    def test_meta_present_on_success(self, client):
        response = client.post("/api/v1/maintenance/prioritize", json=PRIORITY_BODY)
        meta = response.json()["meta"]
        assert meta["requestId"]
        assert meta["version"] == "v1.0.0"

    def test_no_stack_traces_in_error_responses(self, client):
        response = client.post(
            "/api/v1/maintenance/prioritize",
            json={**PRIORITY_BODY, "criticality": "URGENT"},
        )
        assert "Traceback" not in response.text
        assert "engine_bridge" not in response.text  # no internal paths

    def test_existing_endpoints_untouched(self, client):
        assert client.get("/health").status_code == 200
        assert client.get("/api/v1/maintenance/tasks").status_code == 200
