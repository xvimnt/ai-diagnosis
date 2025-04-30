from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List
from datetime import datetime

class RootCause(Enum):
    FIBER_CUT = "FIBER_CUT"
    POWER_ISSUE = "POWER_ISSUE"
    LAN_PROBLEM = "LAN_PROBLEM"
    DEVICE_FAILURE = "DEVICE_FAILURE"
    CONFIG_ERROR = "CONFIG_ERROR"
    OK = "OK"
    UNDETERMINED = "UNDETERMINED"

@dataclass
class DeviceResult:
    device_id: str
    status: str
    timestamp: datetime
    details: Dict[str, Any]
    error: str = None

@dataclass
class DiagnosticResult:
    diagnostic_id: str
    service_id: str
    root_cause: RootCause
    summary: str
    device_results: List[DeviceResult]
    start_time: datetime
    end_time: datetime
    status: str
    error: str = None
