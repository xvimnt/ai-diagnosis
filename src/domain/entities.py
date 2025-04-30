from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Device:
    id: str
    ip: str
    vendor: str
    hostname: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None

@dataclass
class Circuit:
    id: str
    devices: List[Device]
    status: Optional[str] = None
    last_modified: Optional[datetime] = None

@dataclass
class Service:
    id: str
    circuit_id: str
    customer_id: str
    service_type: str
    status: str
    created_at: datetime
    last_modified: datetime
