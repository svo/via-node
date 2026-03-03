from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field


class DomainPortEdgeApiRequestDataTransferObject(BaseModel):
    domain_name: str = Field(..., description="Domain name")
    port_number: int = Field(..., ge=1, le=65535, description="Port number (1-65535)")
    protocol: str = Field("TCP", description="Protocol (TCP or UDP)")


class DnsResolvesToHostEdgeApiRequestDataTransferObject(BaseModel):
    domain_name: str = Field(..., description="Domain name")
    ip_address: str = Field(..., description="IP address of the host")


class EdgeApiResponseDataTransferObject(BaseModel):
    source_id: str = Field(..., description="Source vertex ID")
    target_id: str = Field(..., description="Target vertex ID")
    edge_type: str = Field(..., description="Edge type")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Edge metadata")
    created_at: datetime = Field(..., description="Creation timestamp")

    @classmethod
    def from_domain_model(cls, domain_model: Any) -> EdgeApiResponseDataTransferObject:  # pragma: no cover
        return cls(
            source_id=domain_model.source_id,
            target_id=domain_model.target_id,
            edge_type=domain_model.edge_type,
            metadata=domain_model.metadata,
            created_at=domain_model.created_at,
        )
