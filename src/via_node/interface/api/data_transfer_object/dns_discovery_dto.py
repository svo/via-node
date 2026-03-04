from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class DnsDiscoveryApiRequestDataTransferObject(BaseModel):
    domain_name: str = Field(..., description="Domain name to discover DNS records for")
    record_types: Optional[List[str]] = Field(
        None, description="List of DNS record types to query (e.g., A, AAAA, CNAME, MX). Defaults to A, AAAA, CNAME, MX"
    )


class DnsDiscoveryResultApiResponseDataTransferObject(BaseModel):
    domain_name: str = Field(..., description="Domain name queried")
    record_type: str = Field(..., description="DNS record type")
    values: List[str] = Field(..., description="Discovered DNS values")
    ttl: Optional[int] = Field(None, description="Time to live in seconds")
    discovered_at: datetime = Field(..., description="Discovery timestamp")

    @classmethod
    def from_domain_model(cls, domain_model: Any) -> DnsDiscoveryResultApiResponseDataTransferObject:
        return cls(
            domain_name=domain_model.domain_name,
            record_type=domain_model.record_type.value,
            values=domain_model.values,
            ttl=domain_model.ttl,
            discovered_at=domain_model.discovered_at,
        )


class DnsDiscoveryApiResponseDataTransferObject(BaseModel):
    discoveries: List[DnsDiscoveryResultApiResponseDataTransferObject] = Field(
        ..., description="List of DNS record discoveries"
    )
