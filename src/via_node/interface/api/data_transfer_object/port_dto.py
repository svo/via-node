from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class PortApiRequestDataTransferObject(BaseModel):
    port_number: int = Field(..., ge=1, le=65535, description="Port number (1-65535)")
    protocol: str = Field(..., description="Protocol (TCP or UDP)")
    service_name: Optional[str] = Field(None, description="Optional service name")

    @classmethod
    def from_domain_model(cls, domain_model: Any) -> PortApiRequestDataTransferObject:  # pragma: no cover
        return cls(
            port_number=domain_model.port_number,
            protocol=domain_model.protocol,
            service_name=domain_model.service_name,
        )


class PortApiResponseDataTransferObject(BaseModel):
    port_number: int = Field(..., description="Port number")
    protocol: str = Field(..., description="Protocol (TCP or UDP)")
    service_name: Optional[str] = Field(None, description="Service name")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @classmethod
    def from_domain_model(cls, domain_model: Any) -> PortApiResponseDataTransferObject:  # pragma: no cover
        return cls(
            port_number=domain_model.port_number,
            protocol=domain_model.protocol,
            service_name=domain_model.service_name,
            created_at=domain_model.created_at,
            updated_at=domain_model.updated_at,
        )
