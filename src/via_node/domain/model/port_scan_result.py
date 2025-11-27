from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator


class PortState(Enum):
    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    UNFILTERED = "unfiltered"


class PortScanResult(BaseModel):
    target_ip: str
    port_number: int
    protocol: str
    state: PortState
    service_name: Optional[str] = None
    service_version: Optional[str] = None
    scanned_at: datetime

    @field_validator("target_ip")
    @classmethod
    def validate_target_ip(cls, target_ip: str) -> str:
        if not target_ip or len(target_ip.strip()) == 0:
            raise ValueError("Target IP cannot be empty")
        return target_ip.strip()

    @field_validator("port_number")
    @classmethod
    def validate_port_number(cls, port_number: int) -> int:
        if port_number < 1 or port_number > 65535:
            raise ValueError("Port number must be between 1 and 65535")
        return port_number

    @field_validator("protocol")
    @classmethod
    def validate_protocol(cls, protocol: str) -> str:
        protocol_lower = protocol.strip().lower()
        if protocol_lower not in ["tcp", "udp"]:
            raise ValueError("Protocol must be 'tcp' or 'udp'")
        return protocol_lower
