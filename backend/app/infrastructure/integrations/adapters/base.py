from typing import Protocol, Dict, Any, List
from app.infrastructure.integrations.models import DataSourceType

class DataSourceAdapter(Protocol):
    source_type: DataSourceType
    adapter_version: str

    def fetch(self, request_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch records from the mock source based on request_params.
        Returns a list of raw payloads.
        """
        ...