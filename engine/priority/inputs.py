"""Priority engine input models (E02).

Mirrors the canonical vocabulary:
- ``frontend/contracts/maintenance/maintenance-task.ts`` (task_id, asset_id,
  section_id, type, criticality, priority_breakdown)
- ``frontend/contracts/infrastructure/track-section.ts`` (trains_per_day lives
  in the blueprint's §16.2 downstream-impact factor as "trains/day on this
  section"; the canonical TrackSection carries no traffic volume, so it is an
  explicit engine input here — see docs/E02_Report.md contract gaps)

The asset failure risk input also mirrors the TS contract
``ai/predictions.ts::FailureRiskPrediction`` (probability_of_failure,
time_horizon_hours, model_id/model_version) so a future E06 risk model can
feed E02 without remapping.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from engine.models.inputs import require_timezone_aware
from engine.priority.missing_data import MissingDataPolicy


class TaskType(str, Enum):
    """Canonical task types (``contracts/maintenance/maintenance-task.ts``)."""

    PREVENTIVE = "PREVENTIVE"
    CORRECTIVE = "CORRECTIVE"
    INSPECTION = "INSPECTION"
    EMERGENCY = "EMERGENCY"
    #: Blueprint §11.2 vocabulary member not present in the TS contract enum.
    DEFECT = "DEFECT"


#: Accepted task-type union across both documented vocabularies (module-level
#: so Pydantic does not turn it into a private model attribute).
TASK_TYPES = {"PREVENTIVE", "CORRECTIVE", "INSPECTION", "EMERGENCY", "DEFECT"}


class PriorityInput(BaseModel):
    """One maintenance requirement to prioritise.

    Required (fail-closed): task identity, section context, criticality and
    overdue days — the PRD defines overdue_days as always present ("0 if not
    overdue"), and criticality is a safety-relevant enum that must never be
    guessed.
    """

    model_config = ConfigDict(frozen=True)

    task_id: str
    section_id: str
    asset_id: Optional[str] = None

    # --- REQUIRED factor inputs ------------------------------------------
    criticality: str  # LOW | MEDIUM | HIGH | CRITICAL (canonical enum)
    overdue_days: int = Field(ge=0)  # 0 if not overdue (blueprint §11.2)

    # --- Task nature (feeds the safety factor) ----------------------------
    # Accepts BOTH canonical vocabularies (case-insensitive): the TS contract
    # enum PREVENTIVE|CORRECTIVE|INSPECTION|EMERGENCY and the blueprint §11.2
    # enum Preventive|Corrective|Inspection|Defect. Normalised to uppercase.
    task_type: Optional[str] = None
    is_safety_relevant: Optional[bool] = None  # explicit override flag
    requires_power_block: bool = False
    requires_traffic_block: bool = False

    # --- OPTIONAL factor inputs (missing-data policy applies) -------------
    asset_failure_risk: Optional["AssetFailureRisk"] = None
    trains_per_day: Optional[float] = Field(default=None, ge=0.0)

    # --- Evaluation reference time (determinism: never derived) -----------
    # Reserved for future time-sensitive factors; the overdue factor uses the
    # canonical overdue_days counter, not a clock.
    evaluation_time: Optional[datetime] = None

    @field_validator("criticality")
    @classmethod
    def _criticality_known(cls, value: str) -> str:
        if value not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
            raise ValueError(
                f"criticality must be one of LOW|MEDIUM|HIGH|CRITICAL; got {value!r}"
            )
        return value

    #: Canonical union of both documented task-type vocabularies.
    @field_validator("task_type")
    @classmethod
    def _task_type_known(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.upper()
        if normalized not in TASK_TYPES:
            raise ValueError(
                "task_type must be one of PREVENTIVE|CORRECTIVE|INSPECTION|"
                f"EMERGENCY|DEFECT (either canonical vocabulary); got {value!r}"
            )
        return normalized

    @field_validator("evaluation_time")
    @classmethod
    def _tz_aware_evaluation_time(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        return require_timezone_aware(value, "evaluation_time")


class AssetFailureRisk(BaseModel):
    """Asset failure-risk evidence (mirrors ``ai/predictions.ts``).

    ``probability_of_failure`` ∈ [0, 1] over ``time_horizon_hours``. When the
    producing model is absent (deterministic baseline mode), the probability
    is supplied directly — provenance then records the deterministic source.
    """

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    probability_of_failure: float = Field(ge=0.0, le=1.0)
    time_horizon_hours: float = Field(default=720.0, gt=0.0)
    model_id: Optional[str] = None
    model_version: Optional[str] = None

    @property
    def source(self) -> str:
        return f"risk-model:{self.model_id}@{self.model_version}" if self.model_id else "deterministic-baseline"


class AssetContext(BaseModel):
    """Minimal asset context (canonical ``infrastructure/asset.ts`` subset)."""

    model_config = ConfigDict(frozen=True)

    asset_id: str
    asset_type: Optional[str] = None
    criticality: Optional[str] = None  # LOW|MEDIUM|HIGH|CRITICAL when known
    health_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)


class SectionContext(BaseModel):
    """Minimal section context (canonical ``infrastructure/track-section.ts`` subset)."""

    model_config = ConfigDict(frozen=True)

    section_id: str
    criticality: Optional[str] = None
    trains_per_day: Optional[float] = Field(default=None, ge=0.0)


PriorityInput.model_rebuild()
