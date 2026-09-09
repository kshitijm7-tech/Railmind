from typing import Dict, Any
from datetime import datetime
from app.infrastructure.integrations.models import DataQualityResult, RecordStatus

class DataQualityEngine:
    def validate(self, source_type: str, raw_payload: Dict[str, Any]) -> DataQualityResult:
        errors = []
        warnings = []
        checks_passed = 0
        checks_failed = 0
        
        # Generic check: must be dict
        if not isinstance(raw_payload, dict):
            return DataQualityResult(
                status=RecordStatus.INVALID,
                errors=["Payload is not a valid object"],
                checks_passed=0,
                checks_failed=1
            )
            
        checks_passed += 1

        if source_type == "TMS":
            if not raw_payload.get("tms_id"):
                errors.append("Missing required field: tms_id")
                checks_failed += 1
            else:
                checks_passed += 1
                
        elif source_type == "SMMS":
            if not raw_payload.get("smms_task_id"):
                errors.append("Missing required field: smms_task_id")
                checks_failed += 1
            else:
                checks_passed += 1
                
            if raw_payload.get("min_mins", 0) > raw_payload.get("max_mins", 0):
                errors.append("min_mins cannot be greater than max_mins")
                checks_failed += 1
            else:
                checks_passed += 1
                
        # Mock simple warning rule
        if "desc" not in raw_payload and "description" not in raw_payload:
            warnings.append("Optional description is missing")
            
        if errors:
            status = RecordStatus.INVALID
        elif warnings:
            status = RecordStatus.VALID_WITH_WARNINGS
        else:
            status = RecordStatus.VALID
            
        return DataQualityResult(
            status=status,
            errors=errors,
            warnings=warnings,
            checks_passed=checks_passed,
            checks_failed=checks_failed
        )