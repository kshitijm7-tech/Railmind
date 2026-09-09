"""Severity model for constraint results.

Independent of status so a PASS can still carry informational severity
(e.g. an exact-boundary containment) and a WARNING carries elevated severity.
"""

from enum import Enum


class ConstraintSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
