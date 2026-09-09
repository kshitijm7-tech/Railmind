# E06 — Predictive Risk & Uncertainty Intelligence Report

Status: **COMPLETE** · Commit: *this commit* · Branch: `freebuff/engine`

## 1. Executive Summary

Implemented the E06 **predictive-intelligence model boundary** as `engine/prediction/`: the TRD §17 common `PredictionModel` interface (runtime-checkable Protocol), the TRD §18 model-registry metadata contract, the exact TRD §13 / §15 feature contracts, and the two model families the documentation assigns to E06 and that E02 deliberately did not implement — **duration prediction** (TRD §13 / blueprint §16.1) and **asset failure-risk prediction** (TRD §15). Inference is fully deterministic, stdlib-only (pydantic for contracts), and every probability output is structurally bounded to [0, 1].

**No dataset or trained-model artifact exists in this repository.** Per TRD §50 ("ML unavailable → fallback: deterministic rules / statistical baseline") and TRD §16 ("only the models that have sufficient training data should be enabled"), the shipped predictors are the documented **deterministic fallbacks** — honest rule-based baselines labeled `algorithm="deterministic-rules"` with the ML registry path recorded `DISABLED`. Nothing is presented as trained ML; no metrics are fabricated.

## 2. Authoritative specification

- **Blueprint §16** (Intelligence Layer — Concrete Model Specifications): §16.1 duration prediction (features, XGBoost regression on synthetic records, outputs expected duration / P10 / P90 / overrun risk); §16.2 priority — **already owned by E02** (docs/E02_Report.md), not reimplemented; §16.3 delay prediction; §16.4 GNN explicitly deferred ("Do not let the GNN block the core deliverable"); §16.5 anomaly detection = Tier 2.
- **TRD §12/§15** (Model 2 Duration / Model 4 Asset Failure-Risk): exact input/output lists, recommended algorithms.
- **TRD §17** (ML Design Principle): the common `PredictionModel` interface — `predict`, `predict_with_uncertainty`, `get_version`, `explain` — "so XGBoost can later be replaced by LightGBM/PyTorch/GNN without changing the rest of RAILMIND."
- **TRD §18** (ML Model Registry): metadata fields (model_id, version, dataset/feature-schema versions, metrics, artifact_location, status).
- **TRD §19** (evaluation metrics) and **TRD §16** (only models with sufficient data are enabled).
- **TRD §50** (Fault Tolerance: ML unavailable → deterministic fallback) and **§51** (offline mode is first-class).
- **frontend/contracts/ai/predictions.ts** (canonical result vocabulary) and **contracts/common/provenance.ts** (Provenance/DataState enums).
- **Spec silences documented** (§43): no calibration method is specified anywhere → none implemented (§11: do not add hidden calibration); no failure-risk thresholds are specified → E06-owned, configurable, explicitly-documented [ASSUMPTION] thresholds (0.20/0.45/0.70), deliberately not E02's priority thresholds; the §16.1 interval width for the baseline is unspecified → documented factors (0.85/1.25); TRD §15 fixes no numeric horizon → 720 h default mirroring the canonical TS contract. No conflicts requiring resolution were found.

## 3. Architecture

```
DETERMINISTIC PATH (unchanged)
E01 feasibility → E02 priority → E03 objective → E04 comparison

EVIDENCE PATH (extends, never replaces)
E05 Monte Carlo simulation evidence ┐
                                    ├─→ E06 predictive evidence (this engine)
TRD §13/§15 feature vectors ────────┘
        ↓
PredictionModel interface (TRD §17) → DurationPredictor | FailureRiskPredictor
        ↓                                   (future: XGBoost adapters)
DurationPredictionResult | FailureRiskPredictionResult (+ TRD §18 metadata)
```

`engine/prediction/` imports only stdlib + pydantic + `engine._version` (+ `engine.models.inputs` for the shared timezone guard and `engine.priority.inputs` for the shared task-type vocabulary). Dependency direction is **E06 → upstream contracts only**; E01–E05 never import E06 (AST-tested). ML-library objects never cross the boundary — concrete future adapters implement the same Protocol (TRD §17's replacement guarantee).

## 4. Input contract

Exact documented feature lists, no invented features (prompt §6):

- **`DurationFeatures`** (TRD §13 / blueprint §16.1): `task_type` (canonical vocabulary), `department`, `asset_type`, `section_criticality` (LOW|MEDIUM|HIGH|CRITICAL), `crew_size`, `historical_duration_minutes`, `time_of_day_minutes`, `days_since_last_similar_task`. All required — missing data is the caller's problem; the engine never invents features.
- **`FailureRiskFeatures`** (TRD §15): `asset_age_days`, `asset_type`, `maintenance_history`, `failure_history`, `criticality`, `days_since_last_service`, `task_backlog`, `condition_score` (0–100), plus `time_horizon_hours` (mirrors the TS `FailureRiskPrediction` contract).
- **`DurationPredictionWindow`**: the overrun-threshold context — explicit `overrun_threshold_minutes` > deadline-derived budget (`latest_finish` − `start_at`) > configured default. A deadline without `start_at` is **refused, never guessed**.

Validation: canonical enums only, finite numbers, loud rejection of NaN/±Infinity/out-of-range (no clamping), timezone-aware datetimes, frozen models.

## 5. Model contract

- **Interface**: `PredictionModel` Protocol (TRD §17), `runtime_checkable`; both shipped predictors satisfy `isinstance` checks and expose all four methods. `ModelNotAvailableError` exists for callers that explicitly demand model-backed inference (TRD §50's complement — baseline numbers are never dressed up as ML output).
- **Registry** (TRD §18): `ModelMetadata` frozen record (model_id/name/type, version, feature_schema_version, algorithm, dataset/timestamp/metrics/artifact fields, status, deterministic_fallback). Both baselines carry `status=DISABLED`, `deterministic_fallback=True`, `training_dataset_version=None` — the honest state. Each result embeds its registry snapshot (`registry_metadata`).
- **Identity** (`engine/_version.py`): umbrella `PREDICTION_MODEL_ID="railmind-predictive-risk"` plus per-model `DURATION_MODEL_ID` / `FAILURE_RISK_MODEL_ID`, all v1.0.0 — matching the E01–E05 convention. `ENGINE_VERSION` untouched.

## 6. Prediction semantics

- **Duration** (`DurationPredictionResult`): `expected = historical_duration × criticality_factor × task_type_factor` (both factor maps configurable); `p10 = 0.85 × expected`, `p90 = 1.25 × expected` [ASSUMPTION factors]; `overrun_probability ∈ {0.0, 1.0}` — an honest step function of (point estimate > threshold): the baseline is a point estimate, and fabricating a smooth probability would be dishonest (prompt §10: keep model evidence distinct from E05's simulation evidence). `reason_codes` are data-derived (`OVERRUN_RISK`, `HIGH_CRITICALITY_SECTION`, `UNPLANNED_WORK`, `LONG_SINCE_SIMILAR_TASK`).
- **Failure risk** (`FailureRiskPredictionResult`): `probability_of_failure` = weighted mean of normalized TRD §15 features (weights sum to 1.0: failure history 0.25, age/criticality 0.15 each, type/maintenance/gap/condition 0.10 each, backlog 0.05 — degradation evidence dominates [ASSUMPTION]); `risk_class` ∈ LOW|MEDIUM|HIGH|CRITICAL under E06-owned thresholds with `>=` boundary ownership (tested: a probability exactly on a threshold belongs to the higher class); `confidence` = the documented baseline honesty budget (0.5), not a fabricated uncertainty estimate.
- **Probabilities are never rounded, clamped or renamed**; `require_probability`/`require_finite` guard every boundary (NaN fails all range comparisons and is rejected).

## 7. Calibration

**Not implemented — intentionally.** No authoritative document specifies a calibration method (Platt/isotonic/other). Per prompt §11, calibration is not added as hidden behavior; the calibrated/raw distinction would be fabricated evidence. The contract leaves room: `PredictionConfig` is versioned, and a future spec-backed calibrator would slot in behind the same `PredictionModel` interface.

## 8. Provenance

Every result carries `model_id` / `model_version` / `engine_version` / `algorithm` plus the TRD §18 `registry_metadata` snapshot. Upstream lineage is preserved by reference and never rewritten: E02's `AssetFailureRisk` (the E02-facing risk input, mirroring the same TS contract) remains the integration point in that direction; E05 simulation evidence is consumed upstream of E06 by callers, not re-derived here. Canonical `Provenance` vocabulary (DataSource/DataState enums from `contracts/common/provenance.ts`) is mirrored 1:1 in `PredictionProvenance` with caller-supplied `recorded_at` — the engine reads no clock, so results remain byte-identical for identical inputs.

## 9. Reproducibility

Inference is a pure function of (features, window, config): no clocks, no randomness, no I/O, no global state — verified by byte-identical `model_dump()` equality across repeated calls, frozen input/result models (mutation attempts raise), and AST-level scans proving zero `random` usage and zero clock reads (`now`/`utcnow`/`time`/`perf_counter`/`monotonic`) inside `engine/prediction/`. If a future trained model introduces stochastic training, E05's seed discipline (`SimulationConfig` explicit-seed pattern) is the designated precedent.

## 10. Testing

- `test_prediction_config.py` (15): version identity, documented defaults, non-increasing/out-of-range thresholds rejected, non-positive saturations/horizons rejected, `>=` classification boundary ownership (exact 0.199/0.20/0.449/0.45/0.699/0.70 cases), thresholds provably not E02's, saturation normalization, shared E02 criticality mapping, honest registry status, pinned feature-schema version.
- `test_prediction_models.py` (33): exact documented feature vocabulary (case handling), every invalid-input rejection (unknown task type/criticality, negative, out-of-range, NaN/±Inf, 1440-minute bound, naive datetimes, zero horizon), unknown asset type refused loudly at the predictor boundary, **threshold resolution order** (explicit > deadline-derived > default; deadline-without-start refused; inverted deadline refused), **exact formula assertions** for both predictors (duration point/interval; weighted-mean failure probability recomputed independently), degradation monotonicity, saturated-input boundedness (0 ≤ p ≤ 1 with CRITICAL classification), `get_version` identity, `predict_with_uncertainty` equivalence, runtime-Protocol conformance, deterministic `explain`, byte-identical repeated inference, frozen inputs/results, provenance vocabulary enforcement (invalid DataSource/DataState rejected; naive timestamps rejected), serialization round-trips preserving model identity + registry snapshot.
- `test_prediction_contract.py` (19): E01–E05 never import E06 (dependency direction), zero randomness/forbidden-import/ML-library imports inside E06 (AST), zero clock reads (AST), no E02/E03/E05 logic duplication in predictor bodies (token scan), full TRD §17 method surface, runtime Protocol, honest registry IDs (distinct per model under the umbrella identity), result-stamped identity matching `_version.py`, exact public export surface (present AND private-helper absence), byte-identical inference through the public API.

**Totals: E06 = 67 test functions · engine 357 passed (290 baseline + 67 E06) · backend 27 passed (no regression).** First-run result: all 67 E06 tests passed; no engine code required fixing after the initial smoke check, and no existing test was modified.

## 11. Performance

O(1) per prediction — a handful of arithmetic operations and dict lookups; no model loading, no artifact parsing, no transformations. Suitable for repeated candidate evaluation (prompt §26); a future artifact-backed adapter would add loading once at construction, not per call. 357 engine tests complete in < 1 s.

## 12. REAL / MOCKED / STUBBED

- `PredictionModel` interface + runtime conformance (TRD §17): **REAL**
- TRD §18 registry metadata contract: **REAL**
- Feature contracts (TRD §13/§15, exact documented lists): **REAL**
- Duration deterministic baseline (formula, P10/P90 band, overrun step function): **REAL** (as a *baseline* — honestly labeled)
- Failure-risk deterministic baseline (weighted mean, risk classification): **REAL** (as a *baseline*)
- Validation/numerical safety (NaN/±Inf/range/enum/timezone, loud failures): **REAL**
- Provenance + serialization discipline: **REAL**
- MOCKED: **none**
- STUBBED: **none**

## 13. NOT IMPLEMENTED

- **Trained XGBoost duration regressor** (TRD §13/§16.1) and **trained XGBoost failure-risk classifier** (TRD §15): no dataset or artifact exists in the repository — the registry records honestly keep these `DISABLED`. Training, dataset contracts, temporal-split leakage safeguards, and evaluation metrics (TRD §19) belong to the ML-track phase that produces those artifacts; nothing is fabricated in their place.
- **Delay prediction** (TRD §14 Model 3 / blueprint §16.3): requires per-train block-impact inputs and the NetworkX graph-propagation layer; not part of the authoritative E06 assignment (E02/E05 reports consistently scope E06 to duration + failure risk).
- **GNN cascading-delay** (§16.4): explicitly deferred by the blueprint ("stretch enhancement… do not let the GNN block the core deliverable").
- **Anomaly detection** (§16.5): Tier 2.
- **Calibration**: unspecified (see §7).
- Model registry persistence/MLflow, FastAPI endpoints, database, frontend: outside the engine boundary (TRD §1506 explicitly warns against introducing MLflow/K8s for the MVP).

## 14. Known limitations

1. **Baselines are heuristic.** The duration factors (0.85/1.25 band, criticality/task-type multipliers) and failure-risk weights are documented [ASSUMPTION]s — deterministic and inspectable, but not learned. They must be replaced by trained models before any real-world deployment claim (PRD §137: "Claim production deployment where only synthetic data exists" is a listed anti-pattern).
2. **Overrun probability is a step function** for the baseline. Smooth per-task overrun curves require either a trained regressor or distributional sampling; E05's Monte Carlo already provides the simulation-based view and the two evidence types remain deliberately distinct (prompt §10).
3. **Asset-type vocabulary is open-ended**; unknown values are refused loudly rather than mapped to a guess. Deployments must extend `ASSET_TYPE_SCORES` (documented, configurable) or supply training data.
4. **All TRD §13/§15 features are required.** A missing-data policy (E02-style EXCLUDE/ZERO) is deliberately absent: the spec defines none for E06, and inventing one would duplicate a policy decision that belongs to an authoritative contract.
5. **Confidence is a fixed honesty budget (0.5)** for baselines — a real uncertainty model is the trained model's job.

## 15. E07 boundary

E07 may consume from E06:
- `DurationPredictionResult` / `FailureRiskPredictionResult` as bounded, provenance-complete predictive evidence (probabilities ∈ [0,1], registry metadata embedded);
- the `PredictionModel` Protocol + `ModelMetadata` contract as the integration surface for trained-model adapters (a real XGBoost artifact would plug in without changing E07's view);
- `PredictionConfig` as the single configuration point for baseline factors and risk thresholds;
- the honest-labeling convention (`algorithm`, `ModelStatus`, `deterministic_fallback`) for REAL/MOCKED/STUBBED discipline downstream.

E06 does **not** provide: delay predictions (§16.3), GNN outputs (§16.4), anomaly detection (§16.5), calibration, risk-adjusted ranking, E05-replacing simulation evidence, trained artifacts, persistence, or any API/UI — and E07 must not expect the deterministic E02–E05 semantics to change because of E06 evidence.
