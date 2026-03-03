from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class HostApiRequestDataTransferObject(BaseModel):
    ip_address: str = Field(..., description="IPv4 or IPv6 address")
    hostname: str = Field(..., description="Hostname or FQDN")
    os_type: str = Field(..., description="Operating system type (e.g., Linux, Windows)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata dictionary")

    @classmethod
    def from_domain_model(cls, domain_model: Any) -> HostApiRequestDataTransferObject:  # pragma: no cover
        return cls(
            ip_address=domain_model.ip_address,
            hostname=domain_model.hostname,
            os_type=domain_model.os_type,
            metadata=domain_model.metadata,
        )


class HostApiResponseDataTransferObject(BaseModel):
    ip_address: str = Field(..., description="IPv4 or IPv6 address")
    hostname: str = Field(..., description="Hostname or FQDN")
    os_type: str = Field(..., description="Operating system type")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata dictionary")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @classmethod
    def from_domain_model(cls, domain_model: Any) -> HostApiResponseDataTransferObject:  # pragma: no cover
        return cls(
            ip_address=domain_model.ip_address,
            hostname=domain_model.hostname,
            os_type=domain_model.os_type,
            metadata=domain_model.metadata,
            created_at=domain_model.created_at,
            updated_at=domain_model.updated_at,
        )
