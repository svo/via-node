from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class PortScanApiRequestDataTransferObject(BaseModel):
    target: str = Field(..., description="Target IP address or hostname to scan")
    ports: str = Field("1-1000", description="Port range or comma-separated list (e.g., '1-1000' or '22,80,443')")


class PortScanResultApiResponseDataTransferObject(BaseModel):
    target_ip: str = Field(..., description="Target IP address")
    port_number: int = Field(..., description="Port number")
    protocol: str = Field(..., description="Protocol (tcp or udp)")
    state: str = Field(..., description="Port state (open, closed, filtered, unfiltered)")
    service_name: Optional[str] = Field(None, description="Detected service name")
    service_version: Optional[str] = Field(None, description="Detected service version")
    scanned_at: datetime = Field(..., description="Scan timestamp")

    @classmethod
    def from_domain_model(cls, domain_model: Any) -> PortScanResultApiResponseDataTransferObject:
        return cls(
            target_ip=domain_model.target_ip,
            port_number=domain_model.port_number,
            protocol=domain_model.protocol,
            state=domain_model.state.value,
            service_name=domain_model.service_name,
            service_version=domain_model.service_version,
            scanned_at=domain_model.scanned_at,
        )


class PortScanApiResponseDataTransferObject(BaseModel):
    results: List[PortScanResultApiResponseDataTransferObject] = Field(..., description="List of port scan results")
