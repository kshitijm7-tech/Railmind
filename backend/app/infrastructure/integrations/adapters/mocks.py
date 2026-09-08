from typing import Dict, Any, List
from app.infrastructure.integrations.models import DataSourceType
from app.infrastructure.integrations.adapters.base import DataSourceAdapter

class MockTMSAdapter:
    source_type = DataSourceType.TMS
    adapter_version = "v1.0"
    
    def fetch(self, request_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Mocks Train TRN-500
        return [{
            "tms_id": "TRN-500",
            "name": "Express 500",
            "number": "500X",
            "train_type": "PASSENGER",
            "origin": "STN-A",
            "destination": "STN-B",
            "max_velocity_kmh": 120,
            "length_meters": 300,
            "weight_tons": 500,
            "priority_class": 1,
            "path_segments": [
                {
                    "section": "SEC-002",
                    "entry_time": "2026-09-09T10:00:00Z",
                    "exit_time": "2026-09-09T10:30:00Z"
                }
            ]
        }]

class MockSMMSAdapter:
    source_type = DataSourceType.SMMS
    adapter_version = "v1.0"
    
    def fetch(self, request_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Mocks Task TASK-001
        return [{
            "smms_task_id": "TASK-001",
            "asset_reference": "AST-101",
            "section_reference": "SEC-002",
            "maintenance_type": "CORRECTIVE",
            "status": "PENDING",
            "criticality_level": "HIGH",
            "department": "SIGNAL",
            "desc": "Fix circuit fault",
            "duration_mins": 120,
            "min_mins": 90,
            "max_mins": 150,
            "power_block": True,
            "traffic_block": True,
            "defects": ["DEF-001"]
        }]

class MockTDMSAdapter:
    source_type = DataSourceType.TDMS
    adapter_version = "v1.0"
    
    def fetch(self, request_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Mocks Asset AST-101, SEC-002, DEF-001
        return [{
            "tdms_asset_id": "AST-101",
            "section": "SEC-002",
            "asset_type": "TRACK_CIRCUIT",
            "current_condition": "DEGRADED",
            "last_inspection": "2026-09-01T00:00:00Z"
        }]

class MockBDMSAdapter:
    source_type = DataSourceType.BDMS
    adapter_version = "v1.0"
    
    def fetch(self, request_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [{
            "bdms_block_id": "BLK-999",
            "section": "SEC-002",
            "requested_start": "2026-09-09T12:00:00Z",
            "requested_end": "2026-09-09T14:00:00Z",
            "block_state": "APPROVED"
        }]

class MockCOAAdapter:
    source_type = DataSourceType.COA
    adapter_version = "v1.0"
    
    def fetch(self, request_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [{
            "coa_window_id": "WIN-001",
            "section_id": "SEC-002",
            "start": "2026-09-09T01:00:00Z",
            "end": "2026-09-09T05:00:00Z",
            "availability": "AVAILABLE"
        }]