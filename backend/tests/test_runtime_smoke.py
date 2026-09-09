"""E08 runtime smoke tests — the actual HTTP application boundary.

Layer discipline (prompt §21): these tests exercise
``HTTP → FastAPI → router → service → mapper → engine`` through the real
ASGI application (TestClient transport) — no engine mocks, controlled
deterministic fixtures, `raise_server_exceptions=False` so genuine server
errors surface as HTTP 500 exactly as a deployed app would emit them.

Classified per prompt §33: unit = engine/tests + backend unit tests;
integration = backend router→engine suites; runtime/smoke = this file
(real ASGI app, real HTTP semantics, server-error path included).
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

# Real ASGI app, server exceptions surfaced as HTTP 500 (as deployed).
client = TestClient(app, raise_server_exceptions=False)

PRIORITY_BODY = {
    "taskId": "RT-T-1",
    "sectionId": "SEC-002",
    "criticality": "CRITICAL",
    "overdueDays": 10,
    "taskType": "EMERGENCY",
}

SIMULATE_BODY = {
    "windows": [
        {
            "windowId": "RT-W1",
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
    "taskId": "RT-T-9",
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
    "assetId": "RT-A-1",
    "assetAgeDays": 4000.0,
    "assetType": "SWITCH",
    "maintenanceHistory": 6,
    "failureHistory": 3,
    "criticality": "HIGH",
    "daysSinceLastService": 200.0,
    "taskBacklog": 4,
    "conditionScore": 55.0,
}


class TestRuntimeSmoke:
    """Runtime/smoke classification: real ASGI boundary (prompt §33)."""

    def test_prioritize_over_http(self, client=client):
        response = client.post("/api/v1/maintenance/prioritize", json=PRIORITY_BODY)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["taskId"] == "RT-T-1"
        assert data["priorityClass"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        assert 0.0 <= data["priorityScore"] <= 1.0
        assert {f["factor"] for f in data["factors"]} >= {"criticality", "overdue"}
        assert data["priorityModelId"] == "railmind-deterministic-priority"

    def test_plan_simulate_over_http_preserves_sampling_evidence(self, client=client):
        response = client.post("/api/v1/plans/PLAN-RT/simulate", json=SIMULATE_BODY)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["candidateId"] == "PLAN-RT"
        assert data["seed"] == 7
        assert data["iterations"] == 50
        assert data["distribution"] == "UNIFORM"
        assert 0.0 <= data["planViolationProbability"] <= 1.0
        block = data["blocks"][0]
        assert block["windowId"] == "RT-W1"
        assert set(block["constraintExceedances"]) == {
            "c6_duration_feasibility", "c7_window_bounds",
        }
        assert block["violationDraws"] == sorted(block["violationDraws"])
        assert set(block["violationDraws"]) <= set(range(50))

    def test_scenario_simulate_over_http(self, client=client):
        response = client.post(
            "/api/v1/scenarios/SC-RT/simulate", json=SIMULATE_BODY
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["candidateId"] == "SC-RT"
        assert data["seed"] == 7 and data["iterations"] == 50

    def test_scenario_registration_over_http(self, client=client):
        response = client.post("/api/v1/scenarios", json={"scenarioId": "SC-RT"})
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "REGISTERED"

    def test_duration_prediction_over_http(self, client=client):
        response = client.post("/api/v1/predictions/duration", json=DURATION_BODY)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["predictedDurationMinutes"] == pytest.approx(113.85)  # 90×1.10×1.15
        assert data["algorithm"] == "deterministic-rules"
        assert data["modelId"] == "railmind-duration-prediction"

    def test_failure_risk_prediction_over_http(self, client=client):
        response = client.post("/api/v1/predictions/failure-risk", json=FAILURE_BODY)
        assert response.status_code == 200
        data = response.json()["data"]
        assert 0.0 <= data["probabilityOfFailure"] <= 1.0
        assert data["riskClass"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        assert data["algorithm"] == "deterministic-rules"

    def test_health_over_http(self, client=client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["data"] == "OK"

    def test_version_over_http(self, client=client):
        response = client.get("/api/v1/version")
        assert response.status_code == 200
        assert response.json()["data"]["version"] == "1.0.0"


class TestRuntimeErrorPaths:
    """Live failure behavior through the real app (§9)."""

    def test_malformed_json_is_422_shape(self, client=client):
        response = client.post(
            "/api/v1/maintenance/prioritize",
            content=b"{not json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_missing_required_field_is_422(self, client=client):
        response = client.post(
            "/api/v1/maintenance/prioritize",
            json={"taskId": "T", "criticality": "HIGH"},
        )
        assert response.status_code == 422

    def test_engine_semantic_violation_is_400_with_envelope(self, client=client):
        response = client.post(
            "/api/v1/maintenance/prioritize",
            json={**PRIORITY_BODY, "criticality": "URGENT"},
        )
        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "INVALID_CRITICALITY"
        assert error["httpStatus"] == 400
        assert "LOW|MEDIUM|HIGH|CRITICAL" in error["message"]
        assert "Traceback" not in response.text
        assert "engine_bridge" not in response.text  # no internals/paths

    def test_unknown_route_is_404(self, client=client):
        assert client.get("/api/v1/does-not-exist").status_code == 404

    def test_inverted_bands_400_engine_message_preserved(self, client=client):
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


class TestRuntimeDeterminism:
    """Same request → equivalent domain results through the real app (§11)."""

    def test_simulation_reproducible_over_http(self, client=client):
        a = client.post("/api/v1/plans/P/simulate", json=SIMULATE_BODY).json()["data"]
        b = client.post("/api/v1/plans/P/simulate", json=SIMULATE_BODY).json()["data"]
        a.pop("candidateId"), b.pop("candidateId")
        assert a == b  # seed+iterations identical → identical evidence

    def test_priority_deterministic_over_http(self, client=client):
        a = client.post("/api/v1/maintenance/prioritize", json=PRIORITY_BODY).json()["data"]
        b = client.post("/api/v1/maintenance/prioritize", json=PRIORITY_BODY).json()["data"]
        assert a == b

    def test_global_rng_untouched_after_traffic(self, client=client):
        import random

        random.seed(42)
        before = random.getstate()
        client.post("/api/v1/plans/P/simulate", json=SIMULATE_BODY)
        client.post("/api/v1/maintenance/prioritize", json=PRIORITY_BODY)
        assert random.getstate() == before


class TestRuntimeProvenance:
    """§10: engine → adapter → HTTP → JSON lineage, nothing rewritten."""

    def test_e05_provenance_end_to_end(self, client=client):
        data = client.post("/api/v1/plans/P/simulate", json=SIMULATE_BODY).json()["data"]
        assert data["simulationModelId"] == "railmind-monte-carlo-robustness"
        assert data["simulationModelVersion"] == "1.0.0"
        assert data["engineVersion"] == "0.1.0"

    def test_e02_provenance_end_to_end(self, client=client):
        data = client.post("/api/v1/maintenance/prioritize", json=PRIORITY_BODY).json()["data"]
        assert data["priorityModelVersion"] == "1.0.0"
        assert data["engineVersion"] == "0.1.0"

    def test_request_correlation_separate_from_domain_provenance(self, client=client):
        """§18: the middleware's X-Request-Id is transport correlation only —
        it never appears inside domain provenance fields."""
        response = client.post("/api/v1/maintenance/prioritize", json=PRIORITY_BODY)
        header_id = response.headers.get("x-request-id")
        assert header_id
        data = response.json()["data"]
        assert header_id not in str(data["priorityModelId"])
        assert "requestId" not in data  # correlation lives in meta only


class TestCorsConfiguration:
    """TRD §46 API Security (Tier-1): CORS is environment-configured only.

    The secure default applies NO CORS middleware (same-origin only); a
    wildcard is never silently mixed with explicit origins.
    """

    def _client_for(self, env):
        from app.core.runtime import RuntimeContext
        from app.main import create_app

        return TestClient(
            create_app(RuntimeContext.from_env(env)), raise_server_exceptions=False
        )

    def test_default_no_cors_headers(self):
        response = self._client_for({}).options(
            "/api/v1/version",
            headers={
                "Origin": "http://evil.example",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" not in response.headers

    def test_explicit_origin_allowed(self):
        env = {"RAILMIND_CORS_ALLOWED_ORIGINS": "http://localhost:5173"}
        client = self._client_for(env)
        response = client.options(
            "/api/v1/version",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.headers["access-control-allow-origin"] == "http://localhost:5173"

    def test_unlisted_origin_rejected(self):
        env = {"RAILMIND_CORS_ALLOWED_ORIGINS": "http://localhost:5173"}
        client = self._client_for(env)
        response = client.options(
            "/api/v1/version",
            headers={
                "Origin": "http://evil.example",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" not in response.headers

    def test_wildcard_allowed(self):
        env = {"RAILMIND_CORS_ALLOWED_ORIGINS": "*"}
        client = self._client_for(env)
        response = client.options(
            "/api/v1/version",
            headers={
                "Origin": "http://anything.example",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.headers["access-control-allow-origin"] == "*"

    def test_wildcard_mixed_with_origins_rejected_at_startup(self):
        import pytest as _pytest

        from app.core.runtime import RuntimeContext

        with _pytest.raises(ValueError, match="mixes"):
            RuntimeContext.from_env(
                {"RAILMIND_CORS_ALLOWED_ORIGINS": "*,http://localhost:5173"}
            )


class TestObservability:
    """TRD §47 Tier-1: structured JSON log line per request, X-Request-Id
    correlation, engine-phase metadata — no payloads in logs (§19)."""

    def test_request_id_header_present_and_unique(self):
        a = client.get("/health")
        b = client.get("/health")
        assert a.headers["x-request-id"]
        assert b.headers["x-request-id"]
        assert a.headers["x-request-id"] != b.headers["x-request-id"]

    def test_structured_json_log_line(self, caplog):
        import json
        import logging

        logger = logging.getLogger("railmind.api")
        old_propagate = logger.propagate
        logger.propagate = True
        try:
            with caplog.at_level(logging.INFO, logger="railmind.api"):
                client.post("/api/v1/maintenance/prioritize", json=PRIORITY_BODY)
            record = json.loads(caplog.records[-1].message)
            assert record["service"] == "railmind-backend"
            assert record["method"] == "POST"
            assert record["path"] == "/api/v1/maintenance/prioritize"
            assert record["status"] == 200
            assert isinstance(record["duration_ms"], float)
            assert record["engine_phase"] == "E02"
            assert "timestamp" in record and "run_id" in record
        finally:
            logger.propagate = old_propagate

    def test_log_line_carries_no_request_payload(self, caplog):
        import json
        import logging

        logger = logging.getLogger("railmind.api")
        old_propagate = logger.propagate
        logger.propagate = True
        try:
            with caplog.at_level(logging.INFO, logger="railmind.api"):
                client.post("/api/v1/maintenance/prioritize", json=PRIORITY_BODY)
            line = caplog.records[-1].message
            assert "sectionId" not in line
            assert "criticality" not in line
        finally:
            logger.propagate = old_propagate
        json.loads(line)  # and the line is still valid JSON


class TestOpenApiContract:
    """§8: generated OpenAPI exposes exactly the intended public routes with
    request/response models — no internal engine classes, no accidental
    routes."""

    def test_all_engine_routes_registered(self):
        schema = client.get("/openapi.json").json()
        paths = set(schema["paths"])
        assert "/api/v1/maintenance/prioritize" in paths
        assert "/api/v1/plans/{plan_id}/simulate" in paths
        assert "/api/v1/scenarios" in paths
        assert "/api/v1/scenarios/{scenario_id}/simulate" in paths
        assert "/api/v1/predictions/duration" in paths
        assert "/api/v1/predictions/failure-risk" in paths
        assert "/health" in paths
        assert "/api/v1/version" in paths

    def test_request_response_models_present(self):
        schema = client.get("/openapi.json").json()
        prioritize = schema["paths"]["/api/v1/maintenance/prioritize"]["post"]
        assert "requestBody" in prioritize
        assert "200" in prioritize["responses"]

    def test_no_internal_routes_exposed(self):
        schema = client.get("/openapi.json").json()
        for path in schema["paths"]:
            assert "engine" not in path  # engine internals stay unexposed
            assert not path.startswith("/app")


class TestRuntimePerformance:
    """§23: smoke-level guard against obvious regressions (no invented
    benchmark target — TRD §48's 'UI < 1 second' is the only published
    figure and these O(N) operations are orders of magnitude below it)."""

    def test_plan_generation_runtime_smoke(self, client=client):
        """E09 over the real ASGI boundary: the full chain
        HTTP → router → service → mapper → engine_bridge → CP-SAT → E03,
        with deterministic reproducibility and provenance intact."""
        import time

        def pb(tid):
            return {
                "taskId": tid, "sectionId": "SEC-RT", "criticality": "HIGH",
                "overdueDays": 3, "taskType": "PREVENTIVE",
            }

        p1 = client.post("/api/v1/maintenance/prioritize", json=pb("RT-T1")).json()["data"]
        p2 = client.post("/api/v1/maintenance/prioritize", json=pb("RT-T2")).json()["data"]
        body = {
            "planRef": "PLAN-RT-GEN",
            "tasks": [
                {"taskId": "RT-T1", "durationMinutes": 40, "department": "S&T",
                 "crewSize": 2, "priority": p1},
                {"taskId": "RT-T2", "durationMinutes": 25, "department": "S&T",
                 "crewSize": 2, "priority": p2},
            ],
            "windows": [
                {"windowId": "RT-GW1", "sectionId": "SEC-RT",
                 "earliestStart": "2026-09-14T22:00:00Z",
                 "latestEnd": "2026-09-15T02:00:00Z",
                 "maxDurationMinutes": 90.0, "qualifiedDepartments": ["S&T"]},
                {"windowId": "RT-GW2", "sectionId": "SEC-RT",
                 "earliestStart": "2026-09-15T22:00:00Z",
                 "latestEnd": "2026-09-16T02:00:00Z",
                 "maxDurationMinutes": 90.0, "qualifiedDepartments": ["S&T"]},
            ],
            "crewPools": [{"department": "S&T", "shiftId": "NIGHT", "availableCrew": 4}],
            "randomSeed": 7,
            "alternativeCount": 1,
        }
        started = time.perf_counter()
        response = client.post("/api/v1/plans/generate", json=body)
        elapsed = time.perf_counter() - started
        assert response.status_code == 200
        data = response.json()["data"]

        # Solve evidence rides on the real boundary (TRD §67).
        evidence = data["evidence"]
        assert evidence["solver"] == "cpsat"
        assert evidence["randomSeed"] == 7
        assert evidence["status"] in {"OPTIMAL", "FEASIBLE"}
        assert evidence["constraintSetId"]
        assert evidence["plannerModelId"]

        # Every task accounted for; plans ranked; ids canonical.
        assert len(data["plans"]) == 2
        assert data["bestPlanId"] == data["plans"][0]["planId"]
        assert data["bestPlanId"].endswith("-alt0")
        for plan in data["plans"]:
            assert {a["taskId"] for a in plan["assignments"]} == {"RT-T1", "RT-T2"}
            for block in plan["blocks"]:
                assert block["start"] < block["end"]
                assert block["assignedTaskIds"]
            assert plan["constraintTrace"]

        # c5: same-section windows never overlap on the same plan.
        for plan in data["plans"]:
            blocks = plan["blocks"]
            for i in range(len(blocks)):
                for j in range(i + 1, len(blocks)):
                    if blocks[i]["sectionId"] == blocks[j]["sectionId"]:
                        assert (
                            blocks[i]["end"] <= blocks[j]["start"]
                            or blocks[j]["end"] <= blocks[i]["start"]
                        )

        # Determinism: same request → identical domain payload (wall time
        # is a genuine measurement, compared with tolerance).
        again = client.post("/api/v1/plans/generate", json=body).json()["data"]
        again["evidence"]["wallTimeMs"] = data["evidence"]["wallTimeMs"]
        assert again == data

        # §47 observability: E09 phase attribution on the real boundary.
        from app.core.runtime import engine_phase_for_path

        assert engine_phase_for_path("/api/v1/plans/generate") == "E09"
        # TRD §48's published UI figure — the O(N·windows) pipeline is far
        # below it (the engine's own budget guard pins the 10 s solve).
        assert elapsed < 1.0

    def test_prioritize_under_one_second(self, client=client):
        import time

        started = time.perf_counter()
        response = client.post("/api/v1/maintenance/prioritize", json=PRIORITY_BODY)
        elapsed = time.perf_counter() - started
        assert response.status_code == 200
        assert elapsed < 1.0

    def test_monte_carlo_200_iterations_under_one_second(self, client=client):
        import time

        body = {**SIMULATE_BODY, "iterations": 200}  # authoritative default
        started = time.perf_counter()
        response = client.post("/api/v1/plans/P/simulate", json=body)
        elapsed = time.perf_counter() - started
        assert response.status_code == 200
        assert elapsed < 1.0
