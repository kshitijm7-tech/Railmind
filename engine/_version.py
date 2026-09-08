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
