from __future__ import annotations

from datetime import datetime
from typing import Any, List

from pydantic import BaseModel, Field


class DnsRecordApiRequestDataTransferObject(BaseModel):
    domain_name: str = Field(..., description="Domain name or FQDN")
    record_type: str = Field(..., description="DNS record type (A, AAAA, CNAME, MX, NS, TXT, SOA, PTR)")
    ip_addresses: List[str] = Field(default_factory=list, description="List of IP addresses")

    @classmethod
    def from_domain_model(cls, domain_model: Any) -> DnsRecordApiRequestDataTransferObject:  # pragma: no cover
        return cls(
            domain_name=domain_model.domain_name,
            record_type=domain_model.record_type,
            ip_addresses=domain_model.ip_addresses,
        )


class DnsRecordApiResponseDataTransferObject(BaseModel):
    domain_name: str = Field(..., description="Domain name or FQDN")
    record_type: str = Field(..., description="DNS record type")
    ip_addresses: List[str] = Field(..., description="List of IP addresses")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @classmethod
    def from_domain_model(cls, domain_model: Any) -> DnsRecordApiResponseDataTransferObject:  # pragma: no cover
        return cls(
            domain_name=domain_model.domain_name,
            record_type=domain_model.record_type,
            ip_addresses=domain_model.ip_addresses,
            created_at=domain_model.created_at,
            updated_at=domain_model.updated_at,
        )
