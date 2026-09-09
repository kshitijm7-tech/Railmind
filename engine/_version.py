"""Version constants for the Freebuff constraint engine.

The reproducibility contract (TRD §67) requires every evaluation to identify
which constraint definitions were used. These constants are the E01 source of
truth; keep them explicit and simple (no registry machinery at E01).
"""

ENGINE_VERSION = "0.1.0"

# Identity of the constraint set evaluated by this engine.
CONSTRAINT_SET_ID = "railmind-core-constraints"
CONSTRAINT_SET_VERSION = "1.0.0"

# Identity of the deterministic priority model (E02).
PRIORITY_MODEL_ID = "railmind-deterministic-priority"
PRIORITY_MODEL_VERSION = "1.0.0"

# Identity of the optimization objective/evaluation layer (E03).
OPTIMIZATION_MODEL_ID = "railmind-optimization-objective"
OPTIMIZATION_MODEL_VERSION = "1.0.0"

# Identity of the deterministic scenario comparison layer (E04).
SCENARIO_MODEL_ID = "railmind-scenario-comparison"
SCENARIO_MODEL_VERSION = "1.0.0"

# Identity of the seeded Monte Carlo robustness pass (E05).
SIMULATION_MODEL_ID = "railmind-monte-carlo-robustness"
SIMULATION_MODEL_VERSION = "1.0.0"

# Identity of the predictive-intelligence boundary (E06). The umbrella id
# covers the model interface + registry contract; the two shipped
# deterministic-fallback predictors carry their own identities.
PREDICTION_MODEL_ID = "railmind-predictive-risk"
PREDICTION_MODEL_VERSION = "1.0.0"
DURATION_MODEL_ID = "railmind-duration-prediction"
DURATION_MODEL_VERSION = "1.0.0"
FAILURE_RISK_MODEL_ID = "railmind-failure-risk-prediction"
FAILURE_RISK_MODEL_VERSION = "1.0.0"
